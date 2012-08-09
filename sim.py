
from persist import Persistent, NULL
from .clock import Clock
from .message import Channel, RepeaterMixin
import pickle
from .container import Container


class Sim(Persistent):

    attributes = []
    name = "thing"
    locationSlot = None
    id = None
    description = "something"
    detail = "maybe it's nothing"
    article = "a"
    attributes = []
    name = 'thing'
    location = NULL

    def __init__(self,id=None):
        Persistent.__init__(self,id)

    def callLater(self, time, function, *args,**kwargs):
        return Clock.getInstance().callLater(time, function, *args, **kwargs)
