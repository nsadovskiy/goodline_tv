import logging
from os import path, mkdir
from datetime import datetime
from urllib.parse import urlsplit
from aiofiles import open as open_file
from aiohttp import ClientSession as Http
from asyncio import get_event_loop, gather

from goodline_iptv.m3u import create_m3u
from goodline_iptv.jtvfile import JtvFile
from goodline_iptv.xmltv import XmltvBuilder
from goodline_iptv.goodline_playlist import parse_playlist
from goodline_iptv.udpxy_address_tarnsformer import UdpxyAddressTransformer


EPG_URL = 'http://bolshoe.tv/tv.zip'
PLAYLIST_URL = 'http://playlist.bolshoe.tv/playlist'
PLAYLIST_FILENAME = 'playlist.m3u'
EPG_FILENAME = 'teleguide.xmltv'


logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)-5.5s] [%(funcName)s] %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

log = logging.getLogger()


async def download_playlist(http, url):
    log.info(f'Start downloading playlist from "{url}"')

    async with http.get(url) as response:

        if response.status != 200:
            log.error(f'Error downloading playlist. Response code {response.status}')
            return None

        log.info('Playlist successfully downloaded')

        return parse_playlist(await response.text(), log)


async def download_epg(http, url, out_dir):
    log.info(f'Start downloading epg from "{url}"')

    async with http.get(url) as response:
        if response.status != 200:
            log.error(f'Error downloading EPG. Response code {response.status}')
            return None

        data = await response.read()

        epg_path = path.join(out_dir, path.basename(urlsplit(url).path))

        log.debug(f'EPG successfully downloaded. Saving to "{epg_path}"')

        async with open_file(epg_path, mode='w+b') as f:
            await f.write(data)
            log.debug(f'EPG saved to "{epg_path}"')

    log.info('EPG successfully downloaded')

    return epg_path


async def download_icons(http, playlist, out_dir):

    icons_dir = path.join(out_dir, 'icons')

    if not path.exists(icons_dir):
        mkdir(icons_dir)

    async def download_icon(http, url, file_name):
        log.debug(f'Start downloading icon "{url}"')
        async with http.get(url) as response:
            if response.status != 200:
                log.error(f'Error downloading icon "{url}". Response code: {response.status}')
                return None

            data = await response.read()

            log.debug(f'Icon "{url}" successfully downloaded. Saving...')

            icon_path = path.join(icons_dir, file_name)
            async with open_file(icon_path, mode='w+b') as f:
                await f.write(data)

            log.debug(f'Icon "{url}" successfully saved to "{icon_path}"')

    log.info('Start downloading icons')

    await gather(*[download_icon(http, track['icon_url'], track['icon_name']) for track in playlist.values()])

    log.info('Icons downloading finished')


async def create_xmltv(out_dir, epg_path, playlist, encoding, timezone, pretty_xmltv=False):

    xmltv_builder = XmltvBuilder(timezone)

    for channel in JtvFile(epg_path, log, encoding).channels:

        if channel.track_id not in playlist:
            log.warning(f'{channel.track_id} not found in channels playlist. EPG ignored.')
            continue

        xmltv_builder.add_channel(
            channel.track_id,
            playlist[channel.track_id]['name'],
            playlist[channel.track_id]['icon_name']
        )

        prev_time = prev_name = None

        for time, name in channel.tracks:
            if prev_time:
                xmltv_builder.add_track(channel.track_id, prev_time, time, prev_name)
            prev_time, prev_name = time, name

    await xmltv_builder.save(path.join(out_dir, EPG_FILENAME), pretty_xmltv)


async def main(out_dir, encoding, timezone, pretty_xmltv, udpxy):
    time_begin = datetime.now()

    log.info("Let's do it :)")

    if not path.exists(out_dir):
        log.debug(f'Directory {out_dir} does not exist. Creating.')
        mkdir(out_dir)

    async with Http() as http:

        playlist, epg_path = await gather(
            download_playlist(http, PLAYLIST_URL),
            download_epg(http, EPG_URL, out_dir)
        )

        await download_icons(http, playlist, out_dir)

        transformer = UdpxyAddressTransformer(udpxy) if udpxy else None

        await gather(
            create_xmltv(out_dir, epg_path, playlist, encoding, timezone, pretty_xmltv),
            create_m3u(playlist, path.join(out_dir, PLAYLIST_FILENAME), transformer, log)
        )

    log.info(f'Finished due {datetime.now() - time_begin}')


def do_import(verbosity, out_dir, encoding, timezone, pretty_xmltv=False, udpxy=None):

    log.setLevel((4 - verbosity) * 10)

    get_event_loop().run_until_complete(main(out_dir, encoding, timezone, pretty_xmltv, udpxy))
