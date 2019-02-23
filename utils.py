from threading import Thread
from time import sleep

def daemon(call):
    def ret(*a, **kw):
        th = Thread(target=call, args=a, kwargs=kw)
        th.daemon = True
        th.start()
    return ret

def wait():
    while True: sleep(.5)