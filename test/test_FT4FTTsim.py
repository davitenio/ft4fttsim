# author: David Gessner <davidges@gmail.com>

import unittest
from FT4FTTSim import *

logging.disable(logging.CRITICAL)

class TestLink(unittest.TestCase):

    def setUp(self):
        self.source = NetworkComponent("source")
        self.destination = NetworkComponent("destination")
        self.link = Link(self.source, self.destination, 0)

    def test_get_end_point__link_created__end_point_is_correct(self):
        self.assertEqual(self.link.get_end_point(), self.destination)

    def test_has_message__new_link__returns_false(self):
        self.assertFalse(self.link.has_message())

    def test_get_message__after_put_message__returns_same_message(self):
        m = Message(self.source, [self.destination], "test message")
        self.link.put_message(m)
        self.assertEqual(self.link.get_message(), m)

    def test_get_message__new_link__returns_none(self):
        self.assertEqual(self.link.get_message(), None)


class TestNetworkComponent(unittest.TestCase):

    def setUp(self):
        self.component = NetworkComponent("test component")

    def test_get_outlinks__new_component__returns_empty_list(self):
        self.assertEqual(self.component.get_outlinks(), [])

    def test_get_inlinks__new_component__returns_empty_list(self):
        self.assertEqual(self.component.get_inlinks(), [])

    def test_get_outlinks__connected_1_outlink__returns_new_outlink(self):
        outlink = Link(self.component, NetworkComponent("destination"), 0)
        self.component.connect_outlink(outlink)
        self.assertEqual(self.component.get_outlinks(), [outlink])

    def test_get_outlinks__connected_2_outlinks__returns_new_outlinks(self):
        outlink1 = Link(self.component, NetworkComponent("destination1"), 0)
        outlink2 = Link(self.component, NetworkComponent("destination2"), 0)
        self.component.connect_outlink(outlink1)
        self.component.connect_outlink(outlink2)
        self.assertEqual(self.component.get_outlinks(), [outlink1, outlink2])

    def test_get_outlinks__connected_3_outlinks__returns_new_outlinks(self):
        outlink1 = Link(self.component, NetworkComponent("destination1"), 0)
        outlink2 = Link(self.component, NetworkComponent("destination2"), 0)
        outlink3 = Link(self.component, NetworkComponent("destination3"), 0)
        self.component.connect_outlink(outlink1)
        self.component.connect_outlink(outlink2)
        self.component.connect_outlink(outlink3)
        self.assertEqual(self.component.get_outlinks(),
            [outlink1, outlink2, outlink3])

    def test_get_inlinks__connected_1_inlink__returns_new_inlink(self):
        inlink = Link(NetworkComponent("source"), self.component, 0)
        self.component.connect_inlink(inlink)
        self.assertEqual(self.component.get_inlinks(), [inlink])

    def test_get_inlinks__connected_2_inlinks__returns_new_inlinks(self):
        inlink1 = Link(NetworkComponent("source1"), self.component, 0)
        inlink2 = Link(NetworkComponent("source2"), self.component, 0)
        self.component.connect_inlink(inlink1)
        self.component.connect_inlink(inlink2)
        self.assertEqual(self.component.get_inlinks(), [inlink1, inlink2])

    def test_get_inlinks__connected_3_inlinks__returns_new_inlinks(self):
        inlink1 = Link(NetworkComponent("source1"), self.component, 0)
        inlink2 = Link(NetworkComponent("source2"), self.component, 0)
        inlink3 = Link(NetworkComponent("source3"), self.component, 0)
        self.component.connect_inlink(inlink1)
        self.component.connect_inlink(inlink2)
        self.component.connect_inlink(inlink3)
        self.assertEqual(self.component.get_inlinks(),
            [inlink1, inlink2, inlink3])

    def test_read_inlinks__put_message_on_1_inlink__returns_message(self):
        source = NetworkComponent("source")
        inlink = Link(source, self.component, 0)
        self.component.connect_inlink(inlink)
        test_message = Message(source, [self.component], "test message")
        inlink.put_message(test_message)
        received_messages = self.component.read_inlinks()
        self.assertEqual(received_messages, [test_message])

    def test_read_inlinks__1_empty_inlink__returns_empty_list(self):
        source = NetworkComponent("source")
        inlink = Link(source, self.component, 0)
        self.component.connect_inlink(inlink)
        received_messages = self.component.read_inlinks()
        self.assertEqual(received_messages, [])

    def test_read_inlinks__2_empty_inlinks__returns_empty_list(self):
        source = NetworkComponent("source")
        inlink1 = Link(source, self.component, 0)
        inlink2 = Link(source, self.component, 0)
        self.component.connect_inlink(inlink1)
        self.component.connect_inlink(inlink2)
        received_messages = self.component.read_inlinks()
        self.assertEqual(received_messages, [])

    def test_read_inlinks__put_same_message_on_2_inlinks__returns_messages(self):
        source = NetworkComponent("source")
        inlink1 = Link(source, self.component, 0)
        inlink2 = Link(source, self.component, 0)
        self.component.connect_inlink(inlink1)
        self.component.connect_inlink(inlink2)
        test_message = Message(source, [self.component], "test message")
        inlink1.put_message(test_message)
        inlink2.put_message(test_message)
        received_messages = self.component.read_inlinks()
        self.assertEqual(received_messages, [test_message, test_message])

    def test_read_inlinks__put_diff_message_on_2_inlinks__returns_messages(self):
        source = NetworkComponent("source")
        inlink1 = Link(source, self.component, 0)
        inlink2 = Link(source, self.component, 0)
        self.component.connect_inlink(inlink1)
        self.component.connect_inlink(inlink2)
        test_message1 = Message(source, [self.component], "test message1")
        test_message2 = Message(source, [self.component], "test message2")
        inlink1.put_message(test_message1)
        inlink2.put_message(test_message2)
        received_messages = self.component.read_inlinks()
        self.assertEqual(received_messages, [test_message1, test_message2])



if __name__ == '__main__':
    unittest.main()
