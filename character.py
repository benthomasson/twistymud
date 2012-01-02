


from .persist import Persistent, NULL
from .clock import Clock
from .message import Channel, RepeaterMixin
import pickle
from .container import Container
from .sim import Sim

class Character(RepeaterMixin,Channel,Sim):

    location = NULL
    name = "someone"
    attributes = ['character']
    deferred = None
    task = None

    def __init__(self,id=None):
        Channel.__init__(self)
        self.task = None
        self.d = None
        self.id = id

    def doSomethingLater(self):
        self.cancel_command()
        self.task = "work"
        self.d = self.callLater(10,self.finishSomething)
        self.sendMessage("task",message="Starting work")

    def command_do(self,*args):
        return self.doSomethingLater()

    def command_stop(self,*args):
        self.cancel_command()

    def command_spy(self,*args):
        self.sendMessage("spy",message="""
        self {0}
        task {1}
        id {2}
        listeners {3}
        """.format(id(self),self.task,self.id,self.listeners))

    def command_pickle(self,*args):
        self.sendMessage("pickle",message=pickle.dumps(self))

    def command_say(self,*args):
        line = " ".join(args)
        self.sendMessage("say",message="You said: " + line)
        #self.channel.sendMessage('say',message="They said: " + line,_exclude=[self])

    def cancel_command(self):
        if self.d:
            self.sendMessage("task", message="Stopping " + self.task)
            if self.d.active():
                self.d.cancel()
            self.task = ""
            self.d = None

    def finishSomething(self):
        self.task = ""
        self.sendMessage("task",message="Finished work")


