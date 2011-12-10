#!/usr/bin/env python


from twisted.internet import reactor, protocol

class QuickDisconnectionProtocol(protocol.Protocol):
    def connectionMade(self):
        print "Connection to %s" % self.transport.getPeer().host
        self.transport.loseConnection()


class BasicClientFactory(protocol.ClientFactory):


    protocol = QuickDisconnectionProtocol

    def clientConnectionLost(self,connection, reason):
        print "Lost conneciton: %s" % reason.getErrorMessage()
        reactor.stop()


    def clientConnectionFailed(self,connector,reason):
        print "Connection failed %s:" % reason.getErrorMessage()
        reactor.stop()


reactor.connectTCP('www.google.com', 80, BasicClientFactory())
reactor.run()


