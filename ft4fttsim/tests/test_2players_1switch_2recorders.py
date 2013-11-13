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


@pytest.fixture
def recorder1(env):
    from ft4fttsim.networking import MessageRecordingDevice
    recorder = MessageRecordingDevice(env, "recorder1")
    return recorder


@pytest.fixture
def recorder2(env):
    from ft4fttsim.networking import MessageRecordingDevice
    recorder = MessageRecordingDevice(env, "recorder2")
    return recorder


@pytest.fixture
def switch2(env):
    from ft4fttsim.networking import Switch
    return Switch(env, "switch2", num_ports=2)


@pytest.fixture(params=PLAYBACK_CONFIGS)
def player1_r1(request, env, recorder1):
    """
    Create a message playback device that sends messages to recorder 1 only.

    """
    config = request.param
    new_playback_device = make_playback_device(
        config, env, recorder1, name="player1")
    return new_playback_device


@pytest.fixture(params=PLAYBACK_CONFIGS)
def player2_r2(request, env, recorder2):
    """
    Create a message playback device that sends messages to recorder 2 only.

    """
    config = request.param
    new_playback_device = make_playback_device(
        config, env, recorder2, name="player2")
    return new_playback_device


@pytest.fixture(params=[(1000, 123)])
def link_p1r1(env, request, player1_r1, switch2):
    config = request.param
    new_link = make_link(
        config, env, player1_r1.output_ports[0], switch2.input_port)
    return new_link


@pytest.fixture(params=[(1000, 123)])
def link_p2r2(env, request, player2_r2, switch2):
    config = request.param
    new_link = make_link(
        config, env, player2_r2.output_ports[0], switch2.input_port)
    return new_link


@pytest.fixture(params=[(1000, 123)])
def link_r1(env, request, switch2, recorder1):
    config = request.param
    new_link = make_link(
        config, env, switch2.output_ports[0], recorder1.input_port)
    return new_link


@pytest.fixture(params=[(1000, 123)])
def link_r2(env, request, switch2, recorder2):
    config = request.param
    new_link = make_link(
        config, env, switch2.output_ports[1], recorder2.input_port)
    return new_link


# until the switch implements proper forwarding mechanism, we expect the
# following test to fail.
@pytest.mark.xfail
@pytest.mark.usefixtures("link_p1r1", "link_p2r2", "link_r1", "link_r2")
def test_recorder1_receives_messages_from_player1_r1(
        env, player1_r1, recorder1):
    """
    Test recorder1 receives only the messages from player1_r1.
    """
    env.run(until=float("inf"))
    received_messages = recorder1.recorded_messages
    assert player1_r1.messages_to_transmit == received_messages


# until the switch implements proper forwarding mechanism, we expect the
# following test to fail.
@pytest.mark.xfail
@pytest.mark.usefixtures("link_p1r1", "link_p2r2", "link_r1", "link_r2")
def test_recorder2_does_not_receive_messages_from_player1_r1(
        env, player1_r1, recorder2):
    """
    Test recorder2 does not receive the messages from player1_r1.
    """
    env.run(until=float("inf"))
    received_messages = recorder2.recorded_messages
    assert all(
        message not in player1_r1.messages_to_transmit
        for message in received_messages)


# until the switch implements proper forwarding mechanism, we expect the
# following test to fail.
@pytest.mark.xfail
@pytest.mark.usefixtures("link_p1r1", "link_p2r2", "link_r1", "link_r2")
def test_recorder2_receives_messages_from_player2_r2(
        env, player2_r2, recorder2):
    """
    Test recorder2 receives only the messages from player2_r2.
    """
    env.run(until=float("inf"))
    received_messages = recorder2.recorded_messages
    assert player2_r2.messages_to_transmit == received_messages


# until the switch implements proper forwarding mechanism, we expect the
# following test to fail.
@pytest.mark.xfail
@pytest.mark.usefixtures("link_p1r1", "link_p2r2", "link_r1", "link_r2")
def test_recorder1_does_not_receive_messages_from_player2_r2(
        env, player2_r2, recorder1):
    """
    Test recorder1 does not receive the messages from player2_r2.
    """
    env.run(until=float("inf"))
    received_messages = recorder1.recorded_messages
    assert all(
        message not in player2_r2.messages_to_transmit
        for message in received_messages)


##########################################################


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
def link_p2r1(env, request, player2_r1, switch2):
    config = request.param
    new_link = make_link(
        config, env, player2_r1.output_ports[0], switch2.input_port)
    return new_link


@pytest.mark.usefixtures("link_p1r1", "link_p2r1", "link_r1", "link_r2")
def test_recorder1_receives_all_messages_from_player1_r1(
        env, player1_r1, recorder1):
    """
    Test recorder1 receives all messages from player1_r1.
    """
    env.run(until=float("inf"))
    received_messages = recorder1.recorded_messages
    assert all(
        message in received_messages
        for message in player1_r1.messages_to_transmit
    )


# until the switch implements proper forwarding mechanism, we expect the
# following test to fail.
@pytest.mark.xfail
@pytest.mark.usefixtures("link_p1r1", "link_p2r1", "link_r1", "link_r2")
def test_recorder2_receives_exactly_0_messages(
        env, recorder2):
    """
    Test recorder2 receives exactly zero messages.
    """
    env.run(until=float("inf"))
    received_messages = recorder2.recorded_messages
    assert len(received_messages) == 0


@pytest.mark.usefixtures("link_p1r1", "link_p2r1", "link_r1", "link_r2")
def test_recorder1_receives_all_messages_from_player2_r1(
        env, player2_r1, recorder1):
    """
    Test recorder1 receives all messages from player2_r1.
    """
    env.run(until=float("inf"))
    received_messages = recorder1.recorded_messages
    assert all(
        message in received_messages
        for message in player2_r1.messages_to_transmit
    )
