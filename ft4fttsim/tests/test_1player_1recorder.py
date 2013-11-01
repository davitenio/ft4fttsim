# author: David Gessner <davidges@gmail.com>

import unittest
from ft4fttsim.networking import *
from ft4fttsim.masterslave import *
from ft4fttsim.ethernet import *


class Test1Player1Recorder(unittest.TestCase):

    def setUp(self):
        """
        Set up the following network:

        +--------+      +----------+
        | player | ---> | recorder |
        +--------+      +----------+
        """
        self.env = simpy.Environment()
        self.player = MessagePlaybackDevice(self.env, "player")
        self.recorder = MessageRecordingDevice(self.env, "recorder")
        self.link_Mbps = 100
        self.link_propagation_delay_us = 3
        link_player_recorder = Link(self.env, self.link_Mbps,
            self.link_propagation_delay_us)
        self.player.connect_outlink(link_player_recorder)
        self.recorder.connect_inlink(link_player_recorder)


class TestSingleMessage(Test1Player1Recorder):

    def setUp(self):
        """
        Set up the player sending a single message.
        """
        Test1Player1Recorder.setUp(self)
        self.tx_start_time = 0
        self.message_size_bytes = 1518
        self.messages_to_transmit = [Message(self.env, self.player,
            self.recorder, self.message_size_bytes, "test message")]
        outlink = self.player.outlinks[0]
        transmission_command = {outlink: self.messages_to_transmit}
        list_of_commands = {self.tx_start_time: transmission_command}
        self.player.load_transmission_commands(list_of_commands)

    def test_message_played__equals_message_recorded(self):
        """
        Test that the recorder receives the message transmitted by player.
        """
        self.env.run(until=float("inf"))
        received_messages = self.recorder.recorded_messages
        self.assertEqual(self.messages_to_transmit, received_messages)

    def test_message_played__arrives_when_expected(self):
        """
        Test that the message transmitted by the player arrives at the recorder
        when expected.
        """
        self.env.run(until=float("inf"))
        timestamp = self.recorder.recorded_timestamps[0]
        BITS_PER_BYTE = 8
        # time it should take the message to arrive at recorder in microseconds
        time_to_destination_in_us = (
            (Ethernet.PREAMBLE_SIZE_BYTES + Ethernet.SFD_SIZE_BYTES +
            self.message_size_bytes) * BITS_PER_BYTE /
            float(self.link_Mbps) + self.link_propagation_delay_us)
        expected_timestamp = self.tx_start_time + time_to_destination_in_us
        self.assertEqual(timestamp, expected_timestamp)


class TestTwoMessages(Test1Player1Recorder):

    def setUp(self):
        """
        Set up the player sending 2 messages.
        """
        Test1Player1Recorder.setUp(self)
        tx_start_time0, tx_start_time1 = range(2)
        self.messages_to_transmit0 = [Message(self.env, self.player,
            self.recorder, Ethernet.MAX_FRAME_SIZE_BYTES,
            "message at time {:d}".format(tx_start_time0))]
        self.messages_to_transmit1 = [Message(self.env, self.player,
            self.recorder, Ethernet.MAX_FRAME_SIZE_BYTES,
            "message at time {:d}".format(tx_start_time1))]
        outlink = self.player.outlinks[0]
        list_of_commands = {}
        transmission_command0 = {outlink: self.messages_to_transmit0}
        list_of_commands[tx_start_time0] = transmission_command0
        transmission_command1 = {outlink: self.messages_to_transmit1}
        list_of_commands[tx_start_time1] = transmission_command1
        self.player.load_transmission_commands(list_of_commands)

    def test_2_messages_played__receive_2_messages(self):
        """
        That that the recorder receives exactly 2 messages.
        """
        self.env.run(until=float("inf"))
        received_messages = self.recorder.recorded_messages
        self.assertEqual(len(received_messages), 2)

    def test_2_messages_played__equals_the_2_messages_recorded(self):
        """
        Test that the recorder receives the messages transmitted by the player.
        """
        self.env.run(until=float("inf"))
        received_messages = self.recorder.recorded_messages
        all_messages_transmitted = (self.messages_to_transmit0 +
            self.messages_to_transmit1)
        self.assertEqual(all_messages_transmitted, received_messages)


class TestEightMessages(Test1Player1Recorder):

    def setUp(self):
        """
        Set up the player sending 8 messages.
        """
        Test1Player1Recorder.setUp(self)
        outlink = self.player.outlinks[0]
        transmission_start_times = range(8)
        self.all_messages_to_transmit = []
        list_of_commands = {}
        for time in transmission_start_times:
            transmission_command = {}
            messages_to_transmit = [Message(self.env, self.player,
                self.recorder, Ethernet.MAX_FRAME_SIZE_BYTES, "test")]
            self.all_messages_to_transmit.extend(messages_to_transmit)
            transmission_command[outlink] = messages_to_transmit
            list_of_commands[time] = transmission_command
        self.player.load_transmission_commands(list_of_commands)

    def test_8_messages_played__same_messages_recorded(self):
        """
        Test that the set of messages received by recorder equals the set of
        messages transmitted by player.
        """
        self.env.run(until=float("inf"))
        received_messages = self.recorder.recorded_messages
        self.assertEqual(set(self.all_messages_to_transmit),
            set(received_messages))

    def test_8_messages_played__messages_recorded_same_order(self):
        """
        Test that the recorder receives the same messages as the player
        transmitted, checking also that the order of messages coincides.
        """
        self.env.run(until=float("inf"))
        received_messages = self.recorder.recorded_messages
        self.assertEqual(self.all_messages_to_transmit, received_messages)


class Test3BatchesOf2Messages(Test1Player1Recorder):

    def setUp(self):
        """
        Set up the player sending 2 messages simultaneously at 3 different
        instants of time.
        """
        Test1Player1Recorder.setUp(self)
        tx_start_time0, tx_start_time1, tx_start_time2 = 0, 1, 2
        self.messages_to_transmit0 = [
            Message(self.env, self.player, self.recorder,
            Ethernet.MAX_FRAME_SIZE_BYTES, "batch 0 msg 0"),
            Message(self.env, self.player, self.recorder,
            Ethernet.MAX_FRAME_SIZE_BYTES, "batch 0 msg 1"),
            ]
        self.messages_to_transmit1 = [
            Message(self.env, self.player, self.recorder,
            Ethernet.MAX_FRAME_SIZE_BYTES, "batch 1 msg 0"),
            Message(self.env, self.player, self.recorder,
            Ethernet.MAX_FRAME_SIZE_BYTES, "batch 1 msg 1"),
            ]
        self.messages_to_transmit2 = [
            Message(self.env, self.player, self.recorder,
            Ethernet.MAX_FRAME_SIZE_BYTES, "batch 2 msg 0"),
            Message(self.env, self.player, self.recorder,
            Ethernet.MAX_FRAME_SIZE_BYTES, "batch 2 msg 1"),
            ]
        outlink = self.player.outlinks[0]
        list_of_commands = {}
        transmission_command0 = {outlink: self.messages_to_transmit0}
        list_of_commands[tx_start_time0] = transmission_command0
        transmission_command1 = {outlink: self.messages_to_transmit1}
        list_of_commands[tx_start_time1] = transmission_command1
        transmission_command2 = {outlink: self.messages_to_transmit2}
        list_of_commands[tx_start_time2] = transmission_command2
        self.player.load_transmission_commands(list_of_commands)

    def test_3_batches_of_2_messages_played__six_messages_recorded(self):
        """
        Test that the recorder received exactly 6 messages.
        """
        self.env.run(until=float("inf"))
        received_messages = self.recorder.recorded_messages
        self.assertEqual(len(received_messages), 6)

    def test_3_batches_of_2_messages_played__equals_messages_recorded(self):
        """
        Test that the recorder receives the messages transmitted by player, and
        that it receives them in the correct order.
        """
        self.env.run(until=float("inf"))
        received_messages = self.recorder.recorded_messages
        all_messages_transmitted = (self.messages_to_transmit0 +
            self.messages_to_transmit1 + self.messages_to_transmit2)
        self.assertEqual(all_messages_transmitted, received_messages)


if __name__ == '__main__':
    unittest.main()
