from aiofiles import open as open_file


async def create_m3u(playlist, m3u_path, log):

    log.info('Start creating m3u playlist')

    async with open_file(m3u_path, 'w') as m3u_file:

        await m3u_file.write('#EXTM3U\n')

        for channel in playlist.values():
            await m3u_file.write(f'#EXTINF:-1 tvg-name="{channel["epg_id"]}", tvg-logo="{channel["icon_name"]}", {channel["name"]}\n{channel["stream_url"]}\n')

    log.info('Creating playlist complete')
