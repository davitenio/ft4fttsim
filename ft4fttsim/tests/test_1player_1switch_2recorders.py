# author: David Gessner <davidges@gmail.com>
"""
Perform tests under the following network:

                 +--------+ link1  +-----------+
                 |        | -----> | recorder1 |
+--------+ link0 |        |        +-----------+
| player | ----> | switch |
+--------+       |        | link2  +-----------+
                 |        | -----> | recorder2 |
                 +--------+        +-----------+
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


@pytest.fixture(params=PLAYBACK_CONFIGS)
def player_rec1(request, env, recorder1):
    """
    Create a message playback device that sends messages to recorder 1 only.

    """
    config = request.param
    new_playback_device = make_playback_device(
        config, env, recorder1)
    return new_playback_device


@pytest.fixture
def switch2(env):
    from ft4fttsim.networking import Switch
    return Switch(env, "switch2", num_ports=2)


@pytest.fixture(params=[(1000, 123)])
def link0_pr1(env, request, player_rec1, switch2):
    config = request.param
    new_link = make_link(
        config, env, player_rec1.output_ports[0], switch2.input_port)
    return new_link


@pytest.fixture(params=[(1000, 123)])
def link1(env, request, switch2, recorder1):
    config = request.param
    new_link = make_link(
        config, env, switch2.output_ports[0], recorder1.input_port)
    return new_link


@pytest.fixture(params=[(1000, 123)])
def link2(env, request, switch2, recorder2):
    config = request.param
    new_link = make_link(
        config, env, switch2.output_ports[1], recorder2.input_port)
    return new_link


@pytest.mark.usefixtures("link0_pr1", "link1", "link2")
def test_messages_are_received_by_recorder1(
        env, player_rec1, recorder1):
    """
    Test that recorder1 receives messages.

    """
    env.run(until=float("inf"))
    received_messages = recorder1.recorded_messages
    assert player_rec1.messages_to_transmit == received_messages


# until the switch implements proper forwarding mechanism, we expect the
# following test to fail.
@pytest.mark.xfail
def test_no_message_is_received_by_recorder2(
        env, player_rec1_switch_recorder1_recorder2):
    """
    Test that recorder2 does not receive any message.

    """
    env.run(until=float("inf"))
    player = player_rec1_switch_recorder1_recorder2[0]
    recorder2 = player_rec1_switch_recorder1_recorder2[3]
    received_messages = recorder2.recorded_messages
    assert len(received_messages) == 0


@pytest.fixture(params=PLAYBACK_CONFIGS)
def player_rec2(request, env, recorder2):
    """
    Create a message playback device that sends messages to recorder 2 only.

    """
    config = request.param
    new_playback_device = make_playback_device(
        config, env, recorder2)
    return new_playback_device


@pytest.fixture(params=[(1000, 123)])
def link0_pr2(env, request, player_rec2, switch2):
    config = request.param
    new_link = make_link(
        config, env, player_rec2.output_ports[0], switch2.input_port)
    return new_link


@pytest.mark.usefixtures("link0_pr2", "link1", "link2")
def test_messages_are_received_by_recorder2(
        env, player_rec2, recorder2):
    """
    Test that recorder2 receives messages.

    """
    env.run(until=float("inf"))
    received_messages = recorder2.recorded_messages
    assert player_rec2.messages_to_transmit == received_messages


# until the switch implements proper forwarding mechanism, we expect the
# following test to fail.
@pytest.mark.xfail
def test_no_message_is_received_by_recorder1(
        env, player_rec2_switch_recorder1_recorder2):
    """
    Test that recorder1 does not receive any message.

    """
    env.run(until=float("inf"))
    player = player_rec2_switch_recorder1_recorder2[0]
    recorder1 = player_rec2_switch_recorder1_recorder2[2]
    received_messages = recorder1.recorded_messages
    assert len(received_messages) == 0


@pytest.fixture(params=PLAYBACK_CONFIGS)
def player_rec12(request, env, recorder1, recorder2):
    """
    Create a player sending messages to recorder 1 and 2.

    """
    config = request.param
    new_playback_device = make_playback_device(
        config, env, [recorder1, recorder2])
    return new_playback_device


@pytest.fixture(params=[(1000, 123)])
def link0_pr12(env, request, player_rec12, switch2):
    config = request.param
    new_link = make_link(
        config, env, player_rec12.output_ports[0], switch2.input_port)
    return new_link


@pytest.mark.usefixtures("link0_pr12", "link1", "link2")
def test_multicast_messages_are_received_by_recorder1(
        env, player_rec12, recorder1):
    """
    Test that recorder1 receives multicast messages.

    """
    env.run(until=float("inf"))
    received_messages = recorder1.recorded_messages
    assert player_rec12.messages_to_transmit == received_messages


@pytest.mark.usefixtures("link0_pr12", "link1", "link2")
def test_multicast_messages_are_received_by_recorder2(
        env, player_rec12, recorder2):
    """
    Test that recorder2 receives multicast messages.

    """
    env.run(until=float("inf"))
    received_messages = recorder2.recorded_messages
    assert player_rec12.messages_to_transmit == received_messages
