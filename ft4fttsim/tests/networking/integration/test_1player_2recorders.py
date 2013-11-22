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
def player(env):
    from ft4fttsim.networking import MessagePlaybackDevice
    player = MessagePlaybackDevice(env, "player", num_ports=2)
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
    port0 = player.ports[0]
    port1 = player.ports[1]
    player.load_transmission_commands(
        {
            0: {port0: messages1},
            1: {port1: messages2},
        }
    )
    player.messages1 = messages1
    player.messages2 = messages2
    return player


@pytest.fixture(params=[(1000, 13)])
def link1(env, request, player_diff, recorder1):
    config = request.param
    new_link = make_link(
        config, env, player_diff.ports[0], recorder1.ports[0])
    return new_link


@pytest.fixture(params=[(1000, 13)])
def link2(env, request, player_diff, recorder2):
    config = request.param
    new_link = make_link(
        config, env, player_diff.ports[1], recorder2.ports[0])
    return new_link


@pytest.mark.usefixtures("link1", "link2")
def test_recorder1_gets_correct_message(env, player_diff, recorder1):
    env.run(until=float("inf"))
    assert player_diff.messages1 == recorder1.recorded_messages


@pytest.mark.usefixtures("link1", "link2")
def test_recorder2_gets_correct_message(env, player_diff, recorder2):
    env.run(until=float("inf"))
    assert player_diff.messages2 == recorder2.recorded_messages


@pytest.mark.usefixtures("link1", "link2")
def test_recorder1_does_not_get_wrong_message(env, player_diff, recorder1):
    env.run(until=float("inf"))
    assert player_diff.messages2 != recorder1.recorded_messages


@pytest.mark.usefixtures("link1", "link2")
def test_recorder2_does_not_get_wrong_message(env, player_diff, recorder2):
    env.run(until=float("inf"))
    assert player_diff.messages1 != recorder2.recorded_messages
