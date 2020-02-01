import signal
import sys
import time

import tornado.ioloop

from thumbor.utils import logger


def signal_handler(server, config, sig, _):
    io_loop = tornado.ioloop.IOLoop.instance()

    def stop_loop(now, deadline):
        if now < deadline and (
            io_loop._callbacks  # pylint: disable=protected-access
            or io_loop._timeouts  # pylint: disable=protected-access
        ):
            logger.debug("Waiting for next tick")
            now += 1
            io_loop.add_timeout(now, stop_loop, now, deadline)
        else:
            io_loop.stop()
            logger.debug("Shutdown finally")

    def stop_server(now, deadline):
        if now < deadline:
            logger.debug("Waiting for next tick")
            now += 1
            io_loop.add_timeout(now, stop_server, now, deadline)
        else:
            server.stop()
            logger.debug("Stopped http server.")
            logger.debug(
                "Will shutdown io in maximum %d seconds ...",
                config.MAX_WAIT_SECONDS_BEFORE_IO_SHUTDOWN,
            )
            now = time.time()
            stop_loop(now, now + config.MAX_WAIT_SECONDS_BEFORE_IO_SHUTDOWN)

    def shutdown():
        logger.debug(
            "Stopping http server (i.e. stopping accepting new requests) in %d seconds ...",
            config.MAX_WAIT_SECONDS_BEFORE_SERVER_SHUTDOWN,
        )
        now = time.time()
        stop_server(now, now + config.MAX_WAIT_SECONDS_BEFORE_SERVER_SHUTDOWN)

    logger.warning("Caught signal: %d. Shutting down server.", sig)
    io_loop.add_callback_from_signal(shutdown)


def setup_signal_handler(server, config):
    def server_sig_handler(sig, frame):
        signal_handler(server, config, sig, frame)
        if sig == signal.SIGINT:
            sys.stdout.write("\n")
            sys.stdout.write("-- thumbor closed by user interruption --\n")

    signal.signal(signal.SIGTERM, server_sig_handler)
    signal.signal(signal.SIGINT, server_sig_handler)
