#!/usr/bin/env python
# coding: utf-8

from shutil import rmtree
from struct import unpack
from zipfile import ZipFile
from urllib2 import urlopen
from os import mkdir, listdir
from tempfile import gettempdir
from xml.sax.saxutils import escape
from datetime import datetime, timedelta
from os.path import join, isfile, splitext
from xml.etree.ElementTree import parse as parse_xml


EPG_URL = 'http://bolshoe.tv/tv.zip'
PLAYLIST_URL = 'http://212.75.210.50/playlist'


def unzip_jtv(file_name, extract_path):

	# Faggoten function to decode file names for MAC and WIN zip-files
	def decode_name(name):
		try:
			return name.decode('utf-8')
		except:
			return name.decode('cp866')

	mkdir(extract_path)
	# Extract EPG
	with ZipFile(file_name) as z:
		for name in z.namelist():
			file_path = join(extract_path, decode_name(name))
			with open(file_path, 'w') as f:
				f.write(z.read(name))
	return extract_path


def process_jtv_directory(jtv_path):

	def list_ndx(path):
		for f in listdir(path):
			if isfile(join(jtv_path, f)) and splitext(f)[1].lower() == '.ndx':
				yield f

	def from_timestamp(timestamp):
		return datetime(1601, 1, 1) + timedelta(seconds = int(timestamp / 10000000))

	guides = dict()
	for ndx in list_ndx(jtv_path):
		guide = dict(name=splitext(ndx)[0])
		pdt = guide['name'] + '.pdt'
		with open(join(jtv_path, pdt), 'r') as pdt_file:
			hdr = pdt_file.read(26)
			broadcasts = dict()
			if hdr != 'JTV 3.x TV Program Data\x0a\x0a\x0a':
				print pdt, 'does not contain valid header!'
				continue
			key = 26
			while True:
				str_len = pdt_file.read(2)
				if str_len == '':
					break
				l = unpack('H', str_len)[0]
				track = pdt_file.read(l).decode('cp1251').strip() # .encode('utf-8')
				if track == '':
					break
				broadcasts[key] = track
				key += l + 2
			guide['broadcasts'] = broadcasts
			with open(join(jtv_path, ndx), 'r') as ndx_file:
				num_entries = unpack('H', ndx_file.read(2))[0]
				entries = list()
				for i in range(0, num_entries):
					ndx_file.read(2)
					time = from_timestamp(unpack('Q', ndx_file.read(8))[0])
					offset = unpack('H', ndx_file.read(2))[0]
					entries.append((time, offset))
				guide['entries'] = entries
		guides[guide['name']] = guide
	return guides


def read_playlist(file):
	result = []
	root = parse_xml(file).getroot()
	for track in root.findall('{http://xspf.org/ns/0/}trackList/{http://xspf.org/ns/0/}track'):
		url = track.find('{http://xspf.org/ns/0/}location').text.strip()
		title = track.find('{http://xspf.org/ns/0/}title').text.strip()
		epg_id = track.find('{http://xspf.org/ns/0/}psfile').text.strip()
		zoom = track.find('{http://xspf.org/ns/0/}zoom').text.strip()
		image = track.find('{http://xspf.org/ns/0/}image').text.strip()
		result.append(dict(url=url, title=title, epg_id=epg_id, zoom=zoom, image=image))
	return result

def download_file(url, path):
	response = urlopen(url)
	code = response.getcode()
	if code != 200:
		raise IOError('Downloading "%s" was failed with code' % (url, code))
	file_name = response.geturl().split('/')[-1]
	out_path = join(path, file_name)
	with open(out_path, 'wb') as out_file:
		out_file.write(response.read())
	return out_path

def get_temp_dir():
	path = join(gettempdir(), 'goodline')
	try:
		rmtree(path)
	except OSError:
		pass
	mkdir(path)
	return path

def create_playlist(playlist, file):
	with open(file, 'w') as f:
		f.write('#EXTM3U\n')
		for track in playlist:
			icon_name = track['image'].split('/')[-1]
			track = '#EXTINF:-1 tvg-name="%s", tvg-logo="%s", %s\n%s\n' % (track['epg_id'], icon_name, track['title'], track['url'])
			f.write(track.encode('utf-8'))

def create_epg(playlist, epg, file):
	with open(file, 'w') as f:
		f.write('<?xml version="1.0" encoding="utf-8" ?>\n')
		f.write('<!DOCTYPE tv SYSTEM "http://www.teleguide.info/xmltv.dtd">\n')
		f.write('<tv generator-info-name="Preved" generator-info-url="http://www.medved.info/">\n')

		for channel in playlist:
			epg_id = channel['epg_id']
			icon = channel['image']
			channel_title = channel['title']
			if epg_id not in epg:
				print 'WARNING! EPG not found for %s' % channel['title']
				continue
			f.write('\t<channel id="%s">\n' % epg_id)
			f.write(('\t\t<display-name>%s</display-name>\n' % escape(channel_title)).encode('utf-8'))
			icon_name = icon.split('/')[-1]
			f.write(('\t\t<icon>%s</icon>\n' % escape(icon_name)).encode('utf-8'))
			f.write('\t</channel>\n')
			guide = epg[epg_id]
			for i in range(0, len(guide['entries']) - 2):
				time_begin = guide['entries'][i][0]
				time_end = guide['entries'][i + 1][0]
				title = guide['broadcasts'][guide['entries'][i][1]]
				f.write(('\t<programme start="%s +0700" stop="%s +0700" channel="%s">\n' % (time_begin.strftime('%Y%m%d%H%M%S'), time_end.strftime('%Y%m%d%H%M%S'), epg_id)).encode('utf-8'))
				f.write((u'\t\t<title lang="ru">%s</title>\n' % escape(title.strip(' \t\n\r'))).encode('utf-8'))
				f.write(('\t</programme>\n').encode('utf-8'))
		f.write('</tv>\n')

if __name__ == '__main__':
	temp_dir = get_temp_dir()
	playlist_file = download_file(PLAYLIST_URL, temp_dir)
	epg_file = download_file(EPG_URL, temp_dir)
	playlist = read_playlist(playlist_file)
	create_playlist(playlist, join(temp_dir, 'playlist.m3u'))
	jtv_path = unzip_jtv(epg_file, join(temp_dir, 'jtv'))
	epg = process_jtv_directory(jtv_path)
	create_epg(playlist, epg, join(temp_dir, 'teleguide.xmltv'))
