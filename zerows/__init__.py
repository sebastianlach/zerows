#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
usage: zerows [-h]
"""

__author__ = "Sebastian Łach"
__copyright__ = "Copyright 2015, Sebastian Łach"
__credits__ = ["Sebastian Łach", ]
__license__ = "MIT"
__version__ = "1.0"
__maintainer__ = "Sebastian Łach"
__email__ = "root@slach.eu"


from json import loads

from zmq import Context as ZMQContext, REQ
from zmq.eventloop.zmqstream import ZMQStream
from zmq.eventloop.ioloop import install as zmq_ioloop_install
zmq_ioloop_install()

import tornado
import tornado.web
import tornado.websocket
from tornado.log import app_log
from tornado.options import define, parse_command_line, options
from tornado.web import Application
from tornado.ioloop import IOLoop


# define application options
define('port', type=int, default=8080, help='application port number')
define('router', type=str, default='tcp://localhost:5559', help='router url')


ERROR_INVALID_REQUEST = b'{"error": "invalid request"}'


def load_message(message):
    try:
        return loads(message)
    except ValueError as e:
        app_log.debug(e)
        return None


class ZeroMQHandler(tornado.websocket.WebSocketHandler):

    def __init__(self, *args, **kwargs):
        super(ZeroMQHandler, self).__init__(*args, **kwargs)
        self.socket = None
        self.stream = None

    def open(self):
        settings = self.application.settings
        self.socket = settings['zeromq']['context'].socket(REQ)
        self.socket.connect(settings['zeromq']['url'])
        self.stream = ZMQStream(self.socket, settings['ioloop'])
        self.stream.on_recv(self.on_dispatch)

    def on_message(self, message):
        request = load_message(message)
        if request:
            data = message.encode('utf8')
            self.stream.send(data)
        else:
            self.write_message(ERROR_INVALID_REQUEST)

    def on_dispatch(self, messages):
        for message in messages:
            data = message.encode('utf8')
            self.write_message(data)

    def on_close(self):
        self.stream.close()
        self.socket.close()

    def check_origin(self, origin):
        return True

    def data_received(self, chunk):
        pass


def main():
    """Main entry-point"""
    parse_command_line()
    application = Application(
        [
            (r'/', ZeroMQHandler),
        ],
        ioloop=IOLoop.current(),
        zeromq=dict(
            context=ZMQContext(),
            url=options.router,
        )
    )
    app_log.info(application.settings)
    application.listen(options.port)
    application.settings['ioloop'].start()


if __name__ == '__main__':
    main()
