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

    def test__message_played__equals_message_recorded(self):
        # uncomment the next line to enable logging during this test
        #simlogging.logger.propagate = True
        tx_start_time = 0
        message_size_bytes = Ethernet.MAX_FRAME_SIZE_BYTES
        messages_to_transmit = [Message(self.player, self.recorder,
            message_size_bytes, "test")]
        outlink = self.player.get_outlinks()[0]
        transmissions = [(tx_start_time, messages_to_transmit, outlink)]
        self.player.load_transmissions(transmissions)
        # start simulation
        simulate(until=1000)
        received_messages = self.recorder.recorded_messages[0][1]
        self.assertEqual(messages_to_transmit, received_messages)

    def test__message_played__arrives_when_expected(self):
        # uncomment the next line to enable logging during this test
        #simlogging.logger.propagate = True
        tx_start_time = 0
        message_size_bytes = 1526
        messages_to_transmit = [Message(self.player, self.recorder,
            message_size_bytes, "test")]
        outlink = self.player.get_outlinks()[0]
        transmissions = [(tx_start_time, messages_to_transmit, outlink)]
        self.player.load_transmissions(transmissions)
        # start simulation
        simulate(until=1000)
        timestamp = self.recorder.recorded_messages[0][0]
        BITS_PER_BYTE = 8
        # time it takes the message to arrive at recorder in microseconds
        time_to_destination_in_us = (message_size_bytes * BITS_PER_BYTE /
            float(self.link_Mbps) + self.link_propagation_delay_us)
        expected_timestamp = time_to_destination_in_us
        self.assertEqual(timestamp, expected_timestamp)

    def test__2_messages_played__equals_2_messages_recorded(self):
        # uncomment the next line to enable logging during this test
        #simlogging.logger.propagate = True
        transmission_start_times = range(2)
        message_list = [[Message(self.player, self.recorder,
            Ethernet.MAX_FRAME_SIZE_BYTES,
            "test")] for i in transmission_start_times]
        transmissions = []
        for time, messages in zip(transmission_start_times, message_list):
            transmissions.append((time, messages,
                self.player.get_outlinks()[0]))
        self.player.load_transmissions(transmissions)
        # start simulation
        simulate(until=10000000)
        received_messages = [self.recorder.recorded_messages[i][1]
            for i in range(len(self.recorder.recorded_messages))]
        self.assertEqual(message_list, received_messages)


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
        EC_duration_us = Ethernet.MAX_FRAME_SIZE_BYTES * 10
        self.master = Master("test master", [self.recorder], EC_duration_us)
        link_master_switch = Link(10, 0)
        link_switch_recorder = Link(10, 0)
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

    def test_network__1EC_simulated__record_1_msg(self):
        # uncomment the next line to enable logging during this test
        #simlogging.logger.propagate = True
        simulate(until=1000000)
        timestamp, received_messages = self.recorder.recorded_messages[0]
        self.assertEqual(len(received_messages), 1)


if __name__ == '__main__':
    unittest.main()
