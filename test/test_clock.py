

from twisted.trial import unittest
from twisted.internet import task

from ..clock import Clock, TestableClock
from ..persist import Persistent, getP, deref, reset, persist, MockPersistence, Persistence
import twistymud.persist
import os

class X(Persistent):

    def __init__(self):
        Persistent.__init__(self)
        self.reset()

    def reset(self):
        self.called = False

    def f(self):
        self.called = True


class TestClock(unittest.TestCase):

    def setUp(self):
        reset()

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


class TestTestableClock(unittest.TestCase):

    def setUp(self):
        reset()

    def testAddEvent(self):
        c = TestableClock()
        x = X()
        x.id = 1
        self.assertFalse(x.called)
        eventId = c.addEvent(10,x,'f')
        self.assertEquals(eventId,1)
        self.assertEquals(c.events[1],(0,10,getP(x),'f',(),{}))
        self.assert_(1 in c.events)
        c.advance(10)
        self.assertFalse(1 in c.events)
        self.assert_(x.called)

    def testCancel(self):
        c = TestableClock()
        x = X()
        x.id = 1
        self.assertFalse(x.called)
        eventId = c.addEvent(10,x,'f')
        self.assertEquals(eventId,1)
        self.assertEquals(c.events[1],(0,10,getP(x),'f',(),{}))
        c.cancel(1)
        self.assertFalse(1 in c.events)
        c.advance(10)
        self.assertFalse(x.called)

class TestPersist(unittest.TestCase):

    def setUp(self):
        reset()
        if os.path.exists("test.db"): os.remove("test.db")
        if os.path.exists("test.db.db"): os.remove("test.db.db")


    def buildClock(self):
        self.c = TestableClock()
        self.c.id = 'clock'


    def testPersistMock(self):
        twistymud.persist.persistence = MockPersistence()
        self.buildClock()
        self.assertEquals(self.c.id,'clock')
        self.assertEquals(self.c.time,0)
        self.c.start()
        self.c.advance(10)
        self.assertEquals(self.c.time,10)
        p = getP(self.c)
        persist(self.c)
        self.c = None
        self.c = deref(p)
        self.assertEquals(self.c.id,'clock')
        self.assertEquals(self.c.time,10)
        self.c.advance(10)
        self.assertEquals(self.c.time,20)

    def testPersist(self):
        twistymud.persist.persistence = Persistence("test.db")
        self.buildClock()
        self.assertEquals(self.c.id,'clock')
        self.assertEquals(self.c.time,0)
        self.c.start()
        self.c.advance(10)
        self.assertEquals(self.c.time,10)
        p = getP(self.c)
        persist(self.c)
        self.assertEquals(twistymud.persist.P.instances,{'clock':self.c})
        twistymud.persist.persistence.syncAll()
        reset()
        self.c = None
        p.clear()
        self.assertEquals(twistymud.persist.persistence,None)
        self.assertEquals(twistymud.persist.P.instances,{})
        twistymud.persist.persistence = Persistence("test.db")
        self.c = deref(p)
        self.assertEquals(self.c.id,'clock')
        self.assertEquals(self.c.time,10)
        self.c.advance(10)
        self.assertEquals(self.c.time,20)

    def testPersistEvents(self):
        twistymud.persist.persistence = Persistence("test.db")
        self.buildClock()
        self.c.start()
        persist(self.c)
        clockP = getP(self.c)
        x = X()
        memId = id(x)
        persist(x)
        xP = getP(x)
        eventId = self.c.addEvent(10,x,'f')
        self.assertEquals(x.id,'1')
        self.assertFalse(x.called)
        self.assertEquals(twistymud.persist.P.instances,{'clock':self.c,'1':x})
        twistymud.persist.persistence.syncAll()
        twistymud.persist.persistence.close()
        reset()
        self.c = None
        clockP.clear()
        xP.clear()
        x = None
        self.assertEquals(twistymud.persist.persistence,None)
        self.assertEquals(twistymud.persist.P.instances,{})
        twistymud.persist.persistence = Persistence("test.db")
        self.c = deref(clockP)
        x = deref(xP)
        self.assertEquals(x.id,'1')
        self.assert_(self.c.events)
        self.assert_(self.c.events[1])
        self.assertEquals(self.c.events[1][0],0)
        self.assertEquals(self.c.events[1][1],10)
        self.assertEquals(self.c.events[1][2],x)
        self.assertEquals(self.c.events[1][3],'f')
        self.assertEquals(self.c.events[1][4],())
        self.assertEquals(self.c.events[1][5],{})
        self.assertFalse(x.called)
        self.assertNotEquals(id(x),memId)
        self.c.advance(10)
        x = deref(xP)
        self.assertNotEquals(id(x),memId)
        self.assert_(x.called)

