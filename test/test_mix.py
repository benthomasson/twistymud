
from twisted.trial import unittest

from ..mix import mix_classes
from pickle import loads, dumps

import twistymud.mixed

class Man(object):

    def seen(self):
        return "a man"

    def seenAtNight(self):
        return "a man"

class Werewolf(object):

    def seenAtNight(self):
        return "a wolf"

class TestMix(unittest.TestCase):

    def setUp(self):
        if hasattr(twistymud.mixed,'WerewolfMan'):
            del twistymud.mixed.WerewolfMan

    def testMan(self):
        x = Man()
        self.assertEquals(x.seen(),"a man")
        self.assertEquals(x.seenAtNight(),"a man")

    def testWerewolf(self):
        x = Werewolf()
        self.assertEquals(x.seenAtNight(),"a wolf")

    def testMix(self):
        X = mix_classes('WerewolfMan',Man,Werewolf)
        x = X()
        self.assertEquals(x.seen(),"a man")
        self.assertEquals(x.seenAtNight(),"a wolf")

    def testPickle(self):
        X = mix_classes('WerewolfMan',Man,Werewolf)
        x = X()
        self.assertEquals(x.seen(),"a man")
        self.assertEquals(x.seenAtNight(),"a wolf")
        p = dumps(x)
        x2 = loads(p)
        self.assertEquals(x2.seen(),"a man")
        self.assertEquals(x2.seenAtNight(),"a wolf")



