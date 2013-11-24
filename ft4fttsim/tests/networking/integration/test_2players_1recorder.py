# author: David Gessner <davidges@gmail.com>
"""
Execute tests under the following network:

                    +---------+
                    |         |
+---------+ link0   |         |
| player0 0 ------> 0 recorder|
+---------+         |         |
                    |         |
                    +---1-----+
                        ^
                        | link1
                   +----0----+
                   | player1 |
                   +---------+

"""

import pytest

from ft4fttsim.tests.networking.fixturehelper import PLAYBACK_CONFIGS
from ft4fttsim.tests.networking.fixturehelper import make_playback_device
from ft4fttsim.tests.networking.fixturehelper import make_link


@pytest.fixture
def recorder(env):
    """
    Create a MessageRecordingDevice instance with 2 ports.

    """
    from ft4fttsim.networking import MessageRecordingDevice
    recorder = MessageRecordingDevice(env, "recorder", 2)
    return recorder


@pytest.fixture(params=PLAYBACK_CONFIGS)
def player0(request, env, recorder):
    """
    Create a message playback device that sends messages to recorder.

    """
    config = request.param
    new_playback_device = make_playback_device(
        config, env, recorder, name="player0")
    return new_playback_device


@pytest.fixture(params=PLAYBACK_CONFIGS)
def player1(request, env, recorder):
    """
    Create a second message playback device that sends messages to recorder.

    """
    config = request.param
    new_playback_device = make_playback_device(
        config, env, recorder, name="player1")
    return new_playback_device


@pytest.fixture(params=[(1000, 123)])
def link0(env, request, player0, recorder):
    config = request.param
    new_link = make_link(
        config, env, player0.ports[0], recorder.ports[0])
    return new_link


@pytest.fixture(params=[(1000, 123)])
def link1(env, request, player1, recorder):
    config = request.param
    new_link = make_link(
        config, env, player1.ports[0], recorder.ports[1])
    return new_link


@pytest.mark.usefixtures("link0", "link1")
def test_recorder_receives_all_messages_from_player0(
        env, player0, recorder):
    """
    Test recorder receives all messages from player0.
    """
    env.run(until=float("inf"))
    received_messages = recorder.recorded_messages
    print("recorder.recorded_messages: " + str(received_messages))
    print("player0.messages_to_transmit: " +
          str(player0.messages_to_transmit))
    assert all(
        message in received_messages
        for message in player0.messages_to_transmit
    )


@pytest.mark.usefixtures("link0", "link1")
def test_recorder_receives_all_messages_from_player1(
        env, player1, recorder):
    """
    Test recorder receives all messages from player1.
    """
    env.run(until=float("inf"))
    received_messages = recorder.recorded_messages
    print("recorder.recorded_messages: " + str(received_messages))
    print("player1.messages_to_transmit: " +
          str(player1.messages_to_transmit))
    assert all(
        message in received_messages
        for message in player1.messages_to_transmit
    )
