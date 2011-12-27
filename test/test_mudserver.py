from twistymud.mudserver import MudServerFactory
from twisted.trial import unittest
from twisted.internet import task
from twisted.test import proto_helpers
from ..persist import P



class RemoteCalculationTestCase(unittest.TestCase):
    def setUp(self):
        P.instances = {}
        self.clock = task.Clock()
        factory = MudServerFactory()
        self.proto = factory.buildProtocol(('127.0.0.1', 0))
        self.proto.callLater = self.clock.callLater
        self.tr = proto_helpers.StringTransport()
        self.proto.makeConnection(self.tr)

        self.proto2 = factory.buildProtocol(('127.0.0.1', 0))
        self.proto2.callLater = self.clock.callLater
        self.tr2 = proto_helpers.StringTransport()
        self.proto2.makeConnection(self.tr2)

    def assertCommand(self, command, expected):
        self.proto.dataReceived(command)
        self.assertEqual(self.tr.value(), expected)

    def assertYouSaid(self, operation, a, b, expected):
        self.proto.dataReceived('%s %d %d\r\n' % (operation, a, b))
        self.assertEqual(self.tr.value(), "You said: " + expected + ">")
        self.assertEqual(self.tr2.value(),"They said: " + expected + ">")


    def test_add(self):
        return self.assertYouSaid('add', 7, 6, "add 7 6\r\n")


    def test_subtract(self):
        return self.assertYouSaid('subtract', 82, 78, "subtract 82 78\r\n")


    def test_multiply(self):
        return self.assertYouSaid('multiply', 2, 8, "multiply 2 8\r\n")


    def test_divide(self):
        return self.assertYouSaid('divide', 14, 3, "divide 14 3\r\n")

    def test_hi(self):
        return self.assertCommand('hi\r\n', "You said: hi\r\n>")

    def test_quit(self):
        return self.assertCommand('quit\r\n', "Goodbye.\r\n")

    def test_do(self):
        self.assertCommand('do\r\n', "Starting work\r\n(work)>")
        self.clock.advance(20)
        self.assertEqual(self.tr.value(), 'Starting work\r\n(work)>Finished work\r\n>')

