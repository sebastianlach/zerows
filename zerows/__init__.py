# -*- coding: utf-8 -*-
"""
usage: zerows [-h] [--xsub-port [XSUB_PORT]] [--xpub-port [XPUB_PORT]]
                 [--debug]
                 [host [host ...]]
"""
__author__ = "Sebastian Łach"
__copyright__ = "Copyright 2015, Sebastian Łach"
__credits__ = ["Sebastian Łach", ]
__license__ = "MIT"
__version__ = "1.0"
__maintainer__ = "Sebastian Łach"
__email__ = "root@slach.eu"


import logging
import socket

import zmq
from zmq.eventloop import ioloop, zmqstream
ioloop.install() 

import tornado
import tornado.web
import tornado.websocket
from tornado.web import Application



FORMAT = '%(message)s'
logging.basicConfig(format=FORMAT, level=logging.DEBUG)
logger = logging.getLogger()


class EchoWebSocket(tornado.websocket.WebSocketHandler):

    clients = set() 

    def open(self):
        self.clients.add(self)

    def on_message(self, incoming):
        self.write_message(str(len(incoming)))

    def on_broadcast(self, outgoing):
        self.write_message(outgoing)
        logger.error(outgoing)

    def on_close(self):
        self.clients.remove(self)

    def check_origin(self, origin):
        return True


def dispatch(message):
    for client in EchoWebSocket.clients:
        client.on_broadcast(message[0])


handlers = [
    (r'/', EchoWebSocket)
]


def main():
    """Main entry-point"""
    ip = socket.gethostbyname(socket.gethostname())
    application = Application(handlers, port=80)
    context = zmq.Context()
    iol = ioloop.IOLoop.current()
    socket = context.socket(zmq.SUB)
    socket.bind('tcp://{}:5000'.format(ip))
    socket.setsockopt_string(zmq.SUBSCRIBE, u'')
    stream = zmqstream.ZMQStream(socket, iol)
    stream.on_recv(dispatch)
    application.listen(80)
    iol.start()

if __name__ == '__main__':
    main()

