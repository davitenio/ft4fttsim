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
    # Creating a message should not raise any exception or cause errors.
    Message(env, sentinel.dummy_source, sentinel.dummy_destination,
            size_in_bytes, sentinel.dummy_type)


def test_message_constructor_with_data_does_not_raise_exception(env):
    # Creating a message should not raise any exception or cause errors.
    Message(env, sentinel.dummy_source, sentinel.dummy_destination,
            1111, sentinel.dummy_type, sentinel.dummy_data)


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
    """
    Test that creating a message with invalid size raises an exception.

    """
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


def test_messages_with_same_data_are_equal(env):
    message1 = Message(env, sentinel.source, sentinel.destinations,
                       Ethernet.MAX_FRAME_SIZE_BYTES, sentinel.message_type,
                       sentinel.dummy_data)
    message2 = Message(env, sentinel.source, sentinel.destinations,
                       Ethernet.MAX_FRAME_SIZE_BYTES, sentinel.message_type,
                       sentinel.dummy_data)
    assert message1 == message2


def test_messages_with_different_data_are_not_equal(env):
    message1 = Message(env, sentinel.source, sentinel.destinations,
                       Ethernet.MAX_FRAME_SIZE_BYTES, sentinel.message_type,
                       sentinel.dummy_data)
    message2 = Message(env, sentinel.source, sentinel.destinations,
                       Ethernet.MAX_FRAME_SIZE_BYTES, sentinel.message_type,
                       sentinel.different_dummy_data)
    assert message1 != message2


def test_creating_message_from_template_creates_equal_message(env):
    template_message = Message(
        env, sentinel.source, sentinel.destinations,
        Ethernet.MAX_FRAME_SIZE_BYTES, sentinel.message_type,
        sentinel.dummy_data)
    new_message = Message.from_message(template_message)
    assert template_message == new_message
