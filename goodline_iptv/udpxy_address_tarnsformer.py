
class UdpxyAddressTransformer(object):

    def __init__(self, address):
        self.__udpxy_addr = address

    def transform(self, channel):
        try:
            url = channel["stream_url"].split('@')[1]
            channel["stream_url"] = f'{self.__udpxy_addr}/udp/{url}'
        except IndexError:
            pass
        return channel
