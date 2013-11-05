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


@pytest.fixture(params=[(10, 3), (100, 0), (1000, 9)])
def link(env, request):
    Mbps, delay = request.param
    return Link(env, megabits_per_second=Mbps, propagation_delay_us=delay)


@pytest.fixture
def recorder(env, link):
    recorder = MessageRecordingDevice(env, "recorder")
    recorder.connect_inlink(link)
    return recorder


@pytest.fixture(params=[
    "single message",
    "2 messages",
    "8 messages",
    "3 batches of 2 messages",
])
def player(request, env, recorder, link):
    player = MessagePlaybackDevice(env, "player")
    player.connect_outlink(link)
    if request.param == "single message":
        messages = [Message(env, player, recorder, 1518, "message")]
        player.load_transmission_commands(
            {
                0: {link: messages}
            }
        )
        player.messages_to_transmit = messages
    elif request.param == "2 messages":
        message_lists = [
            [Message(env, player, recorder, 1200, "message0")],
            [Message(env, player, recorder, 1000, "message1")],
        ]
        player.load_transmission_commands(
            {
                0: {link: message_lists[0]},
                1: {link: message_lists[1]},
            }
        )
        player.messages_to_transmit = [message for message_list in
            message_lists for message in message_list]
    elif request.param == "8 messages":
        message_lists = [
            [Message(env, player, recorder, 1200, "message0")],
            [Message(env, player, recorder, 1000, "message1")],
            [Message(env, player, recorder, 958, "message2")],
            [Message(env, player, recorder, 958, "message3")],
            [Message(env, player, recorder, 1508, "message4")],
            [Message(env, player, recorder, 90, "message5")],
            [Message(env, player, recorder, 1111, "message6")],
            [Message(env, player, recorder, 1234, "message7")],
        ]
        player.load_transmission_commands(
            {
                0: {link: message_lists[0]},
                1: {link: message_lists[1]},
                5: {link: message_lists[2]},
                6: {link: message_lists[3]},
                9: {link: message_lists[4]},
                15: {link: message_lists[5]},
                123: {link: message_lists[6]},
                11114: {link: message_lists[7]},
            }
        )
        player.messages_to_transmit = [message for message_list in
            message_lists for message in message_list]
    elif request.param == "3 batches of 2 messages":
        message_lists = [
            [Message(env, player, recorder, 142, "batch0 message0"),
                Message(env, player, recorder, 1000, "batch0 message1")],
            [Message(env, player, recorder, 218, "batch1 message0"),
                Message(env, player, recorder, 1050, "batch1 message1")],
            [Message(env, player, recorder, 1381, "batch2 message0"),
                Message(env, player, recorder, 150, "batch2 message1")],
        ]
        player.load_transmission_commands(
            {
                100: {link: message_lists[0]},
                111: {link: message_lists[1]},
                555: {link: message_lists[2]},
            }
        )
        player.messages_to_transmit = [message for message_list in
            message_lists for message in message_list]
    return player


def test_messages_played__equals_messages_recorded(env, player, recorder):
    """
    Test that the recorder receives the messages transmitted by player.
    """
    env.run(until=float("inf"))
    assert player.messages_to_transmit == recorder.recorded_messages


def test_first_message_played__arrives_when_expected(
        env, recorder, player, link):
    """
    Test that the first message transmitted by the player arrives at the
    recorder when expected.
    """
    def transmission_delay(message, link):
        bytes_transmitted = (Ethernet.PREAMBLE_SIZE_BYTES +
            Ethernet.SFD_SIZE_BYTES + message.size_bytes)
        BITS_PER_BYTE = 8
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
