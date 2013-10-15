# author: David Gessner <davidges@gmail.com>

import unittest
from mock import sentinel, Mock
from ft4fttsim.networking import *


class TestLink(unittest.TestCase):

    def setUp(self):
        self.link = Link(0)

    def test_get_end_point__link_created__end_point_is_None(self):
        self.assertEqual(self.link.get_end_point(), None)

    def test_has_message__link_created__returns_false(self):
        self.assertFalse(self.link.has_message())

    def test_get_message__after_put_message__returns_same_message(self):
        self.link.put_message(sentinel.dummy_message)
        self.assertEqual(self.link.get_message(), sentinel.dummy_message)

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
        outlink = Mock(name="outlink")
        self.device.connect_outlink(outlink)
        self.assertEqual(self.device.get_outlinks(), [outlink])

    def test_get_outlinks__connect_2_outlinks__returns_new_outlinks(self):
        outlink1 = Mock(name="outlink 1")
        outlink2 = Mock(name="outlink 2")
        self.device.connect_outlink(outlink1)
        self.device.connect_outlink(outlink2)
        self.assertEqual(self.device.get_outlinks(), [outlink1, outlink2])

    def test_get_outlinks__connect_outlink_list2__returns_new_outlinks(self):
        outlinks = [Mock(name="outlink " + str(i)) for i in range(2)]
        self.device.connect_outlink_list(outlinks)
        self.assertEqual(self.device.get_outlinks(), outlinks)

    def test_get_outlinks__connect_3_outlinks__returns_new_outlinks(self):
        outlink1 = Mock(name="outlink 1")
        outlink2 = Mock(name="outlink 2")
        outlink3 = Mock(name="outlink 2")
        self.device.connect_outlink(outlink1)
        self.device.connect_outlink(outlink2)
        self.device.connect_outlink(outlink3)
        self.assertEqual(self.device.get_outlinks(),
            [outlink1, outlink2, outlink3])

    def test_get_outlinks__connect_outlink_list20__returns_new_outlinks(self):
        outlinks = [Mock(name="outlink " + str(i)) for i in range(20)]
        self.device.connect_outlink_list(outlinks)
        self.assertEqual(self.device.get_outlinks(), outlinks)

    def test_get_inlinks__connect_1_inlink__returns_new_inlink(self):
        inlink = Mock(name="inlink")
        self.device.connect_inlink(inlink)
        self.assertEqual(self.device.get_inlinks(), [inlink])

    def test_get_inlinks__connect_2_inlinks__returns_new_inlinks(self):
        inlink1 = Mock(name="inlink 1")
        inlink2 = Mock(name="inlink 2")
        self.device.connect_inlink(inlink1)
        self.device.connect_inlink(inlink2)
        self.assertEqual(self.device.get_inlinks(), [inlink1, inlink2])

    def test_get_inlinks__connect_2_inlinks_at_once__returns_new_inlinks(self):
        inlinks = [Mock(name="inlink " + str(i)) for i in range(2)]
        self.device.connect_inlink_list(inlinks)
        self.assertEqual(self.device.get_inlinks(), inlinks)

    def test_get_inlinks__connect_3_inlinks__returns_new_inlinks(self):
        inlink1 = Mock(name="inlink 1")
        inlink2 = Mock(name="inlink 2")
        inlink3 = Mock(name="inlink 3")
        self.device.connect_inlink(inlink1)
        self.device.connect_inlink(inlink2)
        self.device.connect_inlink(inlink3)
        self.assertEqual(self.device.get_inlinks(),
            [inlink1, inlink2, inlink3])

    def test_get_inlinks__connect_inlink_list20__returns_new_inlinks(self):
        inlinks = [Mock(name="inlink " + str(i)) for i in range(20)]
        self.device.connect_inlink_list(inlinks)
        self.assertEqual(self.device.get_inlinks(), inlinks)

    def test_read_inlinks__put_message_on_1_inlink__returns_message(self):
        link = Mock()
        link.get_message.return_value = sentinel.dummy_message
        self.device.connect_inlink(link)
        received_messages = self.device.read_inlinks()
        self.assertEqual(received_messages, [sentinel.dummy_message])

    def test_read_inlinks__put_message_on_2_inlinks__returns_messages(self):
        inlink1 = Mock()
        inlink1.get_message.return_value = sentinel.dummy_message1
        inlink2 = Mock()
        inlink2.get_message.return_value = sentinel.dummy_message2
        self.device.connect_inlink(inlink1)
        self.device.connect_inlink(inlink2)
        received_messages = self.device.read_inlinks()
        self.assertEqual(received_messages,
            [sentinel.dummy_message1, sentinel.dummy_message2])

    def test_read_inlinks__1_empty_inlink__returns_empty_list(self):
        inlink = Mock(name="inlink")
        inlink.has_message.return_value = False
        self.device.connect_inlink(inlink)
        received_messages = self.device.read_inlinks()
        self.assertEqual(received_messages, [])

    def test_read_inlinks__2_empty_inlinks__returns_empty_list(self):
        inlink1 = Mock(name="inlink1")
        inlink1.has_message.return_value = False
        inlink2 = Mock(name="inlink2")
        inlink2.has_message.return_value = False
        self.device.connect_inlink(inlink1)
        self.device.connect_inlink(inlink2)
        received_messages = self.device.read_inlinks()
        self.assertEqual(received_messages, [])


class TestMessage(unittest.TestCase):

    def setUp(self):
        self.message = Message(sentinel.source, sentinel.destinations,
            sentinel.message_type)

    def test_get_destination_list__message_created__returns_expected_dst(self):
        expected_destination = sentinel.destinations
        actual_destination = self.message.get_destination_list()
        self.assertEqual(actual_destination, expected_destination)

    def test_get_source__message_created__returns_expected_source(self):
        expected_source = sentinel.source
        actual_source = self.message.get_source()
        self.assertEqual(actual_source, expected_source)


if __name__ == '__main__':
    unittest.main()
