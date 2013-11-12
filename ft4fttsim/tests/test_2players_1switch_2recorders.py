# author: David Gessner <davidges@gmail.com>
"""
Execute tests under the following network:

                    +--------+ link_r1  +-----------+
                    |        | -------> | recorder1 |
+---------+ link_p1 |        |          +-----------+
| player1 | ------> | switch |
+---------+         |        | link_r2  +-----------+
                    |        | -------> | recorder2 |
                    +--------+          +-----------+
                        ^
                        | link_p2
                   +---------+
                   | player2 |
                   +---------+

"""

import pytest
from ft4fttsim.tests.fixturehelper import PLAYBACK_CONFIGS
from ft4fttsim.tests.fixturehelper import make_playback_device
from ft4fttsim.tests.fixturehelper import make_link


@pytest.fixture(params=[(1000, 123)])
def link_p1(env, request):
    config = request.param
    new_link = make_link(config, env)
    return new_link


@pytest.fixture(params=[(1000, 123)])
def link_p2(env, request):
    config = request.param
    new_link = make_link(config, env)
    return new_link


@pytest.fixture(params=[(1000, 123)])
def link_r1(env, request):
    config = request.param
    new_link = make_link(config, env)
    return new_link


@pytest.fixture(params=[(1000, 123)])
def link_r2(env, request):
    config = request.param
    new_link = make_link(config, env)
    return new_link


@pytest.fixture
def recorder1(env, link_r1):
    from ft4fttsim.networking import MessageRecordingDevice
    recorder = MessageRecordingDevice(env, "recorder1")
    recorder.connect_inlink(link_r1)
    return recorder


@pytest.fixture
def recorder2(env, link_r2):
    from ft4fttsim.networking import MessageRecordingDevice
    recorder = MessageRecordingDevice(env, "recorder2")
    recorder.connect_inlink(link_r2)
    return recorder


@pytest.fixture(params=PLAYBACK_CONFIGS)
def player1_r1(request, env, recorder1, link_p1):
    """
    Create a message playback device that sends messages to recorder 1 only.

    """
    config = request.param
    new_playback_device = make_playback_device(
        config, env, recorder1, link_p1, name="player1")
    return new_playback_device


@pytest.fixture(params=PLAYBACK_CONFIGS)
def player2_r2(request, env, recorder2, link_p2):
    """
    Create a message playback device that sends messages to recorder 2 only.

    """
    config = request.param
    new_playback_device = make_playback_device(
        config, env, recorder2, link_p2, name="player2")
    return new_playback_device


@pytest.fixture
def connected_devices_p1r1_p2r2(
        env, player1_r1, link_p1, player2_r2, link_p2, switch, recorder1,
        link_r1, recorder2, link_r2):
    switch.connect_inlink(link_p1)
    switch.connect_inlink(link_p2)
    switch.connect_outlink(link_r1)
    switch.connect_outlink(link_r2)
    return player1_r1, player2_r2, recorder1, recorder2


# until the switch implements proper forwarding mechanism, we expect the
# following test to fail.
@pytest.mark.xfail
def test_recorder1_receives_messages_from_player1_r1(
        env, connected_devices_p1r1_p2r2):
    """
    Test recorder1 receives only the messages from player1_r1.
    """
    env.run(until=float("inf"))
    player1_r1 = connected_devices_p1r1_p2r2[0]
    recorder1 = connected_devices_p1r1_p2r2[2]
    received_messages = recorder1.recorded_messages
    assert player1_r1.messages_to_transmit == received_messages


# until the switch implements proper forwarding mechanism, we expect the
# following test to fail.
@pytest.mark.xfail
def test_recorder2_does_not_receive_messages_from_player1_r1(
        env, connected_devices_p1r1_p2r2):
    """
    Test recorder2 does not receive the messages from player1_r1.
    """
    env.run(until=float("inf"))
    player1_r1 = connected_devices_p1r1_p2r2[0]
    recorder2 = connected_devices_p1r1_p2r2[3]
    received_messages = recorder2.recorded_messages
    assert all(
        message not in player1_r1.messages_to_transmit
        for message in received_messages)


# until the switch implements proper forwarding mechanism, we expect the
# following test to fail.
@pytest.mark.xfail
def test_recorder2_receives_messages_from_player2_r2(
        env, connected_devices_p1r1_p2r2):
    """
    Test recorder2 receives only the messages from player2_r2.
    """
    env.run(until=float("inf"))
    player2_r2 = connected_devices_p1r1_p2r2[1]
    recorder2 = connected_devices_p1r1_p2r2[3]
    received_messages = recorder2.recorded_messages
    assert player2_r2.messages_to_transmit == received_messages


# until the switch implements proper forwarding mechanism, we expect the
# following test to fail.
@pytest.mark.xfail
def test_recorder1_does_not_receive_messages_from_player2_r2(
        env, connected_devices_p1r1_p2r2):
    """
    Test recorder1 does not receive the messages from player2_r2.
    """
    env.run(until=float("inf"))
    player2_r2 = connected_devices_p1r1_p2r2[1]
    recorder1 = connected_devices_p1r1_p2r2[2]
    received_messages = recorder1.recorded_messages
    assert all(
        message not in player2_r2.messages_to_transmit
        for message in received_messages)


@pytest.fixture(params=PLAYBACK_CONFIGS)
def player2_r1(request, env, recorder1, link_p2):
    """
    Create a second message playback device that sends messages to recorder 1
    only.

    """
    config = request.param
    new_playback_device = make_playback_device(
        config, env, recorder1, link_p2, name="player2")
    return new_playback_device


@pytest.fixture
def connected_devices_p1r1_p2r1(
        env, player1_r1, link_p1, player2_r1, link_p2, switch, recorder1,
        link_r1, recorder2, link_r2):
    switch.connect_inlink(link_p1)
    switch.connect_inlink(link_p2)
    switch.connect_outlink(link_r1)
    switch.connect_outlink(link_r2)
    return player1_r1, player2_r1, recorder1, recorder2


def test_recorder1_receives_all_messages_from_player1_r1(
        env, connected_devices_p1r1_p2r1):
    """
    Test recorder1 receives all messages from player1_r1.
    """
    env.run(until=float("inf"))
    player1_r1 = connected_devices_p1r1_p2r1[0]
    recorder1 = connected_devices_p1r1_p2r1[2]
    received_messages = recorder1.recorded_messages
    assert all(
        message in received_messages
        for message in player1_r1.messages_to_transmit
    )


# until the switch implements proper forwarding mechanism, we expect the
# following test to fail.
@pytest.mark.xfail
def test_recorder2_receives_exactly_0_messages(
        env, connected_devices_p1r1_p2r1):
    """
    Test recorder2 receives exactly zero messages.
    """
    env.run(until=float("inf"))
    recorder2 = connected_devices_p1r1_p2r1[3]
    received_messages = recorder2.recorded_messages
    assert len(received_messages) == 0


def test_recorder1_receives_all_messages_from_player2_r1(
        env, connected_devices_p1r1_p2r1):
    """
    Test recorder1 receives all messages from player2_r1.
    """
    env.run(until=float("inf"))
    player2_r1 = connected_devices_p1r1_p2r1[1]
    recorder1 = connected_devices_p1r1_p2r1[2]
    received_messages = recorder1.recorded_messages
    assert all(
        message in received_messages
        for message in player2_r1.messages_to_transmit
    )
