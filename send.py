from udp import create_ip4

s = create_ip4()

s.sendto(b'buffer', ('192.168.1.2', 55983))