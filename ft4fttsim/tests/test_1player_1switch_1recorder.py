# author: David Gessner <davidges@gmail.com>
"""
Execute tests under the following network:

+--------+      +--------+     +----------+
| player | ---> | switch | --> | recorder |
+--------+      +--------+     +----------+
"""


import pytest
from ft4fttsim.tests.fixturehelper import make_playback_device
from ft4fttsim.tests.fixturehelper import PLAYBACK_CONFIGS
from ft4fttsim.tests.fixturehelper import make_link
from ft4fttsim.tests.fixturehelper import LINK_CONFIGS


@pytest.fixture(params=LINK_CONFIGS)
def link1(env, request):
    config = request.param
    new_link = make_link(config, env)
    return new_link


@pytest.fixture(params=LINK_CONFIGS)
def link2(env, request):
    config = request.param
    new_link = make_link(config, env)
    return new_link


@pytest.fixture
def recorder(env, link2):
    from ft4fttsim.networking import MessageRecordingDevice
    recorder = MessageRecordingDevice(env, "recorder")
    recorder.connect_inlink(link2)
    return recorder


@pytest.fixture(params=PLAYBACK_CONFIGS)
def player(request, env, recorder, link1):
    config = request.param
    new_playback_device = make_playback_device(config, env, recorder,
        link1)
    return new_playback_device


@pytest.fixture
def player_switch_recorder(env, player, switch, recorder,
        link1, link2):
    switch.connect_inlink(link1)
    switch.connect_outlink(link2)
    return player, switch, recorder


def test_messages_played__equals_messages_recorded(env,
        player_switch_recorder):
    """
    Test that the recorder receives the messages transmitted by player.

    """
    env.run(until=float("inf"))
    player = player_switch_recorder[0]
    recorder = player_switch_recorder[2]
    assert player.messages_to_transmit == recorder.recorded_messages
