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


import os

import zmq
from zmq.eventloop import ioloop, zmqstream
ioloop.install() 

import tornado
import tornado.web
import tornado.websocket
from tornado.web import Application

import logging 
FORMAT = '%(message)s'
logging.basicConfig(format=FORMAT,level=logging.DEBUG)
logger = logging.getLogger()


class EchoWebSocket(tornado.websocket.WebSocketHandler):

    clients = set() 

    def open(self):
        self.clients.add(self)

    def on_message(self, incoming):
        self.write_message(str(len(incoming)))

    def on_broadcast(self, outgoing):
        import json
        x = str(outgoing)[2:-1]
        d = json.loads(x)
        o = json.dumps(d)
        self.write_message(o)
        logger.error(d)

    def on_close(self):
        self.clients.remove(self)

    def check_origin(self, origin):
        return True

def dispatch(message):
    cluster = EchoWebSocket.clients
    for c in cluster:
        c.on_broadcast(message[0])


handlers = [
    (r'/', EchoWebSocket)
]


def main():
    """Main entry-point"""
    application = Application(handlers, port=9666)
    context = zmq.Context()
    iol = ioloop.IOLoop.current()
    socket = context.socket(zmq.SUB)
    socket.bind('tcp://127.0.0.1:5000')
    socket.setsockopt_string(zmq.SUBSCRIBE, u'')
    stream = zmqstream.ZMQStream(socket, iol)
    stream.on_recv(dispatch)
    application.listen(9666)
    iol.start()


if __name__ == '__main__':
    main()

