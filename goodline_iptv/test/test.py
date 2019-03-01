import unittest
from goodline_iptv.jtvfile import parse_pdt, parse_ndx
from goodline_iptv.test.jtv_data import PDT_DATA, NDX_DATA, PDT_RESULT, NDX_RESULT


class TestJtv(unittest.TestCase):

    def test_parse_pdt(self):
        result = parse_pdt(PDT_DATA)
        self.assertDictEqual(result, PDT_RESULT)

    def test_parse_ndx(self):
        result = parse_ndx(NDX_DATA)
        self.assertListEqual(result, NDX_RESULT)


if __name__ == '__main__':
    unittest.main(verbosity=2)
