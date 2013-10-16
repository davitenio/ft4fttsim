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
        link_player_recorder = Link(0)
        self.player.connect_outlink(link_player_recorder)
        self.recorder.connect_inlink(link_player_recorder)
        # initialize SimPy
        initialize()
        for device in [self.player, self.recorder]:
            activate(device, device.run(), at=0.0)

    def tearDown(self):
        simlogging.logger.propagate = False

    def test__1_message_played__1_message_recorded(self):
        # uncomment the next line to enable logging during this test
        #simlogging.logger.propagate = True
        tx_start_time = 0
        message_length = Ethernet.MAX_FRAME_LENGTH
        messages_to_transmit = [Message(self.player, self.recorder,
            message_length, "test")]
        outlink = self.player.get_outlinks()[0]
        transmissions = [(tx_start_time, messages_to_transmit, outlink)]
        self.player.load_transmissions(transmissions)
        # start simulation
        simulate(until=10000000)
        received_messages = self.recorder.recorded_messages[0][1]
        self.assertEqual(messages_to_transmit, received_messages)

    def test__2_messages_played__2_messages_recorded(self):
        # uncomment the next line to enable logging during this test
        #simlogging.logger.propagate = True
        transmission_start_times = range(2)
        message_list = [[Message(self.player, self.recorder,
            Ethernet.MAX_FRAME_LENGTH,
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
        EC_length = Ethernet.MAX_FRAME_LENGTH * 10
        self.master = Master("test master", [self.recorder], EC_length)
        link_master_switch = Link(0)
        link_switch_recorder = Link(0)
        self.master.connect_outlink(link_master_switch)
        self.switch.connect_inlink(link_master_switch)
        self.switch.connect_outlink(link_switch_recorder)
        self.recorder.connect_inlink(link_switch_recorder)
        # initialize SimPy
        initialize()
        for device in [self.master, self.switch, self.recorder]:
            activate(device, device.run(), at=0.0)

    def test_network__1EC_simulated__record_1_msg(self):
        simulate(until=self.master.EC_length)
        timestamp, received_messages = self.recorder.recorded_messages[0]
        self.assertEqual(len(received_messages), 1)


if __name__ == '__main__':
    unittest.main()
