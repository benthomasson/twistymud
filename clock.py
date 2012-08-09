
from twistymud.settings import TICK_TIME

from persist import Persistent, getP

from twisted.internet import reactor
from twisted.internet import task

class Clock(Persistent):

    instance = None

    @classmethod
    def getInstance(cls,*args,**kwargs):
        if not cls.instance:
            cls.instance = cls(*args,**kwargs)
        return cls.instance

    def __init__(self,id=None):
        Persistent.__init__(self)
        self.id = id
        self.events = {}
        self.time = 0L
        self.nextEventId=1
        self.stopped = False
        self.debug = False

    def callLater(self,time,function,*args,**kwargs):
        return reactor.callLater(time,function,*args,**kwargs)

    def start(self):
        self.callLater(TICK_TIME,self.tick)
        self.stopped = False

    def stop(self):
        self.stopped = True

    def tick(self):
        self.time+=1
        if self.debug:
            print self.time
        self.callLater(TICK_TIME,self.tick)

    def addEvent(self,time,o,name,*args,**kwargs):
        eventId = self.nextEventId
        self.nextEventId+=1
        self.events[eventId] = (self.time,self.time+time,getP(o),name,args,kwargs)
        self.callLater(time,self.callEvent,eventId)
        return eventId

    def callEvent(self,eventId):
        if self.stopped:
            return
        if eventId not in self.events:
            return
        start,end,p,name,args,kwargs = self.events[eventId]
        del self.events[eventId]
        o = p()
        if o and hasattr(o,name):
            func = getattr(o,name)
            func(*args,**kwargs)

    def cancel(self,eventId):
        if eventId in self.events:
            del self.events[eventId]

    def __setstate__(self,d):
        self.__dict__.update(d)
        self.restartEvents()

    def restartEvents(self):
        for (eventId, (scheduleTime, eventTime, p, names, args, kwargs)) in self.events.iteritems():
            time = eventTime - self.time
            if time < 0:
                time = 0
            self.callLater(time,self.callEvent,eventId)

class TestableClock(Clock):

    @classmethod
    def makeTestClock(cls):
        Clock.instance = TestableClock()
        return Clock.instance

    def __init__(self):
        Clock.__init__(self)
        self.clock = task.Clock()

    def advance(self,time):
        for i in xrange(time):
            self.clock.advance(1)

    def callLater(self,time,function,*args,**kwargs):
        return self.clock.callLater(time,function,*args,**kwargs)

    def __getstate__(self):
        d = self.__dict__.copy()
        del d['clock']
        return d

    def __setstate__(self,d):
        self.__dict__.update(d)
        self.clock = task.Clock()
        self.restartEvents()
