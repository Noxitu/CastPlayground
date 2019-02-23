import ssdp
import uuid
import logging
from udp import create_ip4
from utils import daemon, wait
from my_http.parse import parse_request
from traceback import print_exc

_log = logging.getLogger(__name__)

def _expect(lhs, rhs, error_msg):
    if lhs != rhs:
        _log.debug('{} != {}... Raising exception: {}'.format(lhs, rhs, error_msg))
        raise Exception(error_msg)

def _expect_ssdp_search(req):
    _expect(req.method, 'M-SEARCH', 'Not M-SEARCH request')
    _expect(req.url, '*', 'Wrong url')
    _expect(req.header['man'], b'"ssdp:discover"', 'Not ssdp:discover')


class LoggingDevice:
    def recieve(self, buffer, addr):
        req = parse_request(buffer)
        _expect_ssdp_search(req)

        _log.info('{} is searching for "{}"'.format(addr, req.header['st']))
        

class Device:
    def __init__(self):
        self.__uuid = 'uuid:'+str(uuid.uuid4()).lower()
        self.__urns = {ssdp.URN.UPNP_ROOT_DEVICE, self.__uuid, ssdp.URN.DIAL_DEVICE, ssdp.URN.DIAL_SERVICE}

    def do_notify(self, data):
        raise NotImplementedError()

    def do_answer(self, buffer, addr):
        raise NotImplementedError()

    def recieve(self, buffer, addr):
        req = parse_request(buffer)
        _expect_ssdp_search(req)
        
        st = req.header['st'].decode('ascii')
        for urn in self.__urns:
            if st in {ssdp.URN.SSDP_ALL, urn}:
                if urn.startswith('uuid:'):
                    usn = urn
                else:
                    usn = '{}::{}'.format(self.__uuid, urn)

                _log.info('Responding to {} with USN: {}'.format(addr, usn))

                response = b'\r\n'.join((
                    b'HTTP/1.1 200 OK',
                    b'CACHE-CONTROL: max-age=1800',
                    b'EXT:',
                    b'LOCATION: http://192.168.1.2:8000/dial',
                    b'SERVER: Confidential/1.0, UPnP/1.0, Confidential/1.0',
                    b'ST: ' + req.header['st'],
                    b''
                    b'\r\n'))

                self.do_answer(response, addr)



def main():
    logging.basicConfig(level=logging.INFO)

    multicast_socket = create_ip4(host      = '',
                                  port      = ssdp.UDP_PORT,
                                  multicast = ssdp.IP_ADDRESS)

    unicast_socket = create_ip4()

    devices = []
    devices.append(LoggingDevice())

    dial_device = Device()
    dial_device.do_answer = lambda buffer, addr: unicast_socket.sendto(buffer, addr)
    devices.append(dial_device)

    @daemon
    def listen():
        while True:
            buffer, addr = multicast_socket.recvfrom(10240)
            for device in devices:
                try:
                    device.recieve(buffer, addr)
                except:
                    pass

    listen()
    wait()    

if __name__ == '__main__':
    main()

