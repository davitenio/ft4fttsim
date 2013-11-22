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
from ft4fttsim.tests.networking.fixturehelper import PLAYBACK_CONFIGS
from ft4fttsim.tests.networking.fixturehelper import make_playback_device
from ft4fttsim.tests.networking.fixturehelper import make_link


@pytest.fixture
def switch4(env):
    from ft4fttsim.networking import Switch
    return Switch(env, "switch4", num_ports=4)


@pytest.fixture
def recorder1(env):
    from ft4fttsim.networking import MessageRecordingDevice
    recorder = MessageRecordingDevice(env, "recorder1", 1)
    return recorder


@pytest.fixture
def recorder2(env):
    from ft4fttsim.networking import MessageRecordingDevice
    recorder = MessageRecordingDevice(env, "recorder2", 1)
    return recorder


@pytest.fixture(params=PLAYBACK_CONFIGS)
def player1_r1(request, env, recorder1):
    """
    Create a message playback device that sends messages to recorder 1 only.

    """
    config = request.param
    new_playback_device = make_playback_device(
        config, env, recorder1, name="player1")
    return new_playback_device


@pytest.fixture(params=PLAYBACK_CONFIGS)
def player2_r2(request, env, recorder2):
    """
    Create a message playback device that sends messages to recorder 2 only.

    """
    config = request.param
    new_playback_device = make_playback_device(
        config, env, recorder2, name="player2")
    return new_playback_device


@pytest.fixture
def switch_p1r1_p2r2(env, player1_r1, player2_r2, recorder1, recorder2):
    from ft4fttsim.networking import Switch
    new_switch = Switch(env, "switch4", num_ports=4)
    make_link((1000, 123), env, player1_r1.ports[0], new_switch.ports[0])
    make_link((1000, 123), env, recorder1.ports[0], new_switch.ports[1])
    make_link((1000, 123), env, recorder2.ports[0], new_switch.ports[2])
    make_link((1000, 123), env, player2_r2.ports[0], new_switch.ports[3])
    new_switch.forwarding_table = {
        player1_r1: set([new_switch.ports[0]]),
        recorder1: set([new_switch.ports[1]]),
        recorder2: set([new_switch.ports[2]]),
        player2_r2: set([new_switch.ports[3]]),
    }
    return new_switch


@pytest.mark.usefixtures("switch_p1r1_p2r2")
def test_recorder1_receives_messages_from_player1_r1(
        env, player1_r1, recorder1):
    """
    Test recorder1 receives only the messages from player1_r1.
    """
    env.run(until=float("inf"))
    received_messages = recorder1.recorded_messages
    assert player1_r1.messages_to_transmit == received_messages


@pytest.mark.usefixtures("switch_p1r1_p2r2")
def test_recorder2_does_not_receive_messages_from_player1_r1(
        env, player1_r1, recorder2):
    """
    Test recorder2 does not receive the messages from player1_r1.
    """
    env.run(until=float("inf"))
    received_messages = recorder2.recorded_messages
    assert all(
        message not in player1_r1.messages_to_transmit
        for message in received_messages)


@pytest.mark.usefixtures("switch_p1r1_p2r2")
def test_recorder2_receives_messages_from_player2_r2(
        env, player2_r2, recorder2):
    """
    Test recorder2 receives only the messages from player2_r2.
    """
    env.run(until=float("inf"))
    received_messages = recorder2.recorded_messages
    assert player2_r2.messages_to_transmit == received_messages


@pytest.mark.usefixtures("switch_p1r1_p2r2")
def test_recorder1_does_not_receive_messages_from_player2_r2(
        env, player2_r2, recorder1):
    """
    Test recorder1 does not receive the messages from player2_r2.
    """
    env.run(until=float("inf"))
    received_messages = recorder1.recorded_messages
    assert all(
        message not in player2_r2.messages_to_transmit
        for message in received_messages)


##########################################################


@pytest.fixture(params=PLAYBACK_CONFIGS)
def player2_r1(request, env, recorder1):
    """
    Create a second message playback device that sends messages to recorder 1
    only.

    """
    config = request.param
    new_playback_device = make_playback_device(
        config, env, recorder1, name="player2")
    return new_playback_device


@pytest.fixture
def switch_p1r1_p2r1(env, player1_r1, player2_r1, recorder1, recorder2):
    from ft4fttsim.networking import Switch
    new_switch = Switch(env, "switch4", num_ports=4)
    make_link((1000, 123), env, player1_r1.ports[0], new_switch.ports[0])
    make_link((1000, 123), env, recorder1.ports[0], new_switch.ports[1])
    make_link((1000, 123), env, recorder2.ports[0], new_switch.ports[2])
    make_link((1000, 123), env, player2_r1.ports[0], new_switch.ports[3])
    new_switch.forwarding_table = {
        player1_r1: set([new_switch.ports[0]]),
        recorder1: set([new_switch.ports[1]]),
        recorder2: set([new_switch.ports[2]]),
        player2_r1: set([new_switch.ports[3]]),
    }
    return new_switch


@pytest.mark.usefixtures("switch_p1r1_p2r1")
def test_recorder1_receives_all_messages_from_player1_r1(
        env, player1_r1, recorder1):
    """
    Test recorder1 receives all messages from player1_r1.
    """
    env.run(until=float("inf"))
    received_messages = recorder1.recorded_messages
    assert all(
        message in received_messages
        for message in player1_r1.messages_to_transmit
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
def test_recorder1_receives_all_messages_from_player2_r1(
        env, player2_r1, recorder1):
    """
    Test recorder1 receives all messages from player2_r1.
    """
    env.run(until=float("inf"))
    received_messages = recorder1.recorded_messages
    assert all(
        message in received_messages
        for message in player2_r1.messages_to_transmit
    )
