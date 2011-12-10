from twistymud.chatserver import ChatServerFactory
from twisted.trial import unittest
from twisted.test import proto_helpers



class RemoteCalculationTestCase(unittest.TestCase):
    def setUp(self):
        factory = ChatServerFactory()
        self.proto = factory.buildProtocol(('127.0.0.1', 0))
        self.tr = proto_helpers.StringTransport()
        self.proto.makeConnection(self.tr)

        self.proto2 = factory.buildProtocol(('127.0.0.1', 0))
        self.tr2 = proto_helpers.StringTransport()
        self.proto2.makeConnection(self.tr2)


    def assertYouSaid(self, operation, a, b, expected):
        self.proto.dataReceived('%s %d %d\r\n' % (operation, a, b))
        self.assertEqual(self.tr.value(), "You said: " + expected)
        self.assertEqual(self.tr2.value(),"They said: " + expected)


    def test_add(self):
        return self.assertYouSaid('add', 7, 6, "add 7 6\r\n")


    def test_subtract(self):
        return self.assertYouSaid('subtract', 82, 78, "subtract 82 78\r\n")


    def test_multiply(self):
        return self.assertYouSaid('multiply', 2, 8, "multiply 2 8\r\n")


    def test_divide(self):
        return self.assertYouSaid('divide', 14, 3, "divide 14 3\r\n")

