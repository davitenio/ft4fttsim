# author: David Gessner <davidges@gmail.com>
"""
Perform tests under the following network:

                   +--------+  link1  +-----------+
                   |        1 ------> 0 recorder1 |
+--------+  link0  |        |         +-----------+
| player 0 ------> 0 switch |
+--------+         |        |  link2  +-----------+
                   |        2 ------> 0 recorder2 |
                   +----3---+         +-----------+
                        | link3
                        v
                  +-----0-----+
                  | recorder3 |
                  +-----------+

"""

import pytest
from ft4fttsim.tests.networking.fixturehelper import PLAYBACK_CONFIGS
from ft4fttsim.tests.networking.fixturehelper import make_playback_device
from ft4fttsim.tests.networking.fixturehelper import make_link


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


@pytest.fixture
def recorder3(env):
    from ft4fttsim.networking import MessageRecordingDevice
    recorder = MessageRecordingDevice(env, "recorder3", 1)
    return recorder


@pytest.fixture(params=PLAYBACK_CONFIGS)
def player_rec13(request, env, recorder1, recorder3):
    """
    Create a message playback device that sends messages to recorder 1 and 3.

    """
    config = request.param
    new_playback_device = make_playback_device(
        config, env, [recorder1, recorder3])
    return new_playback_device


@pytest.fixture
def switch_pr13(env, player_rec13, recorder1, recorder2, recorder3):
    from ft4fttsim.networking import Switch
    new_switch = Switch(env, "switch4", num_ports=4)
    make_link((1000, 123), env, player_rec13.ports[0], new_switch.ports[0])
    make_link((1000, 123), env, recorder1.ports[0], new_switch.ports[1])
    make_link((1000, 123), env, recorder2.ports[0], new_switch.ports[2])
    make_link((1000, 123), env, recorder3.ports[0], new_switch.ports[3])
    new_switch.forwarding_table = {
        player_rec13: set([new_switch.ports[0]]),
        recorder1: set([new_switch.ports[1]]),
        recorder2: set([new_switch.ports[2]]),
        recorder3: set([new_switch.ports[3]]),
    }
    return new_switch


@pytest.mark.usefixtures("switch_pr13")
def test_messages_are_received_by_recorder1(
        env, player_rec13, recorder1):
    """
    Test that recorder1 receives the messages.
    """
    env.run(until=float("inf"))
    received_messages = recorder1.recorded_messages
    assert player_rec13.messages_to_transmit == received_messages


@pytest.mark.usefixtures("switch_pr13")
def test_messages_are_received_by_recorder3(
        env, player_rec13, recorder3):
    """
    Test that recorder3 receives the messages.
    """
    env.run(until=float("inf"))
    received_messages = recorder3.recorded_messages
    assert player_rec13.messages_to_transmit == received_messages


@pytest.mark.usefixtures("switch_pr13")
def test_no_message_is_received_by_recorder2(env, recorder2):
    """
    Test that recorder2 does not receive any message.
    """
    env.run(until=float("inf"))
    received_messages = recorder2.recorded_messages
    assert len(received_messages) == 0
