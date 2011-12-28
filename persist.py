#!/usr/bin/env python

import shelve
import sys
import os
from twistymud.coroutine import coroutine,step,finish

persistence = None

def reset():
    global persistence
    persistence = None
    P.instances = {}

def persist(o):
    global persistence
    if persistence:
        persistence.persist(o)
    else:
        raise Exception("No persistence installed")

def makeTemporary(o):
    global persistence
    if persistence:
        persistence.persist(o)
    else:
        raise Exception("No persistence installed")

def getOrCreate(id,klass,*args,**kwargs):
    global persistence
    if persistence:
        return persistence.getOrCreate(id,klass,*args,**kwargs)
    else:
        raise Exception("No persistence installed")

def getP(o):
    if None is o:
        return P.null
    if o.id in P.instances:
        return P.instances[o.id]
    else:
        p = P(o)
        P.instances[o.id] = p
        return p

def deref(p):
    if isinstance(p,P):
        return p.deref()
    raise Exception("Not a P")


class P(object):
    """P is a persistent reference to a persistent object.
    To create a new persistent reference use:
    
    >>> x = persist.P(o).

    To retrieve the object from the persistent reference above use:

    >>> x()
    """

    instances = {}

    __slots__ = ['id','ref']

    def __init__(self,o=None):
        if not o:
            self.id = None
            self.ref = None
        elif isinstance(o,P):
            self.id = o.id
            self.ref = o()
        else:
            self.id = o.id
            self.ref = o
        P.instances[self.id] = self

    def __call__(self):
        return self.deref()

    def deref(self):
        global persistence
        if self.ref and not hasattr(self.ref,'deleted'):
            return self.ref
        if self.ref and not self.ref.deleted:
            return self.ref
        if self.ref and self.ref.deleted:
            return None
        if not self.id: return None
        try:
            if persistence:
                self.ref = persistence.get(self.id)
                return self.ref
            else:
                return None
        except KeyError,e:
            return None

    def __eq__(self,other):
        return self.id == other.id

    def __nonzero__(self):
        return self() != None

    def clear(self):
        self.ref = None

    def delete(self):
        global persistence
        del P.instances[self.id]
        if persistence:
            persistence.delete(self)
        self.id = None
        self.ref = None

    def __setstate__(self,state):
        self.id = state['id']
        self.ref = None

    def __getstate__(self):
        state = {}
        state['id'] = self.id
        return state

    def __str__(self):
        return "P" + str(self())

    def __repr__(self):
        return "P" + repr(self())

P.null = P()

class Persistence(object):

    def __init__(self,filename):
        self.db = shelve.open(filename,protocol=2,writeback=True)
        self.writeBackIterator = None
        if '0' in self.db:
            self.id = self.db['0']
        else:
            self.id = 0
        self.db['0'] = self.id

    def getNextId(self):
        self.id += 1
        self.db['0'] = self.id
        return self.id

    def persist(self,o):
        if not o.id:
            o.id = "%x" % self.getNextId()
        self.db[o.id] = o
        return o

    def makeTemporary(self,o):
        if not o.id:
            o.id = "%x" % self.getNextId()
        if o.id in self.db:
            del self.db[o.id]
        return o

    def get(self,id):
        return self.db[id]

    def getOrCreate(self,id,klass,*args,**kwargs):
        if self.exists(id):
            return self.get(id)
        else:
            instance = klass(id=id,*args,**kwargs)
            instance.id = id
            self.persist(instance)
            return instance

    def exists(self,id):
        try:
            self.db[id]
            return True
        except KeyError, e:
            return False

    def delete(self,o):
        if o.id in self.db:
            self.db[o.id].deleted = True
            del self.db[o.id]

    def sync(self,n=1):
        if not self.writeBackIterator:
            self.writeBackIterator = self.partialSync()
        if not step(self.writeBackIterator,n):
            self.writeBackIterator = None
            return True
        return False

    def syncAll(self):
        #if not self.writeBackIterator:
        #    self.writeBackIterator = self.partialSync()
        #finish(self.writeBackIterator)
        self.db.dict.sync()

    @coroutine
    def partialSync(self):
        db = self.db
        for key, entry in db.cache.copy().iteritems():
            yield
            db.writeback = False
            #print "Persisting %s" % key
            db[key] = entry
            db.writeback = True

    def run(self,n=1):
        self.sync(n)

    def close(self):
        self.db.close()

class MockPersistence(Persistence):

    def __init__(self):
        self.db = {}
        if '0' in self.db:
            self.id = self.db['0']
        else:
            self.id = 0
        self.db['0'] = self.id

    def sync(self,n=1):
        pass

    def syncAll(self):
        pass

    @coroutine
    def partialSync(self):
        yield

    def close(self):
        self.db = None
        self.id = None

class Persistent(object):

    def __init__(self):
        self.id = None
        self.deleted = False

