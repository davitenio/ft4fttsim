# author: David Gessner <davidges@gmail.com>

import unittest
from mock import sentinel, Mock
from ft4fttsim.networking import *
from ft4fttsim.exceptions import FT4FTTSimException
import pytest


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
