

from twisted.trial import unittest
from twisted.internet import task

from ..clock import Clock
from ..persist import Persistent, getP

class X(Persistent):

    def __init__(self):
        Persistent.__init__(self)
        self.reset()

    def reset(self):
        self.called = False

    def f(self):
        self.called = True


class TestClock(unittest.TestCase):

    def testInit(self):
        c = Clock()
        self.assertEquals(c.time,0)
        self.assertEquals(c.nextEventId,1)
        self.assertEquals(c.events,{})

    def testTick(self):
        testClock = task.Clock()
        c = Clock()
        c.callLater = testClock.callLater
        self.assertEquals(c.time,0)
        self.assertEquals(c.events,{})
        c.tick()
        self.assertEquals(c.time,1)
        for i in xrange(1000):
            c.tick()
        self.assertEquals(c.time,1001)

    def testStart(self):
        testClock = task.Clock()
        self.assertEquals(testClock.seconds(),0)
        c = Clock()
        c.callLater = testClock.callLater
        c.start()
        self.assertEquals(c.time,0)
        testClock.advance(1)
        self.assertEquals(testClock.seconds(),1)
        self.assertEquals(c.time,1)
        testClock.advance(1)
        self.assertEquals(testClock.seconds(),2)
        self.assertEquals(c.time,2)
        for i in xrange(10):
            testClock.advance(1)
        self.assertEquals(testClock.seconds(),12)
        self.assertEquals(c.time,12)


    def testAddEvent(self):
        testClock = task.Clock()
        c = Clock()
        c.callLater = testClock.callLater
        x = X()
        x.id = 1
        self.assertFalse(x.called)
        eventId = c.addEvent(10,x,'f')
        self.assertEquals(eventId,1)
        self.assertEquals(c.events[1],(0,10,getP(x),'f',(),{}))
        testClock.advance(10)
        self.assert_(x.called)


    def testCancel(self):
        testClock = task.Clock()
        c = Clock()
        c.callLater = testClock.callLater
        x = X()
        x.id = 1
        self.assertFalse(x.called)
        eventId = c.addEvent(10,x,'f')
        self.assertEquals(eventId,1)
        self.assertEquals(c.events[1],(0,10,getP(x),'f',(),{}))
        c.cancel(1)
        self.assertFalse(1 in c.events)
        testClock.advance(10)
        self.assertFalse(x.called)


