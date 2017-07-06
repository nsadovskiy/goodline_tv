#!/usr/bin/env python3

from shutil import copy
from html import unescape
from struct import unpack
from sys import argv, exit
from urllib import request
from zipfile import ZipFile
from os.path import join, split
from xml.sax.saxutils import escape
from re import compile, DOTALL, search
from tempfile import TemporaryDirectory
from datetime import datetime, timedelta
from urllib.parse import quote, urlsplit, urlunsplit


EPG_URL = 'http://bolshoe.tv/tv.zip'
PLAYLIST_URL = 'http://212.75.210.50/playlist'


XMLTV_FILENAME = 'teleguide.xmltv'

XMLTV_HEADER = '''<?xml version="1.0" encoding="utf-8" ?>
<!DOCTYPE tv SYSTEM "http://www.teleguide.info/xmltv.dtd">
<tv generator-info-name="Preved" generator-info-url="http://www.medved.info/">
'''

XMLTV_CHANNEL = '''\t<channel id="{epg}">
\t\t<display-name>{channel}</display-name>
\t\t<icon>{icon}</icon>
\t</channel>
'''

XMLTV_PROGRAMME = '''\t<programme start="{start:%Y%m%d%H%M%S} +0700" stop="{stop:%Y%m%d%H%M%S} +0700" channel="{epg}">
\t\t<title lang="ru">{escaped_program}</title>
\t</programme>
'''

XMLTV_FOOTER = '</tv>\n'


M3U_FILENAME = 'playlist.m3u'

M3U_HEADER = '#EXTM3U\n'

M3U_ITEM = '#EXTINF:-1 tvg-name="{epg}", tvg-logo="{icon}", {channel}\n{url}\n'


def load_playlist():

    def get_tag_value(string, tag):
        return search(r'<{tag}>(.*?)</{tag}>'.format(tag=tag), string).group(1).strip()

    track_re = compile(r'<track>(.*?)</track>', flags=DOTALL)

    with request.urlopen(PLAYLIST_URL) as response:

        playlist = response.read().decode('utf8')

        for track in track_re.findall(playlist):
            icon = get_tag_value(track, 'image')
            p = urlsplit(icon)
            icon_url = urlunsplit((p.scheme, p.netloc, quote(unescape(p.path)), p.query, p.fragment))
            icon_name = split(p.path)[1]
            yield dict(
                url=get_tag_value(track, 'location'),
                channel=get_tag_value(track, 'title'),
                epg=get_tag_value(track, 'psfile'),
                zoom=get_tag_value(track, 'zoom'),
                icon=icon_name,
                icon_url=icon_url
            )


def load_epg(path, epg):

    JTV_HDR = 'JTV 3.x TV Program Data\x0a\x0a\x0a'

    pdt_filename = join(path, epg + '.pdt')
    ndx_filename = join(path, epg + '.ndx')

    with open(ndx_filename, 'rb') as ndx_file, open(pdt_filename, 'rb') as pdt_file:

        hdr = pdt_file.read(26).decode('cp1251')
        if hdr != JTV_HDR:
            raise RuntimeError('File "%s" does not contain PDT valid header!' % pdt_filename)

        offs = len(JTV_HDR)
        tracks = dict()

        while True:
            track_len = pdt_file.read(2)
            if len(track_len) != 2:
                break
            track_len = unpack('H', track_len)[0]

            track = pdt_file.read(track_len)
            if len(track) != track_len:
                raise RuntimeError('Unexpected end of file while reading "%s"' % pdt_filename)

            tracks[offs] = track.decode('cp1251').strip()
            offs += track_len + 2

        num_entries = unpack('H', ndx_file.read(2))[0]
        programs = list()

        for i in range(0, num_entries):
            ndx_file.read(2)
            t = datetime(1601, 1, 1) + timedelta(seconds=int(unpack('Q', ndx_file.read(8))[0] / 10000000))
            o = unpack('H', ndx_file.read(2))[0]
            programs.append((o, t))

        for i in range(1, num_entries):
            if programs[i-1][0] in tracks:
                yield dict(program=tracks[programs[i-1][0]],
                           escaped_program=escape(tracks[programs[i-1][0]]),
                           start=programs[i-1][1],
                           stop=programs[i][1]
                           )


if __name__ == '__main__':

    if len(argv) != 2:
        exit(1)

    files = []

    with TemporaryDirectory() as tmp_dir:

        epg_archive, headers = request.urlretrieve(EPG_URL, join(tmp_dir, 'epg.zip'))

        with ZipFile(epg_archive) as zip_file:
            zip_file.extractall(tmp_dir)

        xmltv_path = join(tmp_dir, XMLTV_FILENAME)
        m3u_path = join(tmp_dir, M3U_FILENAME)

        with open(xmltv_path, 'w') as epg_file, open(m3u_path, 'w') as m3u_file:

            files.append(XMLTV_FILENAME)
            files.append(M3U_FILENAME)

            m3u_file.write(M3U_HEADER)
            epg_file.write(XMLTV_HEADER)

            for tv in load_playlist():

                request.urlretrieve(tv['icon_url'], join(tmp_dir, tv['icon']))
                files.append(tv['icon'])

                m3u_file.write(M3U_ITEM.format(**tv))
                epg_file.write(XMLTV_CHANNEL.format(**tv))

                for program in load_epg(tmp_dir, tv['epg']):
                    program.update(tv)
                    epg_file.write(XMLTV_PROGRAMME.format(**program))

            epg_file.write(XMLTV_FOOTER)

        for f in files:
            copy(join(tmp_dir, f), argv[1])
