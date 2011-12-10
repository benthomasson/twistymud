#!/usr/bin/env python

from twisted.internet import reactor, protocol
from twisted.protocols import basic


class EchoProtocol(basic.LineReceiver):
    def lineReceived(self, line):
        if line == 'quit':
            self.sendLine("Goodbye.")
            self.tranport.loseConnection()
        else:
            self.sendLine("You said: " + line)


class EchoServerFactory(protocol.ServerFactory):
    protocol = EchoProtocol


if __name__ == "__main__":
    port = 5001
    reactor.listenTCP(port, EchoServerFactory())
    reactor.run()
