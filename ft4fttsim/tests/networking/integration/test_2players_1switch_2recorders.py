# author: David Gessner <davidges@gmail.com>
"""
Execute tests under the following network:

                    +---------+ link_r1  +-----------+
                    |         1 -------> 0 recorder1 |
+---------+ link_p1 |         |          +-----------+
| player1 0 ------> 0 switch4 |
+---------+         |         | link_r2  +-----------+
                    |         2 -------> 0 recorder2 |
                    +---3-----+          +-----------+
                        ^
                        | link_p2
                   +----0----+
                   | player2 |
                   +---------+

"""

import pytest
from ft4fttsim.tests.networking.fixturehelper import make_link


@pytest.fixture
def switch4(env):
    from ft4fttsim.networking import Switch
    return Switch(env, "switch4", num_ports=4)


@pytest.fixture
def switch_p1r1_p2r2(env, player_rec1, player2_rec2, recorder1, recorder2):
    from ft4fttsim.networking import Switch
    new_switch = Switch(env, "switch4", num_ports=4)
    make_link((1000, 123), env, player_rec1.ports[0], new_switch.ports[0])
    make_link((1000, 123), env, recorder1.ports[0], new_switch.ports[1])
    make_link((1000, 123), env, recorder2.ports[0], new_switch.ports[2])
    make_link((1000, 123), env, player2_rec2.ports[0], new_switch.ports[3])
    new_switch.forwarding_table = {
        player_rec1: set([new_switch.ports[0]]),
        recorder1: set([new_switch.ports[1]]),
        recorder2: set([new_switch.ports[2]]),
        player2_rec2: set([new_switch.ports[3]]),
    }
    return new_switch


@pytest.mark.usefixtures("switch_p1r1_p2r2")
def test_recorder1_receives_messages_from_player_rec1(
        env, player_rec1, recorder1):
    """
    Test recorder1 receives only the messages from player_rec1.
    """
    env.run(until=float("inf"))
    received_messages = recorder1.recorded_messages
    assert player_rec1.messages_to_transmit == received_messages


@pytest.mark.usefixtures("switch_p1r1_p2r2")
def test_recorder2_does_not_receive_messages_from_player_rec1(
        env, player_rec1, recorder2):
    """
    Test recorder2 does not receive the messages from player_rec1.
    """
    env.run(until=float("inf"))
    received_messages = recorder2.recorded_messages
    assert all(
        message not in player_rec1.messages_to_transmit
        for message in received_messages)


@pytest.mark.usefixtures("switch_p1r1_p2r2")
def test_recorder2_receives_messages_from_player2_rec2(
        env, player2_rec2, recorder2):
    """
    Test recorder2 receives only the messages from player2_rec2.
    """
    env.run(until=float("inf"))
    received_messages = recorder2.recorded_messages
    assert player2_rec2.messages_to_transmit == received_messages


@pytest.mark.usefixtures("switch_p1r1_p2r2")
def test_recorder1_does_not_receive_messages_from_player2_rec2(
        env, player2_rec2, recorder1):
    """
    Test recorder1 does not receive the messages from player2_rec2.
    """
    env.run(until=float("inf"))
    received_messages = recorder1.recorded_messages
    assert all(
        message not in player2_rec2.messages_to_transmit
        for message in received_messages)


##########################################################


@pytest.fixture
def switch_p1r1_p2r1(env, player_rec1, player2_rec1, recorder1, recorder2):
    from ft4fttsim.networking import Switch
    new_switch = Switch(env, "switch4", num_ports=4)
    make_link((1000, 123), env, player_rec1.ports[0], new_switch.ports[0])
    make_link((1000, 123), env, recorder1.ports[0], new_switch.ports[1])
    make_link((1000, 123), env, recorder2.ports[0], new_switch.ports[2])
    make_link((1000, 123), env, player2_rec1.ports[0], new_switch.ports[3])
    new_switch.forwarding_table = {
        player_rec1: set([new_switch.ports[0]]),
        recorder1: set([new_switch.ports[1]]),
        recorder2: set([new_switch.ports[2]]),
        player2_rec1: set([new_switch.ports[3]]),
    }
    return new_switch


@pytest.mark.usefixtures("switch_p1r1_p2r1")
def test_recorder1_receives_all_messages_from_player_rec1(
        env, player_rec1, recorder1):
    """
    Test recorder1 receives all messages from player_rec1.
    """
    env.run(until=float("inf"))
    received_messages = recorder1.recorded_messages
    assert all(
        message in received_messages
        for message in player_rec1.messages_to_transmit
    )


@pytest.mark.usefixtures("switch_p1r1_p2r1")
def test_recorder2_receives_exactly_0_messages(
        env, recorder2):
    """
    Test recorder2 receives exactly zero messages.
    """
    env.run(until=float("inf"))
    received_messages = recorder2.recorded_messages
    assert len(received_messages) == 0


@pytest.mark.usefixtures("switch_p1r1_p2r1")
def test_recorder1_receives_all_messages_from_player2_rec1(
        env, player2_rec1, recorder1):
    """
    Test recorder1 receives all messages from player2_rec1.
    """
    env.run(until=float("inf"))
    received_messages = recorder1.recorded_messages
    assert all(
        message in received_messages
        for message in player2_rec1.messages_to_transmit
    )
