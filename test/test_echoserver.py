from twistymud.echoserver import EchoServerFactory
from twisted.trial import unittest
from twisted.test import proto_helpers



class RemoteCalculationTestCase(unittest.TestCase):
    def setUp(self):
        factory = EchoServerFactory()
        self.proto = factory.buildProtocol(('127.0.0.1', 0))
        self.tr = proto_helpers.StringTransport()
        self.proto.makeConnection(self.tr)


    def _test(self, operation, a, b, expected):
        self.proto.dataReceived('%s %d %d\r\n' % (operation, a, b))
        self.assertEqual(self.tr.value(), expected)


    def test_add(self):
        return self._test('add', 7, 6, "You said: add 7 6\r\n")


    def test_subtract(self):
        return self._test('subtract', 82, 78, "You said: subtract 82 78\r\n")


    def test_multiply(self):
        return self._test('multiply', 2, 8, "You said: multiply 2 8\r\n")


    def test_divide(self):
        return self._test('divide', 14, 3, "You said: divide 14 3\r\n")

