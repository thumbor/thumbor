
import sys
import signal

import tornado.ioloop
from tornado.httpserver import HTTPServer

from thumbor.app import ThumborServiceApp

port = 8888
server = None

def __kill_server():
    print 'stopping server...'
    server.stop()
    ioloop = tornado.ioloop.IOLoop.instance()
    ioloop.stop()
    ioloop._stopped = False

def handle_sigterm(signum, frame):
    __kill_server()
    print "server stopped"

def handle_sighup(signum, frame):
    __kill_server()

    print 'restarting server...'
    main()

def main():
    global server

    print 'starting server...'

    if not signal.getsignal(signal.SIGHUP):
        signal.signal(signal.SIGHUP, handle_sighup)
    if not signal.getsignal(signal.SIGTERM):
        signal.signal(signal.SIGTERM, handle_sigterm)

    application = ThumborServiceApp()

    server = HTTPServer(application)
    server.bind(port, '0.0.0.0')
    server.start(0)

    print 'server started'
    tornado.ioloop.IOLoop.instance().start(0)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    main()
