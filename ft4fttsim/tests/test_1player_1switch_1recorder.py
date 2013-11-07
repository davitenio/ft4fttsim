# author: David Gessner <davidges@gmail.com>
"""
Execute tests under the following network:

+--------+      +--------+     +----------+
| player | ---> | switch | --> | recorder |
+--------+      +--------+     +----------+
"""


import pytest


@pytest.fixture(params=[(10, 3), (100, 0), (1000, 9)])
def another_link(env, request):
    from ft4fttsim.networking import Link
    Mbps, delay = request.param
    return Link(env, megabits_per_second=Mbps, propagation_delay_us=delay)


@pytest.fixture
def recorder(env, another_link):
    from ft4fttsim.networking import MessageRecordingDevice
    recorder = MessageRecordingDevice(env,
        "recorder attached to 'another_link'")
    recorder.connect_inlink(another_link)
    return recorder


@pytest.fixture
def player_switch_recorder(env, player, switch, recorder, link, another_link):
    switch.connect_inlink(link)
    switch.connect_outlink(another_link)
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
