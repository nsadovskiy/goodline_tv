import logging
import unittest
from io import BytesIO
from datetime import datetime
from goodline_iptv.jtvfile import JtvFile
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


if __name__ == '__main__':
    unittest.main(verbosity=2)
