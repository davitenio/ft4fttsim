import unittest
from FT4FTTSim import *

class TestLink(unittest.TestCase):

    def setUp(self):
        self.source = NetworkComponent("source")
        self.destination = NetworkComponent("destination")
        self.link = Link(self.source, self.destination, 0)

    def test_get_end_point(self):
        self.assertEqual(self.link.get_end_point(), self.destination)

if __name__ == '__main__':
    unittest.main()
