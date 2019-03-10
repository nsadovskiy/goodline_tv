from zipfile import ZipFile
from struct import unpack_from
from datetime import datetime, timedelta


class _Names(object):
    JTV_HEADER = 'JTV 3.x TV Program Data\x0a\x0a\x0a'

    def __init__(self, buffer, encoding='cp1251'):
        self.__encoding = encoding
        self.__buffer = buffer
        self.__names = dict()

        self.__ensure_signature()

        self.__load_names()

    def get_name(self, index):
        return self.__names.get(index, '-')

    def __ensure_signature(self):
        if len(self.__buffer) < len(_Names.JTV_HEADER) or self.__buffer[:len(_Names.JTV_HEADER)].decode(self.__encoding, errors='ignore') != _Names.JTV_HEADER:
            raise RuntimeError('File does not have a valid JTV signature')

    def __load_names(self):

        offset = len(_Names.JTV_HEADER)

        while offset + 2 < len(self.__buffer):

            track_len = unpack_from('<H', self.__buffer, offset)[0]
            offset += 2

            if offset + track_len > len(self.__buffer):
                raise RuntimeError('Unexpected end of file')

            try:
                track_name = self.__buffer[offset:offset + track_len].decode(self.__encoding)
            except UnicodeError:
                raise RuntimeError('Error decoding track name')

            self.__names[offset - 2] = track_name

            offset += track_len


class _Tracks(object):
    NDX_RECORD_LEN = 12

    def __init__(self, buffer, encoding='cp1251'):
        self.__buffer = buffer
        self.__num_tracks = self.__read_num_tracks()
        self.__ensure_length()

    def tracks(self):
        for i in range(self.__num_tracks):
            program = unpack_from('<HQH', self.__buffer, 2 + i * _Tracks.NDX_RECORD_LEN)
            yield _Tracks.parse_time(program[1]), program[2]

    @staticmethod
    def parse_time(time):
        return datetime(1601, 1, 1) + timedelta(microseconds=int(time / 10))

    def __read_num_tracks(self):
        if len(self.__buffer) < 2:
            raise RuntimeError('Unexpected end of file')

        return unpack_from('H', self.__buffer, 0)[0]

    def __ensure_length(self):
        if len(self.__buffer) != 2 + _Tracks.NDX_RECORD_LEN * self.__num_tracks:
            raise RuntimeError('Unexpected length')


class Channel(object):

    def __init__(self, channel_id, tracks, names):
        self.__channel_id = channel_id
        self.__tracks = tracks
        self.__names = names

    @property
    def track_id(self):
        return self.__channel_id

    @property
    def tracks(self):
        for time, index in self.__tracks.tracks():
            yield time, self.__names.get_name(index)


class JtvFile(object):

    def __init__(self, jtv_path, log, encoding='cp1251'):
        self.__log = log
        self.__encoding = encoding
        self.__archive = ZipFile(jtv_path)

    @property
    def channels(self):

        for pdt_filename in [f for f in self.__archive.namelist() if f.endswith('.pdt')]:

            channel_id = pdt_filename[:-4]
            ndx_filename = f'{channel_id}.ndx'

            names = _Names(self.__archive.read(pdt_filename), self.__encoding)
            tracks = _Tracks(self.__archive.read(ndx_filename), self.__encoding)

            yield Channel(channel_id, tracks, names)
