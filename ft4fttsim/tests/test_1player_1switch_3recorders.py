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


@pytest.fixture(params=[(100, 0)])
def link0(env, request, player_rec13, switch4):
    config = request.param
    new_link = make_link(
        config, env, player_rec13.ports[0], switch4.ports[0])
    return new_link


@pytest.fixture(params=[(100, 0)])
def link1(env, request, switch4, recorder1):
    config = request.param
    new_link = make_link(
        config, env, switch4.ports[1], recorder1.ports[0])
    return new_link


@pytest.fixture(params=[(100, 0)])
def link2(env, request, switch4, recorder2):
    config = request.param
    new_link = make_link(
        config, env, switch4.ports[2], recorder2.ports[0])
    return new_link


@pytest.fixture(params=[(100, 0)])
def link3(env, request, switch4, recorder3):
    config = request.param
    new_link = make_link(
        config, env, switch4.ports[3], recorder3.ports[0])
    return new_link


@pytest.mark.usefixtures("link0", "link1", "link2", "link3")
def test_messages_are_received_by_recorder1(
        env, player_rec13, recorder1):
    """
    Test that recorder1 receives the messages.
    """
    env.run(until=float("inf"))
    received_messages = recorder1.recorded_messages
    assert player_rec13.messages_to_transmit == received_messages


@pytest.mark.usefixtures("link0", "link1", "link2", "link3")
def test_messages_are_received_by_recorder3(
        env, player_rec13, recorder3):
    """
    Test that recorder3 receives the messages.
    """
    env.run(until=float("inf"))
    received_messages = recorder3.recorded_messages
    assert player_rec13.messages_to_transmit == received_messages


# until the switch implements proper forwarding mechanism, we expect the
# following test to fail.
@pytest.mark.xfail
@pytest.mark.usefixtures("link0", "link1", "link2", "link3")
def test_no_message_is_received_by_recorder2(env, recorder2):
    """
    Test that recorder2 does not receive any message.
    """
    env.run(until=float("inf"))
    received_messages = recorder2.recorded_messages
    assert len(received_messages) == 0
