import unittest
import os
import shelve
from twistymud.persist import P, getP, deref, Persistent

class TestShelve(unittest.TestCase):

    def setUp(self):
        if os.path.exists("test.db"): os.remove("test.db")
        if os.path.exists("test.db.db"): os.remove("test.db.db")

    def testSimple(self):
        s = shelve.open("test.db",protocol=2)
        s['a'] = 1
        s.close()
        s = shelve.open("test.db",protocol=2)
        self.assertEquals(s['a'],1)
        s.close()

class TestP(unittest.TestCase):

    def setUp(self):
        P.instances = {}
        P.persistence = None

    def testNull(self):
        p = P()
        self.assertEquals(p.id,None)
        self.assertEquals(p.ref,None)
        self.assertEquals(str(p),'PNone')
        self.assertFalse(p)
        self.assertTrue(p==P())
        self.assertTrue(p==P.null)
        self.assertEquals(p(),None)
        self.assertEquals(p.deref(),None)
        self.assertEquals(deref(p),None)
        self.assertTrue(p==getP(None))
        self.assertEquals(p.__getstate__(),dict(id=None))

    def testPersistent(self):
        o = Persistent()
        o.id = 1
        p = P(o)
        self.assertEquals(p.id,1)
        self.assert_(p.ref is o)
        self.assert_(getP(o) is p)
        self.assert_(deref(p) is o)
        self.assert_(p() is o)
        self.assert_(p.deref() is o)
        self.assertEquals(id(deref(p)),id(o))
        self.assertEquals(getP(o),p)
        self.assertEquals(len(P.instances),1)
        self.assert_(p)
        self.assertEquals(p,P(o))
        self.assert_(getP(o) is not p)
        self.assertEquals(p.__getstate__(),dict(id=1))

