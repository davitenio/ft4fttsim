# author: David Gessner <davidges@gmail.com>

from unittest.mock import sentinel, Mock
from ft4fttsim.networking import Switch, Message
from ft4fttsim.ethernet import Ethernet
import pytest


def test_forward_messages__no_outlinks__no_instruct_transmission(env, switch):
    """
    If the switch does not have any outlinks, then the function
    instruct_transmission should not be called.
    """
    switch.instruct_transmission = Mock()
    message_list = [
        Message(env, sentinel.source,
                sentinel.destinations, Ethernet.MAX_FRAME_SIZE_BYTES,
                sentinel.message_type)
        for i in range(10)
    ]
    switch.forward_messages(message_list)
    assert switch.instruct_transmission.called is False
