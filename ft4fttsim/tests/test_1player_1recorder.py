# author: David Gessner <davidges@gmail.com>
"""
Test the following network:

+--------+      +----------+
| player | ---> | recorder |
+--------+      +----------+
"""

from ft4fttsim.networking import *
from ft4fttsim.ethernet import *
import pytest
from ft4fttsim.tests.fixturehelper import make_playback_device
from ft4fttsim.tests.fixturehelper import PLAYBACK_CONFIGS
from ft4fttsim.tests.fixturehelper import make_link
from ft4fttsim.tests.fixturehelper import LINK_CONFIGS


@pytest.fixture(params=LINK_CONFIGS)
def link(env, request):
    new_link = make_link(request.param, env)
    return new_link


@pytest.fixture
def recorder(env, link):
    from ft4fttsim.networking import MessageRecordingDevice
    recorder = MessageRecordingDevice(env, "recorder")
    recorder.connect_inlink(link)
    return recorder


@pytest.fixture(params=PLAYBACK_CONFIGS)
def player(request, env, recorder, link):
    config = request.param
    new_playback_device = make_playback_device(
        config, env, recorder, link)
    return new_playback_device


def test_messages_played__equals_messages_recorded(
        env, player, recorder):
    """
    Test that the recorder receives the messages transmitted by player.
    """
    env.run(until=float("inf"))
    assert (player.messages_to_transmit ==
            recorder.recorded_messages)


BITS_PER_BYTE = 8


def test_first_message_played__arrives_when_expected(
        env, player, recorder, link):
    """
    Test that the first message transmitted by the player arrives at the
    recorder when expected.
    """
    def transmission_delay(message, link):
        bytes_transmitted = (
            Ethernet.PREAMBLE_SIZE_BYTES + Ethernet.SFD_SIZE_BYTES +
            message.size_bytes)
        bits_transmitted = bytes_transmitted * BITS_PER_BYTE
        # transmission delay in microseconds
        delay_in_us = bits_transmitted / float(link.megabits_per_second)
        return delay_in_us
    env.run(until=float("inf"))
    message = recorder.recorded_messages[0]
    # time it should take the first message to arrive at recorder in
    # microseconds
    time_to_destination_in_us = (transmission_delay(message, link) +
                                 link.propagation_delay_us)
    expected_timestamp = (player.transmission_start_times[0] +
                          time_to_destination_in_us)
    assert recorder.recorded_timestamps[0] == expected_timestamp


IFG = Ethernet.IFG_SIZE_BYTES
PS = Ethernet.PREAMBLE_SIZE_BYTES + Ethernet.SFD_SIZE_BYTES


@pytest.mark.parametrize(
    "Mbps,num_bytes,expected_timestamp",
    [(100, 1518,
        2 * (1518 + PS) * BITS_PER_BYTE / 100 + (IFG * BITS_PER_BYTE) / 100),
    (10, 123,
        2 * (123 + PS) * BITS_PER_BYTE / 10 + (IFG * BITS_PER_BYTE) / 10),
    (1000, 64,
        2 * (64 + PS) * BITS_PER_BYTE / 1000 + (IFG * BITS_PER_BYTE) / 1000)]
)
def test_interframe_gap(env, Mbps, num_bytes, expected_timestamp):
    """
    Test that if we instruct the transmission of 2 messages simultaneously,
    then the second message will be delayed by the interframe gap, in addition
    to the transmission time of the first message.

    """
    link = Link(env, Mbps, 0)
    player = MessagePlaybackDevice(env, "player")
    player.connect_outlink(link)
    port = player.output_ports[0]
    recorder = MessageRecordingDevice(env, "recorder")
    recorder.connect_inlink(link)
    messages = [Message(env, player, recorder, num_bytes, "message0"),
                Message(env, player, recorder, num_bytes, "message1")]
    transmission_start_time = 0
    player.load_transmission_commands(
        {
            transmission_start_time: {port: messages}
        }
    )
    env.run(until=float("inf"))
    # check that the 2 recorded timestamps are almost equal (they will usually
    # not be exactly equal because of floating-point imprecision)
    assert abs(recorder.recorded_timestamps[1] - expected_timestamp) < 0.00001
