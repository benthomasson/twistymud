

from .persist import Persistent,getP,deref

from twisted.internet import reactor
from twisted.internet import task

class Clock(Persistent):

    instance = None

    @classmethod
    def getInstance(cls,*args,**kwargs):
        if not cls.instance:
            cls.instance = cls(*args,**kwargs)
        return cls.instance

    def __init__(self):
        Persistent.__init__(self)
        self.events = {}
        self.time = 0L
        self.nextEventId=1

    def callLater(self,time,function,*args,**kwargs):
        return reactor.callLater(time,function,*args,**kwargs)

    def start(self):
        self.callLater(1,self.tick)

    def tick(self):
        self.time+=1
        self.callLater(1,self.tick)

    def addEvent(self,time,o,name,*args,**kwargs):
        eventId = self.nextEventId
        self.nextEventId+=1
        self.events[eventId] = (self.time,self.time+time,getP(o),name,args,kwargs)
        self.callLater(time,self.callEvent,eventId)
        return eventId

    def callEvent(self,eventId):
        if eventId not in self.events:
            return
        start,end,p,name,args,kwargs = self.events[eventId]
        del self.events[eventId]
        o = deref(p)
        if o and hasattr(o,name):
            func = getattr(o,name)
            func(*args,**kwargs)

    def cancel(self,eventId):
        if eventId in self.events:
            del self.events[eventId]


class TestableClock(Clock):

    def __init__(self):
        Clock.__init__(self)
        self.clock = task.Clock()

    def advance(self,time):
        self.clock.advance(time)

    def callLater(self,time,function,*args,**kwargs):
        return self.clock.callLater(time,function,*args,**kwargs)

