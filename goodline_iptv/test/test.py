import logging
import unittest
from io import BytesIO
from datetime import datetime
from goodline_iptv.jtvfile import JtvFile
from goodline_iptv.xmltv import XmltvBuilder
from goodline_iptv.test.jtv_data import TV_ZIP


logging.basicConfig(
    handlers=[
        logging.NullHandler()
    ]
)

log = logging.getLogger()


class TestJtv(unittest.TestCase):

    def setUp(self):
        self.channels = list(JtvFile(BytesIO(TV_ZIP), log).channels)

    def test_channelCount(self):
        self.assertEqual(len(self.channels), 1)

    def test_channelId(self):
        self.assertEqual(self.channels[0].track_id, '0')

    def test_tracks(self):
        tracks = list(self.channels[0].tracks)

        self.assertEqual(len(tracks), 166)

        self.assertEqual(tracks[0][0], datetime(2019, 3, 4, 5, 0))
        self.assertEqual(tracks[0][1], 'Телеканал "Доброе утро"')

        self.assertEqual(tracks[165][0], datetime(2019, 3, 11, 4, 5))
        self.assertEqual(tracks[165][1], 'Давай поженимся! (16+)')


class TestXmltv(unittest.TestCase):

    def setUp(self):
        self.xml = XmltvBuilder()

        self.xml.add_channel('0', '1 канал, канает и будет канать', '1channel.png')

        self.xml.add_track('0', datetime(2019, 3, 4, 5, 0), datetime(2019, 3, 11, 5, 15), 'Утренняя зарядка воды с Аланом Чумаком')
        self.xml.add_track('0', datetime(2019, 3, 4, 5, 20), datetime(2019, 3, 11, 6, 20), 'Чушь с Владимиром Познером')
        self.xml.add_track('0', datetime(2019, 3, 4, 6, 30), datetime(2019, 3, 11, 7, 15), 'Православный приговор')
        self.xml.add_track('0', datetime(2019, 3, 4, 7, 20), datetime(2019, 3, 11, 23, 0), 'Очередное Ток-шоу "Что там у хохлов"')

    def test_buildPretty(self):
        result = ('<?xml version="1.0" ?>\n'
                  '<tv generator-info-name="Preved" generator-info-url="http://www.medved.info">\n'
                  ' <channel id="0">\n'
                  '  <display-name>1 канал, канает и будет канать</display-name>\n'
                  '  <icon>1channel.png</icon>\n'
                  ' </channel>\n'
                  ' <programme channel="0" start="20190304050000 +0700" stop="20190311051500 +0700">\n'
                  '  <title lang="ru">Утренняя зарядка воды с Аланом Чумаком</title>\n'
                  ' </programme>\n'
                  ' <programme channel="0" start="20190304052000 +0700" stop="20190311062000 +0700">\n'
                  '  <title lang="ru">Чушь с Владимиром Познером</title>\n'
                  ' </programme>\n'
                  ' <programme channel="0" start="20190304063000 +0700" stop="20190311071500 +0700">\n'
                  '  <title lang="ru">Православный приговор</title>\n'
                  ' </programme>\n'
                  ' <programme channel="0" start="20190304072000 +0700" stop="20190311230000 +0700">\n'
                  '  <title lang="ru">Очередное Ток-шоу &quot;Что там у хохлов&quot;</title>\n'
                  ' </programme>\n'
                  '</tv>\n')
        self.assertEqual(self.xml.to_string(True), result)

    def test_build(self):
        result = '<tv generator-info-name="Preved" generator-info-url="http://www.medved.info"><channel id="0"><display-name>1 канал, канает и будет канать</display-name><icon>1channel.png</icon></channel><programme channel="0" start="20190304050000 +0700" stop="20190311051500 +0700"><title lang="ru">Утренняя зарядка воды с Аланом Чумаком</title></programme><programme channel="0" start="20190304052000 +0700" stop="20190311062000 +0700"><title lang="ru">Чушь с Владимиром Познером</title></programme><programme channel="0" start="20190304063000 +0700" stop="20190311071500 +0700"><title lang="ru">Православный приговор</title></programme><programme channel="0" start="20190304072000 +0700" stop="20190311230000 +0700"><title lang="ru">Очередное Ток-шоу "Что там у хохлов"</title></programme></tv>'
        self.assertEqual(self.xml.to_string(False), result)


if __name__ == '__main__':
    unittest.main(verbosity=2)
