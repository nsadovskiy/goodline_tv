from xml.dom import minidom
from aiofiles import open as open_file
from xml.etree.ElementTree import Element, SubElement, tostring


class XmltvBuilder(object):

    def __init__(self, timezone='+0700'):

        self.timezone = timezone

        self.root = Element('tv')
        self.root.set('generator-info-name', 'Preved')
        self.root.set('generator-info-url', 'http://www.medved.info')

    def add_channel(self, epg_id, name, icon):

        channel = SubElement(self.root, 'channel', id=epg_id)

        name_element = SubElement(channel, 'display-name')
        name_element.text = name

        icon_element = SubElement(channel, 'icon')
        icon_element.text = icon

    def add_track(self, epg, time_begin, time_end, name):
        programme = SubElement(self.root, 'programme',
            start=f'{time_begin.strftime("%Y%m%d%H%M%S")} {self.timezone}',
            stop=f'{time_end.strftime("%Y%m%d%H%M%S")} {self.timezone}',
            channel=f'{epg}'
        )
        title = SubElement(programme, 'title', lang='ru')
        title.text = name

    async def save(self, path, pretty=False):
        async with open_file(path, mode='w') as f:
            await f.write(self.to_string(pretty))

    def to_string(self, pretty=False):
        return minidom.parseString(tostring(self.root)).toprettyxml(indent=' ') if pretty else tostring(self.root, encoding='unicode')
