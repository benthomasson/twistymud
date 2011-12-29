#!/usr/bin/env python

import unittest
from twistymud.persist import P,getP
from twistymud.exceptions import GameException

class Container(object):

    def __init__(self):
        self.contains = []

    def remove(self,o):
        self.checkRemove(o)
        try:
            self.contains.remove(o)
        except ValueError:
            pass
        o.location = P.null

    def add(self,o):
        self.checkHold(o)
        if o.location():
            o.location().remove(o)
        o.location = getP(self)
        p = getP(o)
        if o not in self.contains:
            self.contains.append(p)

    def getById(self,id):
        for o in self.contains:
            if o and o.id == id:
                return o()
        raise GameException("Cannot find id %s" % id)

    def get(self,id=None,attribute=None,index=0):
        if id:
            return self.getById(id)
        elif attribute:
            if attribute == 'all':
                return map(lambda x:x(),self.contains)
            if attribute.startswith('all.'):
                attribute = attribute[4:]
                matches = []
                for o in self.contains:
                    if o:
                        o = o()
                        if attribute == o.name:
                            matches.append(o)
                        elif attribute in o.attributes:
                            matches.append(o)
                if not matches:
                    raise GameException("Cannot find anything like %s" % attribute)
                return matches
            for o in self.contains:
                if o:
                    o = o()
                    if attribute == o.name:
                        return [o]
                    elif attribute in o.attributes:
                        return [o]
            raise GameException("Cannot find anything like %s" % attribute)
        else:
            raise GameException("Cannot find anything like %s" % attribute)

    def seen(self,o):
        o.sendMessage("container",contains = self.contains)

    def checkHold(self,o):
        pass

    def checkRemove(self,o):
        pass

class SlottedContainer(Container):

    slotNames = []

    def __init__(self):
        Container.__init__(self)
        self.slots = {}

    def add(self,o,slot=None):
        if not slot:
            Container.add(self,o)
            return
        self.checkHoldSlot(o,slot)
        if slot in self.slots:
            other = self.slots[slot]()
            self.add(other)
        if o.location:
            o.location().remove(o)
        self.slots[slot] = getP(o)
        o.location = getP(self)
        o.locationSlot = slot

    def remove(self,o):
        if not o.locationSlot:
            Container.remove(self,o)
            return
        if o.locationSlot and o.locationSlot in self.slots:
            del self.slots[o.locationSlot]
        o.location = P.null
        o.locationSlot = None
    
    def getFromSlots(self,id=None,attribute=None,slot=None):
        if slot:
            if slot not in self.slots:
                raise GameException("You find nothing there")
            return self.slots[slot]
        if id:
            for x in self.slots.values():
                if x.id == id:
                    return x()
        if attribute:
            for x in self.slots.values():
                x = x()
                if attribute == x.name:
                    return x
                if attribute in x.attributes:
                    return x
            raise GameException("Cannot find anything like %s" % attribute)
        raise GameException("Cannot find that here")

    def checkHoldSlot(self,o,slot):
        if slot not in self.slotNames:
            raise GameException("You cannot put something there")
        if slot not in o.fitsInSlots:
            raise GameException("It does not fit there")

    def checkRemoveSlot(self,o,slot):
        pass
