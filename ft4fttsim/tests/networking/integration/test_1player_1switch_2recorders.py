# author: David Gessner <davidges@gmail.com>
"""
Perform tests under the following network:

                 +--------+ link1  +-----------+
                 |        1 -----> 0 recorder1 |
+--------+ link0 |        |        +-----------+
| player 0 ----> 0 switch |
+--------+       |        | link2  +-----------+
                 |        2 -----> 0 recorder2 |
                 +--------+        +-----------+

"""

import pytest

from ft4fttsim.tests.networking.fixturehelper import make_link


@pytest.fixture
def switch_pr1(env, player_rec1, recorder1, recorder2):
    from ft4fttsim.networking import Switch
    new_switch = Switch(env, "switch3", num_ports=3)
    make_link((1000, 123), env, player_rec1.ports[0], new_switch.ports[0])
    make_link((1000, 123), env, recorder1.ports[0], new_switch.ports[1])
    make_link((1000, 123), env, recorder2.ports[0], new_switch.ports[2])
    new_switch.forwarding_table = {
        player_rec1: set([new_switch.ports[0]]),
        recorder1: set([new_switch.ports[1]]),
        recorder2: set([new_switch.ports[2]]),
    }
    return new_switch


@pytest.mark.usefixtures("switch_pr1")
def test_messages_are_received_by_recorder1(
        env, player_rec1, recorder1):
    """
    Test that recorder1 receives messages.

    """
    env.run(until=float("inf"))
    received_messages = recorder1.recorded_messages
    assert player_rec1.messages_to_transmit == received_messages


@pytest.mark.usefixtures("switch_pr1")
def test_no_message_is_received_by_recorder2(
        env, player_rec1, recorder2):
    """
    Test that recorder2 does not receive any message.

    """
    env.run(until=float("inf"))
    received_messages = recorder2.recorded_messages
    assert len(received_messages) == 0


@pytest.fixture
def switch_pr2(env, player_rec2, recorder1, recorder2):
    from ft4fttsim.networking import Switch
    new_switch = Switch(env, "switch3", num_ports=3)
    make_link((1000, 123), env, player_rec2.ports[0], new_switch.ports[0])
    make_link((1000, 123), env, recorder1.ports[0], new_switch.ports[1])
    make_link((1000, 123), env, recorder2.ports[0], new_switch.ports[2])
    new_switch.forwarding_table = {
        player_rec2: set([new_switch.ports[0]]),
        recorder1: set([new_switch.ports[1]]),
        recorder2: set([new_switch.ports[2]]),
    }
    return new_switch


@pytest.mark.usefixtures("switch_pr2")
def test_messages_are_received_by_recorder2(
        env, player_rec2, recorder2):
    """
    Test that recorder2 receives messages.

    """
    env.run(until=float("inf"))
    received_messages = recorder2.recorded_messages
    assert player_rec2.messages_to_transmit == received_messages


@pytest.mark.usefixtures("switch_pr2")
def test_no_message_is_received_by_recorder1(
        env, player_rec2, recorder1):
    """
    Test that recorder1 does not receive any message.

    """
    env.run(until=float("inf"))
    received_messages = recorder1.recorded_messages
    assert len(received_messages) == 0


@pytest.fixture
def switch_pr12(env, player_rec12, recorder1, recorder2):
    from ft4fttsim.networking import Switch
    new_switch = Switch(env, "switch3", num_ports=3)
    make_link((1000, 123), env, player_rec12.ports[0], new_switch.ports[0])
    make_link((1000, 123), env, recorder1.ports[0], new_switch.ports[1])
    make_link((1000, 123), env, recorder2.ports[0], new_switch.ports[2])
    new_switch.forwarding_table = {
        player_rec12: set([new_switch.ports[0]]),
        recorder1: set([new_switch.ports[1]]),
        recorder2: set([new_switch.ports[2]]),
    }
    return new_switch


@pytest.mark.usefixtures("switch_pr12")
def test_multicast_messages_are_received_by_recorder1(
        env, player_rec12, recorder1):
    """
    Test that recorder1 receives multicast messages.

    """
    env.run(until=float("inf"))
    received_messages = recorder1.recorded_messages
    assert player_rec12.messages_to_transmit == received_messages


@pytest.mark.usefixtures("switch_pr12")
def test_multicast_messages_are_received_by_recorder2(
        env, player_rec12, recorder2):
    """
    Test that recorder2 receives multicast messages.

    """
    env.run(until=float("inf"))
    received_messages = recorder2.recorded_messages
    assert player_rec12.messages_to_transmit == received_messages
