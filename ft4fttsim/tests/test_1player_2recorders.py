# author: David Gessner <davidges@gmail.com>
"""
Execute tests under the following network:

+--------+  link1    +-----------+
|        | --------> | recorder1 |
|        |           +-----------+
| player |
|        |  link2    +-----------+
|        | --------> | recorder2 |
+--------+           +-----------+

"""

import pytest
from ft4fttsim.tests.fixturehelper import make_link


@pytest.fixture(params=[(1000, 13)])
def link1(env, request):
    config = request.param
    new_link = make_link(config, env)
    return new_link


@pytest.fixture(params=[(1000, 13)])
def link2(env, request):
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
def player(env, link1, link2):
    from ft4fttsim.networking import MessagePlaybackDevice
    player = MessagePlaybackDevice(env, "player")
    player.connect_outlink(link1)
    player.connect_outlink(link2)
    return player


@pytest.fixture
def player_diff(env, player, recorder1, recorder2):
    """
    Set up player sending a separate message at a different instant of time
    to each recorder.
    """
    from ft4fttsim.networking import Message
    tx_start_time1, tx_start_time2 = range(2)
    messages1 = [Message(env, player, recorder1, 543, "message for recorder1")]
    messages2 = [Message(env, player, recorder2, 453, "message for recorder2")]
    port1 = player.output_ports[0]
    port2 = player.output_ports[1]
    player.load_transmission_commands(
        {
            0: {port1: messages1},
            1: {port2: messages2},
        }
    )
    player.messages1 = messages1
    player.messages2 = messages2
    return player


def test_recorder1_gets_correct_message(env, player_diff, recorder1):
    env.run(until=float("inf"))
    assert player_diff.messages1 == recorder1.recorded_messages


def test_recorder2_gets_correct_message(env, player_diff, recorder2):
    env.run(until=float("inf"))
    assert player_diff.messages2 == recorder2.recorded_messages


def test_recorder1_does_not_get_wrong_message(env, player_diff, recorder1):
    env.run(until=float("inf"))
    assert player_diff.messages2 != recorder1.recorded_messages


def test_recorder2_does_not_get_wrong_message(env, player_diff, recorder2):
    env.run(until=float("inf"))
    assert player_diff.messages1 != recorder2.recorded_messages
