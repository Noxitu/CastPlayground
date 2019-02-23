import socket
import struct

def create_ip4(host='', port=0, multicast=None):

    sock = socket.socket(family = socket.AF_INET, 
                         type   = socket.SOCK_DGRAM, 
                         proto  = socket.IPPROTO_UDP)

    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    sock.bind((host, port))

    if multicast:
        mreq = struct.pack("4sl", socket.inet_aton(multicast), socket.INADDR_ANY)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    return sock