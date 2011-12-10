#!/usr/bin/env python

from twisted.internet import reactor, protocol
from twisted.protocols import basic


class MudProtocol(basic.LineReceiver):

    clients = []

    def __init__(self):
        self.clients.append(self)

    def lineReceived(self, line):
        if line == 'quit':
            self.sendLine("Goodbye.")
            self.tranport.loseConnection()
        else:
            for client in self.clients:
                if client == self:
                    self.sendLine("You said: " + line)
                else:
                    client.sendLine("They said: " + line)


class MudServerFactory(protocol.ServerFactory):
    protocol = MudProtocol


if __name__ == "__main__":
    port = 5001
    reactor.listenTCP(port, MudServerFactory())
    reactor.run()
