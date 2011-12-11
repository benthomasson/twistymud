#!/usr/bin/env python

from twisted.internet import reactor, protocol
from twisted.internet.task import deferLater
from twisted.protocols import basic

import time


class MudProtocol(basic.LineReceiver):

    clients = []

    def __init__(self):
        self.clients.append(self)
        self.d = None
        self.doing = ""

    def command_quit(self,line):
        self.sendLine("Goodbye.")
        self.transport.loseConnection()

    def command_do(self,line):
        return self.doSomethingLater()

    def command_stop(self,line):
        self.cancel_command()

    def cancel_command(self):
        if self.d:
            self.sendMessage("Stopping " + self.doing)
            if self.d.active():
                self.d.cancel()
            self.doing = ""
            self.d = None


    def lineReceived(self, line):
        command,_, rest = line.partition(" ")
        if hasattr(self,"command_{0}".format(command)):
            return getattr(self,"command_{0}".format(command))(line)
        else:
            for client in self.clients:
                if client == self:
                    self.sendMessage("You said: " + line)
                else:
                    client.sendMessage("They said: " + line)

    def callLater(self,time,function,*args,**kwargs):
        return reactor.callLater(time,function,*args,**kwargs)

    def sendMessage(self,string):
        self.sendLine(string)
        self.prompt()

    def sendString(self,string):
        self.transport.write(string)

    def prompt(self):
        if self.doing:
            self.sendString("({0})>".format(self.doing))
        else:
            self.sendString(">")

    def printTime(self):
        self.sendMessage(time.strftime("%H:%M:%S"))

    def doSomethingLater(self):
        self.cancel_command()
        self.doing = "work"
        self.d = self.callLater(10,self.finishSomething)
        self.sendMessage("Starting work")

    def finishSomething(self):
        self.doing = ""
        self.sendMessage("Finished work")

class MudServerFactory(protocol.ServerFactory):
    protocol = MudProtocol

def printTime():
    for client in MudProtocol.clients:
        client.printTime()
    d = deferLater(reactor,1,printTime)

if __name__ == "__main__":
    port = 5001
    reactor.listenTCP(port, MudServerFactory())
    reactor.callLater(5,printTime)
    reactor.run()
