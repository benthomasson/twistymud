
from .persist import Persistent
from .clock import Clock
from .message import Channel, RepeaterMixin


class Sim(Persistent):

    def callLater(self, time, function, *args,**kwargs):
        return Clock.getInstance().callLater(time, function, *args, **kwargs)


class Character(RepeaterMixin,Channel,Sim):

    def __init__(self):
        Channel.__init__(self)
        self.task = None
        self.d = None

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
        """.format(id(self),self.task,self.id))

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

class Item(Sim):
    pass

