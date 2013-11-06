# author: David Gessner <davidges@gmail.com>

import unittest
from mock import sentinel, Mock
from ft4fttsim.ethernet import Ethernet
from ft4fttsim.networking import *


class TestNetworkDeviceIntegration(unittest.TestCase):

    def setUp(self):
        self.env = simpy.Environment()
        self.device = NetworkDevice(self.env, "test device")

    def test_get_outlinks__connect_1_outlink__returns_new_outlink(self):
        outlink = Link(self.env, 10, 0)
        self.device.connect_outlink(outlink)
        assert self.device.outlinks == [outlink]

    def test_get_outlinks__connect_2_outlinks__returns_new_outlinks(self):
        outlink1 = Link(self.env, 10, 0)
        outlink2 = Link(self.env, 10, 0)
        self.device.connect_outlink(outlink1)
        self.device.connect_outlink(outlink2)
        assert self.device.outlinks == [outlink1, outlink2]

    def test_get_outlinks__connect_outlink_list_2__returns_new_outlinks(self):
        outlinks = [Link(self.env, 10, 0) for num_links in range(2)]
        self.device.connect_outlink_list(outlinks)
        assert self.device.outlinks == outlinks

    def test_get_outlinks__connect_3_outlinks__returns_new_outlinks(self):
        outlink1 = Link(self.env, 10, 0)
        outlink2 = Link(self.env, 10, 0)
        outlink3 = Link(self.env, 10, 0)
        self.device.connect_outlink(outlink1)
        self.device.connect_outlink(outlink2)
        self.device.connect_outlink(outlink3)
        assert self.device.outlinks == [outlink1, outlink2, outlink3]

    def test_get_outlinks__connect_outlink_list_20__returns_new_outlinks(self):
        outlinks = [Link(self.env, 10, 0) for num_links in range(20)]
        self.device.connect_outlink_list(outlinks)
        assert self.device.outlinks == outlinks

    def test_get_inlinks__connect_1_inlink__returns_new_inlink(self):
        inlink = Link(self.env, 10, 0)
        self.device.connect_inlink(inlink)
        assert self.device.inlinks == [inlink]

    def test_get_inlinks__connect_2_inlinks__returns_new_inlinks(self):
        inlink1 = Link(self.env, 10, 0)
        inlink2 = Link(self.env, 10, 0)
        self.device.connect_inlink(inlink1)
        self.device.connect_inlink(inlink2)
        assert self.device.inlinks == [inlink1, inlink2]

    def test_get_inlinks__connect_2_inlinks_at_once__returns_new_inlinks(self):
        inlinks = [Link(self.env, 10, 0) for num_links in range(2)]
        self.device.connect_inlink_list(inlinks)
        assert self.device.inlinks == inlinks

    def test_get_inlinks__connect_3_inlinks__returns_new_inlinks(self):
        inlink1 = Link(self.env, 10, 0)
        inlink2 = Link(self.env, 10, 0)
        inlink3 = Link(self.env, 10, 0)
        self.device.connect_inlink(inlink1)
        self.device.connect_inlink(inlink2)
        self.device.connect_inlink(inlink3)
        assert self.device.inlinks == [inlink1, inlink2, inlink3]

    def test_get_inlinks__connect_inlink_list_20__returns_new_inlinks(self):
        inlinks = [Link(self.env, 10, 0) for num_links in range(20)]
        self.device.connect_inlink_list(inlinks)
        assert self.device.inlinks == inlinks

    def test_read_inlinks__put_message_on_1_inlink__returns_message(self):
        link = Link(self.env, 10, 0)
        self.device.connect_inlink(link)
        test_message = Message(self.env, sentinel.dummy_source, [self.device],
            Ethernet.MAX_FRAME_SIZE_BYTES, "test message")
        link.message = test_message
        received_messages = yield self.device.receive_buffer.get()
        assert received_messages == [test_message]

    def test_read_inlinks__1_empty_inlink__returns_empty_list(self):
        inlink = Link(self.env, 10, 0)
        self.device.connect_inlink(inlink)
        received_messages = yield self.device.receive_buffer.get()
        assert received_messages == []


class TestNetworkDeviceWith2Inlinks(unittest.TestCase):

    def setUp(self):
        """
        Set up the following configuration:

                      +--------+
         inlink1 ---> |        |
                      | device |
         inlink2 ---> |        |
                      +--------+
        """
        self.env = simpy.Environment()
        self.device = NetworkDevice(self.env, "test device")
        self.inlink1 = Link(self.env, 10, 0)
        self.inlink2 = Link(self.env, 10, 0)
        self.device.connect_inlink(self.inlink1)
        self.device.connect_inlink(self.inlink2)

    def test_read_inlinks__2_empty_inlinks__returns_empty_list(self):
        received_messages = yield self.device.receive_buffer.get()
        assert received_messages == []

    def test_read_inlinks__put_message_on_2_inlinks__returns_messages(self):
        test_message = Message(self.env, sentinel.dummy_source, [self.device],
            Ethernet.MAX_FRAME_SIZE_BYTES, "test message")
        self.inlink1.message = test_message
        self.inlink2.message = test_message
        received_messages = yield self.device.receive_buffer.get()
        assert received_messages == [test_message, test_message]

    def test_read_inlinks__put_diff_msg_on_2_inlinks__returns_messages(self):
        test_message1 = Message(self.env, sentinel.dummy_source, [self.device],
            Ethernet.MAX_FRAME_SIZE_BYTES, "test message1")
        test_message2 = Message(self.env, sentinel.dummy_source, [self.device],
            Ethernet.MAX_FRAME_SIZE_BYTES, "test message2")
        self.inlink1.message = test_message1
        self.inlink2.message = test_message2
        received_messages = yield self.device.receive_buffer.get()
        assert received_messages == [test_message1, test_message2]

if __name__ == '__main__':
    unittest.main()
