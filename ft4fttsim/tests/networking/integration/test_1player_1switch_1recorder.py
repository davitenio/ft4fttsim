# author: David Gessner <davidges@gmail.com>
"""
Execute tests under the following network:

+--------+ link1 +---------+ link2 +----------+
| player | ----> | switch2 | ----> | recorder |
+--------+       +---------+       +----------+
"""


import pytest
from ft4fttsim.tests.networking.fixturehelper import make_playback_device
from ft4fttsim.tests.networking.fixturehelper import PLAYBACK_CONFIGS
from ft4fttsim.tests.networking.fixturehelper import make_link
from ft4fttsim.tests.networking.fixturehelper import LINK_CONFIGS


@pytest.fixture(params=LINK_CONFIGS)
def link1(env, request, player, switch2):
    config = request.param
    new_link = make_link(
        config, env, player.ports[0], switch2.ports[0])
    return new_link


@pytest.fixture(params=LINK_CONFIGS)
def link2(env, request, switch2, recorder):
    config = request.param
    new_link = make_link(
        config, env, switch2.ports[1], recorder.ports[0])
    return new_link


@pytest.fixture
def recorder(env):
    from ft4fttsim.networking import MessageRecordingDevice
    recorder = MessageRecordingDevice(env, "recorder", 1)
    return recorder


@pytest.fixture(params=PLAYBACK_CONFIGS)
def player(request, env, recorder):
    config = request.param
    new_playback_device = make_playback_device(
        config, env, recorder)
    return new_playback_device


@pytest.mark.usefixtures("link1", "link2")
def test_messages_played__equals_messages_recorded(
        env, player, recorder):
    """
    Test that the recorder receives the messages transmitted by player.

    """
    env.run(until=float("inf"))
    assert player.messages_to_transmit == recorder.recorded_messages
