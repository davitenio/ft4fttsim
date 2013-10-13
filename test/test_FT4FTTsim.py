import unittest
from FT4FTTSim import *

class TestLink(unittest.TestCase):

    def setUp(self):
        self.source = NetworkComponent("source")
        self.destination = NetworkComponent("destination")
        self.link = Link(self.source, self.destination, 0)

    def test_get_end_point(self):
        self.assertEqual(self.link.get_end_point(), self.destination)

    def test_link_has_no_message_when_created(self):
        self.assertFalse(self.link.has_message())

    def test_put_message_then_has_message(self):
        m = Message(self.source, [self.destination], "test message")
        self.link.put_message(m)
        self.assertEqual(self.link.get_message(), m)

if __name__ == '__main__':
    unittest.main()
