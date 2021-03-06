# author: David Gessner <davidges@gmail.com>

from unittest.mock import sentinel, Mock

from ft4fttsim.networking import Switch, Message


def test_forward_messages__no_outlinks__no_instruct_transmission(env):
    """
    If the switch does not have any ports, then the function
    instruct_transmission should not be called.

    """
    switch = Switch(env, "switch", num_ports=0)
    switch.instruct_transmission = Mock()
    message_list = [
        Message(env, sentinel.source,
                sentinel.destinations, 1234,
                sentinel.message_type)
        for i in range(10)
    ]
    switch.forward_messages(message_list)
    assert switch.instruct_transmission.called is False
