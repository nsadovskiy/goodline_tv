import os
from html import unescape
from xml.etree import ElementTree as Xml
from urllib.parse import urlsplit, urlunsplit, quote


def parse_playlist(text, log):
    log.info('Start parsing playlist')

    log.debug(f'Playlist data:\n{text}')

    result = dict()

    def escape_url(url):
        p = urlsplit(url)
        return urlunsplit((p.scheme, p.netloc, quote(unescape(p.path)), p.query, p.fragment))

    log.debug('Parsing XML...')
    root = Xml.fromstring(text)

    log.debug('XML successfully parsed. Processing tracks...')
    for track in root.iter('{http://xspf.org/ns/0/}track'):

        name = track.find('{http://xspf.org/ns/0/}title').text.strip()
        stream_url = track.find('{http://xspf.org/ns/0/}location').text
        epg_id = track.find('{http://xspf.org/ns/0/}psfile').text

        image = track.find('{http://xspf.org/ns/0/}image').text
        icon_url = escape_url(image)

        icon_name = os.path.basename(urlsplit(image).path)

        log.debug(f'[{epg_id}] "{name}" stream: "{stream_url}", icon: "{icon_name}" <{icon_url}>')

        result[epg_id] = dict(name=name, stream_url=stream_url, epg_id=epg_id, icon_url=icon_url, icon_name=icon_name)

    log.info('Playlist successfully parsed')

    return result
