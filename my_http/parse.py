from typing import NamedTuple, Dict

class Request(NamedTuple):
    method: str
    url: str

    header: Dict[str, bytes]
    data: bytes


def parse_request(buffer: bytes) -> Request:
    header, data = buffer.split(b'\r\n\r\n', maxsplit=1)
    header = header.split(b'\r\n')

    method, url, version = header[0].split()

    if version != b'HTTP/1.1':
        raise Exception('Can only parse HTTP/1.1')

    def split(line):
        if b':' not in line:
            raise Exception('No ":" in header')

        key, value = line.split(b':', maxsplit=1)

        key = key.strip().lower().decode('ascii') # case insensitive
        value = value.strip()

        return key, value

    method = method.decode('ascii')
    url = url.decode('ascii')
    header = dict(map(split, header[1:]))

    return Request(method, url, header, data)
