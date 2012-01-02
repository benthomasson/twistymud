
from twisted.trial import unittest

from twistymud.persist import P, getP, deref, Persistent, makeTemporary, reset, MockPersistence
import twistymud.persist
from twistymud.character import Character
from twistymud.item import Item
from twistymud.container import Container,SlottedContainer
from twistymud.exceptions import GameException

class Test(unittest.TestCase):

    def setUp(self):
        reset()
        twistymud.persist.persistence = MockPersistence()

    def testSingle(self):
        c = Container()
        c.id = "container"
        m = Character(id='mob')
        m.name = "mob"
        c.add(m)
        self.assertEquals(c.id,"container")
        self.assertEquals(m.id,"mob")
        self.assert_( m in c.contains)
        self.assertEquals(c.get(id='mob'),m)
        self.assertEquals(c.get(attribute='mob'),[m])
        self.assert_(m.location)
        c.remove(m)
        self.assertFalse('mob' in c.contains)
        self.assertFalse(m.location)
        pass

    def testMultiple(self):
        c = Container()
        c.id = "container"
        m1 = Character(id='mob1')
        m1.name = "mob1"
        m2 = Character(id='mob2')
        m2.name = "mob2"
        c.add(m1)
        c.add(m2)
        self.assert_(m1 in c.contains)
        self.assertEquals(c.get(id='mob1'),m1)
        self.assertEquals(c.get(id='mob2'),m2)
        self.assertEquals(c.get(attribute='character'),[m1])
        c.remove(m1)
        self.assert_(m2 in c.contains)
        self.assertEquals(c.get(id='mob2'),m2)
        self.assertEquals(c.get(attribute='character'),[m2])
        c.remove(m2)
        self.assertFalse(m2 in c.contains)
        self.assertRaises(GameException,c.get,attribute='xcvc')
        self.assertRaises(GameException,c.get,attribute='mob')

class TestSlotted(unittest.TestCase):

    def setUp(self):
        P.instances = {}
    
    def testNonSlotted(self):
        c = SlottedContainer()
        c.id = "container"
        thing = Item(id='thing')
        c.add(thing)
        self.assertEquals(thing.location(),c)
        self.assert_(thing in c.contains)
        c.remove(thing)
        self.assertFalse(thing.location)
        self.assertFalse('thing' in c.contains)

    def testSlotted(self):
        c = SlottedContainer()
        c.id = "container"
        c.slotNames = ['hand']
        thing = Item(id='thing')
        thing.fitsInSlots = ['hand']
        c.add(thing,'hand')
        self.assertEquals(c.slots['hand'](),thing)
        self.assertEquals(thing.location(),c)
        self.assertEquals(thing.locationSlot,'hand')
        c.remove(thing)
        self.assertFalse(thing.location)
        self.assertFalse(thing.locationSlot)
        self.assertRaises(GameException,c.add,thing,'head')

    def testMoveSlots(self):
        c = SlottedContainer()
        c.id = "container"
        c.slotNames = ['head','hand']
        thing = Item(id='thing')
        thing.fitsInSlots = ['hand','head']
        c.add(thing,'hand')
        self.assertEquals(c.slots['hand'](),thing)
        self.assertEquals(thing.location(),c)
        self.assertEquals(thing.locationSlot,'hand')
        c.add(thing,'head')
        self.assertEquals(c.slots['head'](),thing)
        self.assertEquals(thing.location(),c)
        self.assertEquals(thing.locationSlot,'head')

