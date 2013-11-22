# author: David Gessner <davidges@gmail.com>
"""
Execute tests under the following network:

                    +---------+ link_r1  +-----------+
                    |         1 -------> 0 recorder1 |
+---------+ link_p1 |         |          +-----------+
| player1 0 ------> 0 switch4 |
+---------+         |         |
                    |         |
                    +---2-----+
                        ^
                        | link_p2
                   +----0----+
                   | player2 |
                   +---------+

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


@pytest.fixture(params=PLAYBACK_CONFIGS)
def player1_r1(request, env, recorder1):
    """
    Create a message playback device that sends messages to recorder 1 only.

    """
    config = request.param
    new_playback_device = make_playback_device(
        config, env, recorder1, name="player1")
    return new_playback_device


@pytest.fixture(params=[(1000, 123)])
def link_p1r1(env, request, player1_r1, switch4):
    config = request.param
    new_link = make_link(
        config, env, player1_r1.ports[0], switch4.ports[0])
    return new_link


@pytest.fixture(params=[(1000, 123)])
def link_r1(env, request, switch4, recorder1):
    config = request.param
    new_link = make_link(
        config, env, switch4.ports[1], recorder1.ports[0])
    return new_link


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


@pytest.fixture(params=[(1000, 123)])
def link_p2r1(env, request, player2_r1, switch4):
    config = request.param
    new_link = make_link(
        config, env, player2_r1.ports[0], switch4.ports[3])
    return new_link


@pytest.mark.usefixtures("link_p1r1", "link_p2r1", "link_r1")
def test_recorder1_receives_all_messages_from_player1_r1(
        env, player1_r1, recorder1):
    """
    Test recorder1 receives all messages from player1_r1.
    """
    env.run(until=float("inf"))
    received_messages = recorder1.recorded_messages
    print("recorder1.recorded_messages: " + str(received_messages))
    print("player1_r1.messages_to_transmit: " +
          str(player1_r1.messages_to_transmit))
    assert all(
        message in received_messages
        for message in player1_r1.messages_to_transmit
    )


@pytest.mark.usefixtures("link_p1r1", "link_p2r1", "link_r1")
def test_recorder1_receives_all_messages_from_player2_r1(
        env, player2_r1, recorder1):
    """
    Test recorder1 receives all messages from player2_r1.
    """
    env.run(until=float("inf"))
    received_messages = recorder1.recorded_messages
    print(received_messages)
    print(player2_r1.messages_to_transmit)
    assert all(
        message in received_messages
        for message in player2_r1.messages_to_transmit
    )
