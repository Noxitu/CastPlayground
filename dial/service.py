import http.server

class Handler(http.server.BaseHTTPRequestHandler):
    pass

def main():
    addr = ('', 8000)
    httpd = http.server.HTTPServer(addr, Handler)
    httpd.serve_forever()

if __name__ == '__main__':
    main()
