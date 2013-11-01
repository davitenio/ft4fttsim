# author: David Gessner <davidges@gmail.com>

import unittest
from mock import sentinel, Mock
from ft4fttsim.networking import *
from ft4fttsim.exceptions import FT4FTTSimException
import pytest


@pytest.mark.parametrize("megabits,propagation_delay", [
    # negative propagation delay raises exception
    (10, -1),
    # zero megabits per second raises exception
    (0, 1),
    # negative megabits per second raises exception
    (-1, 1),
    # negative megabits per second and negative propagation delay raises
    # exception
    (-5, -5),
])
def test_link_constructor_raises_exception(env, megabits, propagation_delay):
    with pytest.raises(FT4FTTSimException):
        Link(env, megabits, propagation_delay)


@pytest.mark.parametrize("megabits,propagation_delay", [
    # zero propagation delay does not raise an exception
    (10, 0),

    # example constructor parameters that should not raise an exception
    (1, 1),
    (5, 5),
    (100000, 100000),
    (0.00001, 0.00001),
    (0.00001, 100000),
    (100000, 0.00001),
])
def test_link_constructor_does_not_raise_exception(
        env, megabits, propagation_delay):
    try:
        Link(env, megabits, propagation_delay)
    except:
        assert False, "Link constructor should not raise exception."


class TestLink(unittest.TestCase):

    def setUp(self):
        self.env = simpy.Environment()
        self.link = Link(self.env, 10, 0)

    def test_get_end_point__link_created__end_point_is_None(self):
        self.assertEqual(self.link.end_point, None)


class TestNetworkDevice(unittest.TestCase):

    def setUp(self):
        self.env = simpy.Environment()
        self.device = NetworkDevice(self.env, "test device")

    def test_get_outlinks__new_device__returns_empty_list(self):
        self.assertEqual(self.device.outlinks, [])

    def test_get_inlinks__new_device__returns_empty_list(self):
        self.assertEqual(self.device.inlinks, [])

    def test_get_outlinks__connect_1_outlink__returns_new_outlink(self):
        outlink = Mock(spec_set=Link, name="outlink")
        self.device.connect_outlink(outlink)
        self.assertEqual(self.device.outlinks, [outlink])

    def test_get_outlinks__connect_2_outlinks__returns_new_outlinks(self):
        outlink1 = Mock(spec_set=Link, name="outlink 1")
        outlink2 = Mock(spec_set=Link, name="outlink 2")
        self.device.connect_outlink(outlink1)
        self.device.connect_outlink(outlink2)
        self.assertEqual(self.device.outlinks, [outlink1, outlink2])

    def test_get_outlinks__connect_outlink_list2__returns_new_outlinks(self):
        outlinks = [Mock(spec_set=Link, name="outlink " + str(i))
            for i in range(2)]
        self.device.connect_outlink_list(outlinks)
        self.assertEqual(self.device.outlinks, outlinks)

    def test_get_outlinks__connect_3_outlinks__returns_new_outlinks(self):
        outlink1 = Mock(spec_set=Link, name="outlink 1")
        outlink2 = Mock(spec_set=Link, name="outlink 2")
        outlink3 = Mock(spec_set=Link, name="outlink 2")
        self.device.connect_outlink(outlink1)
        self.device.connect_outlink(outlink2)
        self.device.connect_outlink(outlink3)
        self.assertEqual(self.device.outlinks,
            [outlink1, outlink2, outlink3])

    def test_get_outlinks__connect_outlink_list20__returns_new_outlinks(self):
        outlinks = [Mock(spec_set=Link, name="outlink " + str(i))
            for i in range(20)]
        self.device.connect_outlink_list(outlinks)
        self.assertEqual(self.device.outlinks, outlinks)

    def test_get_inlinks__connect_1_inlink__returns_new_inlink(self):
        inlink = Mock(spec_set=Link, name="inlink")
        self.device.connect_inlink(inlink)
        self.assertEqual(self.device.inlinks, [inlink])

    def test_get_inlinks__connect_2_inlinks__returns_new_inlinks(self):
        inlink1 = Mock(spec_set=Link, name="inlink 1")
        inlink2 = Mock(spec_set=Link, name="inlink 2")
        self.device.connect_inlink(inlink1)
        self.device.connect_inlink(inlink2)
        self.assertEqual(self.device.inlinks, [inlink1, inlink2])

    def test_get_inlinks__connect_2_inlinks_at_once__returns_new_inlinks(self):
        inlinks = [Mock(spec_set=Link, name="inlink " + str(i))
            for i in range(2)]
        self.device.connect_inlink_list(inlinks)
        self.assertEqual(self.device.inlinks, inlinks)

    def test_get_inlinks__connect_3_inlinks__returns_new_inlinks(self):
        inlink1 = Mock(spec_set=Link, name="inlink 1")
        inlink2 = Mock(spec_set=Link, name="inlink 2")
        inlink3 = Mock(spec_set=Link, name="inlink 3")
        self.device.connect_inlink(inlink1)
        self.device.connect_inlink(inlink2)
        self.device.connect_inlink(inlink3)
        self.assertEqual(self.device.inlinks,
            [inlink1, inlink2, inlink3])

    def test_get_inlinks__connect_inlink_list20__returns_new_inlinks(self):
        inlinks = [Mock(spec_set=Link, name="inlink " + str(i))
            for i in range(20)]
        self.device.connect_inlink_list(inlinks)
        self.assertEqual(self.device.inlinks, inlinks)

    def test_instruct_transmission__no_outlink__raise_exception(self):
        not_connected_outlink = sentinel.dummy_link
        self.assertRaises(FT4FTTSimException,
            self.device.instruct_transmission,
            sentinel.message, not_connected_outlink)


MINIMUM_ETHERNET_FRAME_SIZE = 64
MAXIMUM_ETHERNET_FRAME_SIZE = 1518


@pytest.mark.parametrize("size_in_bytes",
    # 64 is the minimum valid size in bytes
    [MINIMUM_ETHERNET_FRAME_SIZE,
    # 1518 is the maximum valid size in bytes
    MAXIMUM_ETHERNET_FRAME_SIZE] +
    # also test with a couple of values between the minimum and the
    # maximum size in bytes
    list(range(65, 1519, 404)))
def test_message_constructor_does_not_raise_exception(env,
        size_in_bytes):
    try:
        Message(env, sentinel.dummy_source, sentinel.dummy_destination,
            size_in_bytes, sentinel.dummy_type)
    except:
        assert False, "Message constructor should not raise exception."


@pytest.mark.parametrize("size_in_bytes", [
    -1000, -1, -0.9, 0, 0.5,
    MINIMUM_ETHERNET_FRAME_SIZE - 1,
    MINIMUM_ETHERNET_FRAME_SIZE + 0.5,
    MAXIMUM_ETHERNET_FRAME_SIZE - 9.1,
    MAXIMUM_ETHERNET_FRAME_SIZE + 1,
    10000
])
def test_message_constructor_raises_exception(env, size_in_bytes):
    with pytest.raises(FT4FTTSimException):
        Message(env, sentinel.dummy_source, sentinel.dummy_destination,
            size_in_bytes, sentinel.dummy_type)


class TestMessage(unittest.TestCase):

    def setUp(self):
        self.env = simpy.Environment()
        self.message = Message(self.env, sentinel.source,
            sentinel.destinations, Ethernet.MAX_FRAME_SIZE_BYTES,
            sentinel.message_type)

    def test_destination__message_created__returns_expected_dst(self):
        expected_destination = sentinel.destinations
        actual_destination = self.message.destination
        self.assertEqual(actual_destination, expected_destination)

    def test_get_source__message_created__returns_expected_source(self):
        expected_source = sentinel.source
        actual_source = self.message.source
        self.assertEqual(actual_source, expected_source)


class TestSwitch(unittest.TestCase):

    def setUp(self):
        self.env = simpy.Environment()
        self.switch = Switch(self.env, "switch under test")

    def test_forward_messages__no_outlinks__no_instruct_transmission(self):
        """
        If the switch does not have any outlinks, then the function
        instruct_transmission should not be called.
        """
        self.switch.instruct_transmission = Mock()
        message_list = [Message(self.env, sentinel.source,
            sentinel.destinations, Ethernet.MAX_FRAME_SIZE_BYTES,
            sentinel.message_type) for i in range(10)]
        self.switch.forward_messages(message_list)
        self.assertFalse(self.switch.instruct_transmission.called)


if __name__ == '__main__':
    unittest.main()
