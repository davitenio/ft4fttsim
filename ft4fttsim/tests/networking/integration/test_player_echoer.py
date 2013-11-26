# author: David Gessner <davidges@gmail.com>
"""
Test the following network:

+-----------------+       +--------+
| player_recorder | <---> | echoer |
+-----------------+       +--------+

"""

import pytest

from ft4fttsim.networking import EchoDevice, MessagePlaybackAndRecordingDevice
from ft4fttsim.tests.networking.fixturehelper import make_link
from ft4fttsim.tests.networking.fixturehelper import make_playback_device
from ft4fttsim.tests.networking.fixturehelper import PLAYBACK_CONFIGS


@pytest.fixture(params=[(10, 0)])
def link(env, request, player_recorder, echoer):
    new_link = make_link(request.param, env, player_recorder.ports[0],
                         echoer.ports[0])
    return new_link


@pytest.fixture
def echoer(env):
    echoer = EchoDevice(env, "echoer")
    return echoer


@pytest.fixture(params=PLAYBACK_CONFIGS)
def player_recorder(request, env, echoer):
    config = request.param
    new_playback_device = make_playback_device(
        config, env, echoer, "player/recorder",
        cls=MessagePlaybackAndRecordingDevice)
    return new_playback_device


@pytest.mark.usefixtures("link")
def test_link_is_bidirectional(
        env, player_recorder, echoer):
    """
    Test that player_recorder receives back the messages it transmits.

    """
    env.run(until=float("inf"))
    assert (
        player_recorder.messages_to_transmit ==
        player_recorder.recorded_messages)
