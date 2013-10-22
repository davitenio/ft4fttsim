# author: David Gessner <davidges@gmail.com>

import unittest
from ft4fttsim.networking import *
from ft4fttsim.masterslave import *
from ft4fttsim.ethernet import *
from ft4fttsim import simlogging


class TestMessagePlaybackDeviceToRecorder(unittest.TestCase):

    def setUp(self):
        """
        Set up the following network:

        +--------+      +----------+
        | player | ---> | recorder |
        +--------+      +----------+
        """
        self.player = MessagePlaybackDevice("player")
        self.recorder = MessageRecordingDevice("recorder")
        self.link_Mbps = 100
        self.link_propagation_delay_us = 3
        link_player_recorder = Link(self.link_Mbps,
            self.link_propagation_delay_us)
        self.player.connect_outlink(link_player_recorder)
        self.recorder.connect_inlink(link_player_recorder)
        # initialize SimPy
        initialize()
        for device in [self.player, self.recorder]:
            activate(device, device.run(), at=0.0)

    def tearDown(self):
        simlogging.logger.propagate = False

    def test_message_played__equals_message_recorded(self):
        # uncomment the next line to enable logging during this test
        #simlogging.logger.propagate = True
        tx_start_time = 0
        message_size_bytes = Ethernet.MAX_FRAME_SIZE_BYTES
        messages_to_transmit = [Message(self.player, self.recorder,
            message_size_bytes, "test")]
        outlink = self.player.get_outlinks()[0]
        transmission_command = {outlink: messages_to_transmit}
        list_of_commands = {tx_start_time: transmission_command}
        self.player.load_transmission_commands(list_of_commands)
        simulate(until=float("inf"))
        received_messages = self.recorder.get_recorded_messages()
        self.assertEqual(messages_to_transmit, received_messages)

    def test_message_played__arrives_when_expected(self):
        # uncomment the next line to enable logging during this test
        #simlogging.logger.propagate = True
        tx_start_time = 0
        message_size_bytes = 1526
        messages_to_transmit = [Message(self.player, self.recorder,
            message_size_bytes, "test")]
        outlink = self.player.get_outlinks()[0]
        transmission_command = {outlink: messages_to_transmit}
        list_of_commands = {tx_start_time: transmission_command}
        self.player.load_transmission_commands(list_of_commands)
        simulate(until=float("inf"))
        timestamp = self.recorder.get_recorded_timestamps()[0]
        BITS_PER_BYTE = 8
        # time it should take the message to arrive at recorder in microseconds
        time_to_destination_in_us = (message_size_bytes * BITS_PER_BYTE /
            float(self.link_Mbps) + self.link_propagation_delay_us)
        expected_timestamp = time_to_destination_in_us
        self.assertEqual(timestamp, expected_timestamp)

    def test_2_messages_played__equals_the_2_messages_recorded(self):
        # uncomment the next line to enable logging during this test
        #simlogging.logger.propagate = True
        tx_start_time0, tx_start_time1 = range(2)
        messages_to_transmit0 = [Message(self.player, self.recorder,
            Ethernet.MAX_FRAME_SIZE_BYTES, "test0")]
        messages_to_transmit1 = [Message(self.player, self.recorder,
            Ethernet.MAX_FRAME_SIZE_BYTES, "test1")]
        outlink = self.player.get_outlinks()[0]
        list_of_commands = {}
        transmission_command0 = {outlink: messages_to_transmit0}
        list_of_commands[tx_start_time0] = transmission_command0
        transmission_command1 = {outlink: messages_to_transmit1}
        list_of_commands[tx_start_time1] = transmission_command1
        self.player.load_transmission_commands(list_of_commands)
        simulate(until=float("inf"))
        received_messages = self.recorder.get_recorded_messages()
        all_messages_transmitted = (messages_to_transmit0 +
            messages_to_transmit1)
        self.assertEqual(all_messages_transmitted, received_messages)

    def test_8_messages_played__same_messages_recorded(self):
        # uncomment the next line to enable logging during this test
        #simlogging.logger.propagate = True
        outlink = self.player.get_outlinks()[0]
        transmission_start_times = range(8)
        all_messages_to_transmit = []
        list_of_commands = {}
        for time in transmission_start_times:
            transmission_command = {}
            messages_to_transmit = [Message(self.player, self.recorder,
                Ethernet.MAX_FRAME_SIZE_BYTES, "test")]
            all_messages_to_transmit.extend(messages_to_transmit)
            transmission_command[outlink] = messages_to_transmit
            list_of_commands[time] = transmission_command
        self.player.load_transmission_commands(list_of_commands)
        simulate(until=float("inf"))
        received_messages = self.recorder.get_recorded_messages()
        self.assertEqual(set(all_messages_to_transmit), set(received_messages))

    def test_8_messages_played__messages_recorded_same_order(self):
        # uncomment the next line to enable logging during this test
        #simlogging.logger.propagate = True
        outlink = self.player.get_outlinks()[0]
        transmission_start_times = range(8)
        all_messages_to_transmit = []
        list_of_commands = {}
        for time in transmission_start_times:
            transmission_command = {}
            messages_to_transmit = [Message(self.player, self.recorder,
                Ethernet.MAX_FRAME_SIZE_BYTES, "test")]
            all_messages_to_transmit.extend(messages_to_transmit)
            transmission_command[outlink] = messages_to_transmit
            list_of_commands[time] = transmission_command
        self.player.load_transmission_commands(list_of_commands)
        simulate(until=float("inf"))
        received_messages = self.recorder.get_recorded_messages()
        self.assertEqual(all_messages_to_transmit, received_messages)

    def test_3_batches_of_2_messages_played__equals_messages_recorded(self):
        # uncomment the next line to enable logging during this test
        #simlogging.logger.propagate = True
        tx_start_time0, tx_start_time1, tx_start_time2 = 0, 1, 2
        messages_to_transmit0 = [
            Message(self.player, self.recorder,
            Ethernet.MAX_FRAME_SIZE_BYTES, "batch 0 msg 0"),
            Message(self.player, self.recorder,
            Ethernet.MAX_FRAME_SIZE_BYTES, "batch 0 msg 1"),
            ]
        messages_to_transmit1 = [
            Message(self.player, self.recorder,
            Ethernet.MAX_FRAME_SIZE_BYTES, "batch 1 msg 0"),
            Message(self.player, self.recorder,
            Ethernet.MAX_FRAME_SIZE_BYTES, "batch 1 msg 1"),
            ]
        messages_to_transmit2 = [
            Message(self.player, self.recorder,
            Ethernet.MAX_FRAME_SIZE_BYTES, "batch 2 msg 0"),
            Message(self.player, self.recorder,
            Ethernet.MAX_FRAME_SIZE_BYTES, "batch 2 msg 1"),
            ]
        outlink = self.player.get_outlinks()[0]
        list_of_commands = {}
        transmission_command0 = {outlink: messages_to_transmit0}
        list_of_commands[tx_start_time0] = transmission_command0
        transmission_command1 = {outlink: messages_to_transmit1}
        list_of_commands[tx_start_time1] = transmission_command1
        transmission_command2 = {outlink: messages_to_transmit2}
        list_of_commands[tx_start_time2] = transmission_command2
        self.player.load_transmission_commands(list_of_commands)
        simulate(until=float("inf"))
        received_messages = self.recorder.get_recorded_messages()
        all_messages_transmitted = (messages_to_transmit0 +
            messages_to_transmit1 + messages_to_transmit2)
        self.assertEqual(all_messages_transmitted, received_messages)


class TestMessagePlaybackDeviceToTwoRecorders(unittest.TestCase):

    def setUp(self):
        """
        Set up the following network:

        +--------+      +-----------+
        |        | ---> | recorder1 |
        |        |      +-----------+
        | player |
        |        |      +-----------+
        |        | ---> | recorder2 |
        +--------+      +-----------+
        """
        self.player = MessagePlaybackDevice("player")
        self.recorder1 = MessageRecordingDevice("recorder1")
        self.recorder2 = MessageRecordingDevice("recorder2")
        self.link_Mbps = 100
        self.link_propagation_delay_us = 3
        link_player_recorder1 = Link(self.link_Mbps,
            self.link_propagation_delay_us)
        self.player.connect_outlink(link_player_recorder1)
        self.recorder1.connect_inlink(link_player_recorder1)
        link_player_recorder2 = Link(self.link_Mbps,
            self.link_propagation_delay_us)
        self.player.connect_outlink(link_player_recorder2)
        self.recorder2.connect_inlink(link_player_recorder2)
        # initialize SimPy
        initialize()
        for device in [self.player, self.recorder1, self.recorder2]:
            activate(device, device.run(), at=0.0)

    def tearDown(self):
        simlogging.logger.propagate = False

    def test_1_message_per_outlink__each_recorder_gets_correct_message(self):
        # uncomment the next line to enable logging during this test
        #simlogging.logger.propagate = True
        tx_start_time1, tx_start_time2 = range(2)
        messages_to_transmit1 = [Message(self.player, self.recorder1,
            Ethernet.MAX_FRAME_SIZE_BYTES, "message for recorder1")]
        messages_to_transmit2 = [Message(self.player, self.recorder2,
            Ethernet.MAX_FRAME_SIZE_BYTES, "message for recorder2")]
        outlink1 = self.player.get_outlinks()[0]
        outlink2 = self.player.get_outlinks()[1]
        list_of_commands = {}
        transmission_command1 = {outlink1: messages_to_transmit1}
        list_of_commands[tx_start_time1] = transmission_command1
        transmission_command2 = {outlink2: messages_to_transmit2}
        list_of_commands[tx_start_time2] = transmission_command2
        self.player.load_transmission_commands(list_of_commands)
        simulate(until=float("inf"))
        received_messages1 = self.recorder1.get_recorded_messages()
        self.assertEqual(messages_to_transmit1, received_messages1)
        received_messages2 = self.recorder2.get_recorded_messages()
        self.assertEqual(messages_to_transmit2, received_messages2)


class TestMasterToSwitchToRecorder(unittest.TestCase):

    def setUp(self):
        """
        Set up the following network:

        +--------+      +--------+      +----------+
        | master | ---> | switch | ---> | recorder |
        +--------+      +--------+      +----------+
        """
        self.switch = Switch("test switch")
        self.recorder = MessageRecordingDevice("recorder")
        # configured elementary cycle duration in microseconds
        self.EC_duration_us = 10 ** 9
        self.master = Master("test master", [self.recorder],
            self.EC_duration_us)
        link_master_switch = Link(100, 0)
        link_switch_recorder = Link(100, 0)
        self.master.connect_outlink(link_master_switch)
        self.switch.connect_inlink(link_master_switch)
        self.switch.connect_outlink(link_switch_recorder)
        self.recorder.connect_inlink(link_switch_recorder)
        # initialize SimPy
        initialize()
        for device in [self.master, self.switch, self.recorder]:
            activate(device, device.run(), at=0.0)

    def tearDown(self):
        simlogging.logger.propagate = False

    def test_1EC_simulated__record_1_msg(self):
        # uncomment the next line to enable logging during this test
        #simlogging.logger.propagate = True
        simulate(until=self.EC_duration_us)
        received_messages = self.recorder.get_recorded_messages()
        self.assertEqual(len(received_messages), 1)

    def test_2EC_simulated__record_2_msg(self):
        # uncomment the next line to enable logging during this test
        #simlogging.logger.propagate = True
        simulate(until=2 * self.EC_duration_us)
        received_messages = self.recorder.get_recorded_messages()
        self.assertEqual(len(received_messages), 2)

    def test_3EC_simulated__record_3_msg(self):
        # uncomment the next line to enable logging during this test
        #simlogging.logger.propagate = True
        simulate(until=3 * self.EC_duration_us)
        received_messages = self.recorder.get_recorded_messages()
        self.assertEqual(len(received_messages), 3)


if __name__ == '__main__':
    unittest.main()
