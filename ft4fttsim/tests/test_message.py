# author: David Gessner <davidges@gmail.com>

import pytest
from ft4fttsim.networking import Message
from ft4fttsim.exceptions import FT4FTTSimException
from unittest.mock import sentinel, Mock
from ft4fttsim.ethernet import Ethernet


MINIMUM_ETHERNET_FRAME_SIZE = 64
MAXIMUM_ETHERNET_FRAME_SIZE = 1518


@pytest.mark.parametrize(
    "size_in_bytes",
    [
        # 64 is the minimum valid size in bytes
        MINIMUM_ETHERNET_FRAME_SIZE,
        # 1518 is the maximum valid size in bytes
        MAXIMUM_ETHERNET_FRAME_SIZE
    ] +
    # also test with a couple of values between the minimum and the
    # maximum size in bytes
    list(range(65, 1519, 404))
)
def test_message_constructor_does_not_raise_exception(
        env, size_in_bytes):
    try:
        Message(env, sentinel.dummy_source, sentinel.dummy_destination,
                size_in_bytes, sentinel.dummy_type)
    except:
        assert False, "Message constructor should not raise exception."


@pytest.mark.parametrize(
    "size_in_bytes",
    [
        -1000, -1, -0.9, 0, 0.5,
        MINIMUM_ETHERNET_FRAME_SIZE - 1,
        MINIMUM_ETHERNET_FRAME_SIZE + 0.5,
        MAXIMUM_ETHERNET_FRAME_SIZE - 9.1,
        MAXIMUM_ETHERNET_FRAME_SIZE + 1,
        10000
    ]
)
def test_message_constructor_raises_exception(env, size_in_bytes):
    with pytest.raises(FT4FTTSimException):
        Message(env, sentinel.dummy_source, sentinel.dummy_destination,
                size_in_bytes, sentinel.dummy_type)


def test_message_created__returns_expected_destination(env):
    message = Message(env, sentinel.source, sentinel.destinations,
                      Ethernet.MAX_FRAME_SIZE_BYTES, sentinel.message_type)
    assert message.destination == sentinel.destinations


def test_message_created__returns_expected_source(env):
    message = Message(env, sentinel.source, sentinel.destinations,
                      Ethernet.MAX_FRAME_SIZE_BYTES, sentinel.message_type)
    assert message.source == sentinel.source
