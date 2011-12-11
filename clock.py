

from .persist import Persistent,getP,deref

from twisted.internet import reactor

class Clock(Persistent):

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
        o = deref(p)
        if o and hasattr(o,name):
            func = getattr(o,name)
            func(*args,**kwargs)

    def cancel(self,eventId):
        if eventId in self.events:
            del self.events[eventId]

