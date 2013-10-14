# author: David Gessner <davidges@gmail.com>

import unittest
from FT4FTTSim import *

logging.disable(logging.CRITICAL)

class TestLink(unittest.TestCase):

    def setUp(self):
        self.link = Link(0)

    def test_get_end_point__link_created__end_point_is_None(self):
        self.assertEqual(self.link.get_end_point(), None)

    def test_has_message__link_created__returns_false(self):
        self.assertFalse(self.link.has_message())

    def test_get_message__after_put_message__returns_same_message(self):
        source = NetworkDevice("source")
        source.connect_outlink(self.link)
        destination = NetworkDevice("destination")
        destination.connect_inlink(self.link)
        m = Message(source, [destination], "test message")
        self.link.put_message(m)
        self.assertEqual(self.link.get_message(), m)

    def test_get_message__link_created__returns_none(self):
        self.assertEqual(self.link.get_message(), None)


class TestNetworkDevice(unittest.TestCase):

    def setUp(self):
        self.device = NetworkDevice("test device")

    def test_get_outlinks__new_device__returns_empty_list(self):
        self.assertEqual(self.device.get_outlinks(), [])

    def test_get_inlinks__new_device__returns_empty_list(self):
        self.assertEqual(self.device.get_inlinks(), [])

    def test_get_outlinks__connect_1_outlink__returns_new_outlink(self):
        outlink = Link(0)
        self.device.connect_outlink(outlink)
        self.assertEqual(self.device.get_outlinks(), [outlink])

    def test_get_outlinks__connect_2_outlinks__returns_new_outlinks(self):
        outlink1 = Link(0)
        outlink2 = Link(0)
        self.device.connect_outlink(outlink1)
        self.device.connect_outlink(outlink2)
        self.assertEqual(self.device.get_outlinks(), [outlink1, outlink2])

    def test_get_outlinks__connect_2_outlinks_at_once__returns_new_outlinks(self):
        outlinks = [Link(0) for num_links in range(2)]
        self.device.connect_outlink_list(outlinks)
        self.assertEqual(self.device.get_outlinks(), outlinks)

    def test_get_outlinks__connect_3_outlinks__returns_new_outlinks(self):
        outlink1 = Link(0)
        outlink2 = Link(0)
        outlink3 = Link(0)
        self.device.connect_outlink(outlink1)
        self.device.connect_outlink(outlink2)
        self.device.connect_outlink(outlink3)
        self.assertEqual(self.device.get_outlinks(),
            [outlink1, outlink2, outlink3])

    def test_get_outlinks__connect_20_outlinks_at_once__returns_new_outlinks(self):
        outlinks = [Link(0) for num_links in range(20)]
        self.device.connect_outlink_list(outlinks)
        self.assertEqual(self.device.get_outlinks(), outlinks)

    def test_get_inlinks__connect_1_inlink__returns_new_inlink(self):
        inlink = Link(0)
        self.device.connect_inlink(inlink)
        self.assertEqual(self.device.get_inlinks(), [inlink])

    def test_get_inlinks__connect_2_inlinks__returns_new_inlinks(self):
        inlink1 = Link(0)
        inlink2 = Link(0)
        self.device.connect_inlink(inlink1)
        self.device.connect_inlink(inlink2)
        self.assertEqual(self.device.get_inlinks(), [inlink1, inlink2])

    def test_get_inlinks__connect_2_inlinks_at_once__returns_new_inlinks(self):
        inlinks = [Link(0) for num_links in range(2)]
        self.device.connect_inlink_list(inlinks)
        self.assertEqual(self.device.get_inlinks(), inlinks)

    def test_get_inlinks__connect_3_inlinks__returns_new_inlinks(self):
        inlink1 = Link(0)
        inlink2 = Link(0)
        inlink3 = Link(0)
        self.device.connect_inlink(inlink1)
        self.device.connect_inlink(inlink2)
        self.device.connect_inlink(inlink3)
        self.assertEqual(self.device.get_inlinks(),
            [inlink1, inlink2, inlink3])

    def test_get_inlinks__connect_20_inlinks_at_once__returns_new_inlinks(self):
        inlinks = [Link(0) for num_links in range(20)]
        self.device.connect_inlink_list(inlinks)
        self.assertEqual(self.device.get_inlinks(), inlinks)

    def test_read_inlinks__put_message_on_1_inlink__returns_message(self):
        source = NetworkDevice("source")
        link = Link(0)
        self.device.connect_inlink(link)
        test_message = Message(source, [self.device], "test message")
        link.put_message(test_message)
        received_messages = self.device.read_inlinks()
        self.assertEqual(received_messages, [test_message])

    def test_read_inlinks__1_empty_inlink__returns_empty_list(self):
        source = NetworkDevice("source")
        inlink = Link(0)
        self.device.connect_inlink(inlink)
        received_messages = self.device.read_inlinks()
        self.assertEqual(received_messages, [])

    def test_read_inlinks__2_empty_inlinks__returns_empty_list(self):
        source = NetworkDevice("source")
        inlink1 = Link(0)
        inlink2 = Link(0)
        self.device.connect_inlink(inlink1)
        self.device.connect_inlink(inlink2)
        received_messages = self.device.read_inlinks()
        self.assertEqual(received_messages, [])

    def test_read_inlinks__put_same_message_on_2_inlinks__returns_messages(self):
        source = NetworkDevice("source")
        inlink1 = Link(0)
        inlink2 = Link(0)
        self.device.connect_inlink(inlink1)
        self.device.connect_inlink(inlink2)
        test_message = Message(source, [self.device], "test message")
        inlink1.put_message(test_message)
        inlink2.put_message(test_message)
        received_messages = self.device.read_inlinks()
        self.assertEqual(received_messages, [test_message, test_message])

    def test_read_inlinks__put_diff_message_on_2_inlinks__returns_messages(self):
        source = NetworkDevice("source")
        inlink1 = Link(0)
        inlink2 = Link(0)
        self.device.connect_inlink(inlink1)
        self.device.connect_inlink(inlink2)
        test_message1 = Message(source, [self.device], "test message1")
        test_message2 = Message(source, [self.device], "test message2")
        inlink1.put_message(test_message1)
        inlink2.put_message(test_message2)
        received_messages = self.device.read_inlinks()
        self.assertEqual(received_messages, [test_message1, test_message2])



if __name__ == '__main__':
    unittest.main()
