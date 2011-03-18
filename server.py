
import sys

import tornado.ioloop

from thumbor.app import ThumborServiceApp


def main(port):
    application = ThumborServiceApp()
    application.listen(port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8888
    main(port)
