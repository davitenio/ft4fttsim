# author: David Gessner <davidges@gmail.com>
"""
Perform tests under the following network:

                   +--------+  link1  +-----------+
                   |        | ------> | recorder1 |
+--------+  link0  |        |         +-----------+
| player | ------> | switch |
+--------+         |        |  link2  +-----------+
                   |        | ------> | recorder2 |
                   +--------+         +-----------+
                        | link3
                        v
                  +-----------+
                  | recorder3 |
                  +-----------+

"""

import pytest
from ft4fttsim.tests.fixturehelper import PLAYBACK_CONFIGS
from ft4fttsim.tests.fixturehelper import make_playback_device
from ft4fttsim.tests.fixturehelper import make_link


@pytest.fixture(params=[(100, 0)])
def link0(env, request):
    config = request.param
    new_link = make_link(config, env)
    return new_link


@pytest.fixture(params=[(100, 0)])
def link1(env, request):
    config = request.param
    new_link = make_link(config, env)
    return new_link


@pytest.fixture(params=[(100, 0)])
def link2(env, request):
    config = request.param
    new_link = make_link(config, env)
    return new_link


@pytest.fixture(params=[(100, 0)])
def link3(env, request):
    config = request.param
    new_link = make_link(config, env)
    return new_link


@pytest.fixture
def recorder1(env, link1):
    from ft4fttsim.networking import MessageRecordingDevice
    recorder = MessageRecordingDevice(env, "recorder1")
    recorder.connect_inlink(link1)
    return recorder


@pytest.fixture
def recorder2(env, link2):
    from ft4fttsim.networking import MessageRecordingDevice
    recorder = MessageRecordingDevice(env, "recorder2")
    recorder.connect_inlink(link2)
    return recorder


@pytest.fixture
def recorder3(env, link3):
    from ft4fttsim.networking import MessageRecordingDevice
    recorder = MessageRecordingDevice(env, "recorder3")
    recorder.connect_inlink(link3)
    return recorder


@pytest.fixture(params=PLAYBACK_CONFIGS)
def player_rec13(request, env, recorder1, recorder3, link0):
    """
    Create a message playback device that sends messages to recorder 1 and 3.

    """
    config = request.param
    new_playback_device = make_playback_device(
        config, env, [recorder1, recorder3], link0)
    return new_playback_device


@pytest.fixture
def player_rec13_switch_recorder1_recorder2_recorder3(
        env, player_rec13, switch, recorder1, recorder2, recorder3, link0,
        link1, link2, link3):
    switch.connect_inlink(link0)
    switch.connect_outlink(link1)
    switch.connect_outlink(link2)
    switch.connect_outlink(link3)
    return player_rec13, switch, recorder1, recorder2, recorder3


def test_messages_are_received_by_recorder1(
        env, player_rec13_switch_recorder1_recorder2_recorder3):
    """
    Test that recorder1 receives the messages.
    """
    env.run(until=float("inf"))
    player = player_rec13_switch_recorder1_recorder2_recorder3[0]
    recorder1 = player_rec13_switch_recorder1_recorder2_recorder3[2]
    received_messages = recorder1.recorded_messages
    assert player.messages_to_transmit == received_messages


def test_messages_are_received_by_recorder3(
        env, player_rec13_switch_recorder1_recorder2_recorder3):
    """
    Test that recorder3 receives the messages.
    """
    env.run(until=float("inf"))
    player = player_rec13_switch_recorder1_recorder2_recorder3[0]
    recorder3 = player_rec13_switch_recorder1_recorder2_recorder3[4]
    received_messages = recorder3.recorded_messages
    assert player.messages_to_transmit == received_messages


# until the switch implements proper forwarding mechanism, we expect the
# following test to fail.
@pytest.mark.xfail
def test_no_message_is_received_by_recorder2(
        env, player_rec13_switch_recorder1_recorder2_recorder3):
    """
    Test that recorder2 does not receive any message.
    """
    env.run(until=float("inf"))
    player = player_rec13_switch_recorder1_recorder2_recorder3[0]
    recorder2 = player_rec13_switch_recorder1_recorder2_recorder3[3]
    received_messages = recorder2.recorded_messages
    assert len(received_messages) == 0
