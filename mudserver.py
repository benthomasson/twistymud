
from twistymud.settings import DB_NAME, PORT

from twisted.internet import reactor, protocol
from twisted.internet.task import deferLater
from twisted.protocols import basic

import time

from twistymud.clock import Clock
from twistymud.message import Channel
from twistymud.character import Character

from persist import Persistence,  getOrCreate, makeTemporary
import persist

class MudProtocol(basic.LineReceiver):

    clients = []

    def __init__(self):
        self.clients.append(self)
        self.id = None
        makeTemporary(self)
        self.d = None
        self.doing = ""
        self.channel = Mud.getInstance().channel
        self.channel.addListener(self)
        self.character = Character()
        self.character.addListener(self)
        persist.persist(self.character)

    def command_help(self,*args):
        self.sendLine("No help yet.")
        self.prompt()

    def command_quit(self,*args):
        self.sendLine("Goodbye.")
        self.transport.loseConnection()

    def lineReceived(self, line):
        self.execute_command(line)

    def execute_command(self,line):
        command,_, rest = line.partition(" ")
        command_fn = "command_{0}".format(command)
        args = rest.split(" ")
        if hasattr(self,command_fn):
            return getattr(self,command_fn)(*args)
        elif hasattr(self.character,command_fn):
            return getattr(self.character,command_fn)(*args)
        else:
            return self.character.command_say(*[command] + args)

    def receiveMessage(self,message):
        self.sendMessage(message.dict['message'])

    def sendMessage(self,string):
        self.sendLine(string)
        self.prompt()

    def sendString(self,string):
        self.transport.write(string)

    def prompt(self):
        if self.character.task:
            self.sendString("({0})>".format(self.character.task))
        else:
            self.sendString(">")

class MudServerFactory(protocol.ServerFactory):
    protocol = MudProtocol

class Mud(object):

    instance = None

    @classmethod
    def getInstance(cls,*args,**kwargs):
        if not cls.instance:
            cls.instance = cls(*args,**kwargs)
        return cls.instance

    def __init__(self,port=PORT):
        persist.persistence = Persistence(DB_NAME)
        self.clock = getOrCreate('clock',Clock)
        self.clock.debug = True
        self.channel = getOrCreate('channel',Channel)
        self.port = port

    def run(self):
        self.clock.start()
        reactor.listenTCP(self.port, MudServerFactory())
        try:
            print "Running on {0}".format(self.port)
            reactor.run()
        finally:
            print "\Persisting..."
            persist.persistence.syncAll()
            persist.persistence.close()
            print "\nDone"

