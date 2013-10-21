# author: David Gessner <davidges@gmail.com>

import unittest
from ft4fttsim.ethernet import Ethernet
from ft4fttsim.networking import *


class TestLinkIntegration(unittest.TestCase):

    def setUp(self):
        self.link = Link(10, 0)

    def test_get_message__after_put_message__returns_same_message(self):
        source = NetworkDevice("source")
        source.connect_outlink(self.link)
        destination = NetworkDevice("destination")
        destination.connect_inlink(self.link)
        m = Message(source, [destination],
            Ethernet.MAX_FRAME_SIZE_BYTES, "test message")
        self.link.put_message(m)
        self.assertEqual(self.link.get_message(), m)


class TestNetworkDeviceIntegration(unittest.TestCase):

    def setUp(self):
        self.device = NetworkDevice("test device")

    def test_get_outlinks__connect_1_outlink__returns_new_outlink(self):
        outlink = Link(10, 0)
        self.device.connect_outlink(outlink)
        self.assertEqual(self.device.get_outlinks(), [outlink])

    def test_get_outlinks__connect_2_outlinks__returns_new_outlinks(self):
        outlink1 = Link(10, 0)
        outlink2 = Link(10, 0)
        self.device.connect_outlink(outlink1)
        self.device.connect_outlink(outlink2)
        self.assertEqual(self.device.get_outlinks(), [outlink1, outlink2])

    def test_get_outlinks__connect_outlink_list_2__returns_new_outlinks(self):
        outlinks = [Link(10, 0) for num_links in range(2)]
        self.device.connect_outlink_list(outlinks)
        self.assertEqual(self.device.get_outlinks(), outlinks)

    def test_get_outlinks__connect_3_outlinks__returns_new_outlinks(self):
        outlink1 = Link(10, 0)
        outlink2 = Link(10, 0)
        outlink3 = Link(10, 0)
        self.device.connect_outlink(outlink1)
        self.device.connect_outlink(outlink2)
        self.device.connect_outlink(outlink3)
        self.assertEqual(self.device.get_outlinks(),
            [outlink1, outlink2, outlink3])

    def test_get_outlinks__connect_outlink_list_20__returns_new_outlinks(self):
        outlinks = [Link(10, 0) for num_links in range(20)]
        self.device.connect_outlink_list(outlinks)
        self.assertEqual(self.device.get_outlinks(), outlinks)

    def test_get_inlinks__connect_1_inlink__returns_new_inlink(self):
        inlink = Link(10, 0)
        self.device.connect_inlink(inlink)
        self.assertEqual(self.device.get_inlinks(), [inlink])

    def test_get_inlinks__connect_2_inlinks__returns_new_inlinks(self):
        inlink1 = Link(10, 0)
        inlink2 = Link(10, 0)
        self.device.connect_inlink(inlink1)
        self.device.connect_inlink(inlink2)
        self.assertEqual(self.device.get_inlinks(), [inlink1, inlink2])

    def test_get_inlinks__connect_2_inlinks_at_once__returns_new_inlinks(self):
        inlinks = [Link(10, 0) for num_links in range(2)]
        self.device.connect_inlink_list(inlinks)
        self.assertEqual(self.device.get_inlinks(), inlinks)

    def test_get_inlinks__connect_3_inlinks__returns_new_inlinks(self):
        inlink1 = Link(10, 0)
        inlink2 = Link(10, 0)
        inlink3 = Link(10, 0)
        self.device.connect_inlink(inlink1)
        self.device.connect_inlink(inlink2)
        self.device.connect_inlink(inlink3)
        self.assertEqual(self.device.get_inlinks(),
            [inlink1, inlink2, inlink3])

    def test_get_inlinks__connect_inlink_list_20__returns_new_inlinks(self):
        inlinks = [Link(10, 0) for num_links in range(20)]
        self.device.connect_inlink_list(inlinks)
        self.assertEqual(self.device.get_inlinks(), inlinks)

    def test_read_inlinks__put_message_on_1_inlink__returns_message(self):
        source = NetworkDevice("source")
        link = Link(10, 0)
        self.device.connect_inlink(link)
        test_message = Message(source, [self.device],
            Ethernet.MAX_FRAME_SIZE_BYTES, "test message")
        link.put_message(test_message)
        received_messages = self.device.read_inlinks()
        self.assertEqual(received_messages, [test_message])

    def test_read_inlinks__1_empty_inlink__returns_empty_list(self):
        source = NetworkDevice("source")
        inlink = Link(10, 0)
        self.device.connect_inlink(inlink)
        received_messages = self.device.read_inlinks()
        self.assertEqual(received_messages, [])

    def test_read_inlinks__2_empty_inlinks__returns_empty_list(self):
        source = NetworkDevice("source")
        inlink1 = Link(10, 0)
        inlink2 = Link(10, 0)
        self.device.connect_inlink(inlink1)
        self.device.connect_inlink(inlink2)
        received_messages = self.device.read_inlinks()
        self.assertEqual(received_messages, [])

    def test_read_inlinks__put_message_on_2_inlinks__returns_messages(self):
        source = NetworkDevice("source")
        inlink1 = Link(10, 0)
        inlink2 = Link(10, 0)
        self.device.connect_inlink(inlink1)
        self.device.connect_inlink(inlink2)
        test_message = Message(source, [self.device],
            Ethernet.MAX_FRAME_SIZE_BYTES, "test message")
        inlink1.put_message(test_message)
        inlink2.put_message(test_message)
        received_messages = self.device.read_inlinks()
        self.assertEqual(received_messages, [test_message, test_message])

    def test_read_inlinks__put_diff_msg_on_2_inlinks__returns_messages(self):
        source = NetworkDevice("source")
        inlink1 = Link(10, 0)
        inlink2 = Link(10, 0)
        self.device.connect_inlink(inlink1)
        self.device.connect_inlink(inlink2)
        test_message1 = Message(source, [self.device],
            Ethernet.MAX_FRAME_SIZE_BYTES, "test message1")
        test_message2 = Message(source, [self.device],
            Ethernet.MAX_FRAME_SIZE_BYTES, "test message2")
        inlink1.put_message(test_message1)
        inlink2.put_message(test_message2)
        received_messages = self.device.read_inlinks()
        self.assertEqual(received_messages, [test_message1, test_message2])


if __name__ == '__main__':
    unittest.main()
