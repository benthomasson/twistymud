

import unittest

from ..message import Channel

class TestChannel(unittest.TestCase):

    def receiveMessage(self,message):
        self.receivedMessage = "%(name)s says '%(message)s'" % message.dict

    def testChannel(self):
        self.id = '1'
        c = Channel()
        c.addListener(self)
        self.assert_(c.listeners['1'])
        self.assertEquals(c.listeners['1'].id,'1')
        self.assertEquals(c.listeners['1'].ref,self)
        self.assertEquals(c.listeners['1'].deref(),self)
        self.assertEquals(c.listeners['1']().id,'1')
        self.assertEquals(c.listeners['1'](),self)
        c.sendMessage("say",message="hello1",name="Ed",id="1")
        self.assertEquals(self.receivedMessage,"Ed says 'hello1'")
        self.receivedMessage=None
        c.sendMessage("say",message="hello3",name="Ed",id="1",_exclude=[self])
        self.assertFalse(self.receivedMessage)
        self.deleted = True
        c.sendMessage("say",message="hello2",name="Ed",id="1")
        self.assertFalse(self.receivedMessage)



