import socket
import struct
import ssdp
from pprint import pprint
from traceback import print_exc
from utils import daemon, wait

class App:
    def __init__(self, service_type):
        self.service_type = service_type

        self.search_socket = socket.socket(family=socket.AF_INET, 
                                    type=socket.SOCK_DGRAM, 
                                    proto=socket.IPPROTO_UDP)

        self.search_socket.bind(('', 0))

        self.notify_socket = socket.socket(family=socket.AF_INET, 
                                    type=socket.SOCK_DGRAM, 
                                    proto=socket.IPPROTO_UDP)

        self.notify_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.notify_socket.bind(('0.0.0.0', ssdp.UDP_PORT))

        mreq = struct.pack("4sl", socket.inet_aton(ssdp.IP_ADDRESS), socket.INADDR_ANY)
        self.notify_socket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    def m_search(self):
        buffer = b'\r\n'.join((
               b'M-SEARCH * HTTP/1.1',
               b'Host: 239.255.255.250:1900',
               b'ST: ' + self.service_type,
               b'Man: "ssdp:discover"',
               b'MX: 3',
               b'\r\n'))

        self.search_socket.sendto(buffer, (ssdp.IP_ADDRESS, ssdp.UDP_PORT))

    @daemon
    def listen_for_answer(self, callback):
        def parse(addr, buffer):
            try:
                header = buffer.split(b'\r\n\r\n', maxsplit=1)[0]
                header = header.split(b'\r\n')

                if header[0].rstrip() != b'HTTP/1.1 200 OK': 
                    raise Exception('Not a HTTP response')

                def split(line):
                    key, value = line.split(b':', maxsplit=1)
                    return key.strip().lower().decode('ascii'), value.strip()

                header = dict(map(split, header[1:]))

                if header['st'] != self.service_type: 
                    raise Exception('Not this service')

                data = {
                    #'cache-control': header['cache-control'],
                    'location': header['location'],
                    'st': header['st'],
                    'usn': header['usn'],
                    'addr': addr
                }
                callback(data)
            except:
                print(buffer.decode('ascii'))
                print_exc()
                return

        while True:
            buffer, addr = self.search_socket.recvfrom(10240)
            print('Got data from', addr)
            parse(addr, buffer)

    @daemon
    def listen_for_notify(self, callback):
        def parse(addr, buffer):
            try:
                header = buffer.split(b'\r\n\r\n', maxsplit=1)[0]
                header = header.split(b'\r\n')

                if header[0].rstrip() != b'NOTIFY * HTTP/1.1': 
                    raise Exception('Not a NOTIFY * request')

                def split(line):
                    key, value = line.split(b':', maxsplit=1)
                    return key.strip().lower().decode('ascii'), value.strip()

                header = dict(map(split, header[1:]))

                if header['nt'] != self.service_type: 
                    raise Exception('Not this service')

                data = {
                    #'cache-control': header['cache-control'],
                    'location': header['location'],
                    'nt': header['nt'],
                    'usn': header['usn'],
                    'addr': addr
                }
                callback(data)
            except:
                #print(buffer.decode('ascii'))
                #print_exc()
                return

        while True:
            buffer, addr = self.notify_socket.recvfrom(10240)
            parse(addr, buffer)


    def listen(self, callback):
        self.listen_for_answer(callback)
        #self.listen_for_notify(callback)

#app = App(b'ssdp:all')
#app = App(b'upnp:rootdevice')
#app = App(b'urn:dial-multiscreen-org:device:dialreceiver:1')
#app = App(b'urn:dial-multiscreen-org:service:dialreceiver:1')
#app = App(b'urn:dial-multiscreen-org:service:dial:1')

def myprint(data):
    for key, value in data.items():
        if key == 'location': key = '\033[32mlocation\033[0m'
        if key == 'usn': key = '\033[31musn\033[0m'
        print(key, '=', value)
    print()

app.listen(myprint)
app.m_search()

wait()
