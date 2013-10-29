# author: David Gessner <davidges@gmail.com>

import unittest
from ft4fttsim.networking import *
from ft4fttsim.masterslave import *
from ft4fttsim.ethernet import *
from ft4fttsim import simlogging


class Test1Player1Switch2Recorders(unittest.TestCase):

    def setUp(self):
        """
        Set up the following network:

                        +--------+     +-----------+
                        |        | --> | recorder1 |
        +--------+      |        |     +-----------+
        | player | ---> | switch |
        +--------+      |        |     +-----------+
                        |        | --> | recorder2 |
                        +--------+     +-----------+
        """
        self.player = MessagePlaybackDevice("player")
        self.switch = Switch("switch")
        self.recorder1 = MessageRecordingDevice("recorder1")
        self.recorder2 = MessageRecordingDevice("recorder2")
        self.link_Mbps = 100
        self.link_propagation_delay_us = 3
        link_player_switch = Link(self.link_Mbps,
            self.link_propagation_delay_us)
        self.player.connect_outlink(link_player_switch)
        self.switch.connect_inlink(link_player_switch)
        link_switch_recorder1 = Link(self.link_Mbps,
            self.link_propagation_delay_us)
        self.switch.connect_outlink(link_switch_recorder1)
        self.recorder1.connect_inlink(link_switch_recorder1)
        link_switch_recorder2 = Link(self.link_Mbps,
            self.link_propagation_delay_us)
        self.switch.connect_outlink(link_switch_recorder2)
        self.recorder2.connect_inlink(link_switch_recorder2)
        # initialize SimPy
        initialize()
        for device in [self.player, self.switch, self.recorder1,
        self.recorder2]:
            activate(device, device.run(), at=0.0)

    def tearDown(self):
        simlogging.logger.propagate = False


class TestSingleMessageForRecorder1(Test1Player1Switch2Recorders):

    def setUp(self):
        """
        Set up the player sending a single message to recorder 1.
        """
        Test1Player1Switch2Recorders.setUp(self)
        tx_start_time = 0
        message_size_bytes = Ethernet.MAX_FRAME_SIZE_BYTES
        self.messages_to_transmit = [Message(self.player, self.recorder1,
            message_size_bytes, "message for recorder1")]
        outlink = self.player.outlinks[0]
        transmission_command = {outlink: self.messages_to_transmit}
        list_of_commands = {tx_start_time: transmission_command}
        self.player.load_transmission_commands(list_of_commands)

    def test_message_is_received_by_recorder1(self):
        """
        Test that recorder1 receives the message.
        """
        # uncomment the next line to enable logging during this test
        #simlogging.logger.propagate = True
        simulate(until=float("inf"))
        received_messages = self.recorder1.get_recorded_messages()
        self.assertTrue(
            self.messages_to_transmit[0].is_equivalent(received_messages[0]))

    def test_no_message_is_received_by_recorder2(self):
        """
        Test that recorder2 does not receive any message.
        """
        # uncomment the next line to enable logging during this test
        #simlogging.logger.propagate = True
        simulate(until=float("inf"))
        received_messages = self.recorder2.get_recorded_messages()
        self.assertEqual(len(received_messages), 0)


class TestSingleMessageForRecorder2(Test1Player1Switch2Recorders):

    def setUp(self):
        """
        Set up the player sending a single message to recorder 2.
        """
        Test1Player1Switch2Recorders.setUp(self)
        tx_start_time = 0
        message_size_bytes = Ethernet.MAX_FRAME_SIZE_BYTES
        self.messages_to_transmit = [Message(self.player, self.recorder2,
            message_size_bytes, "message for recorder2")]
        outlink = self.player.outlinks[0]
        transmission_command = {outlink: self.messages_to_transmit}
        list_of_commands = {tx_start_time: transmission_command}
        self.player.load_transmission_commands(list_of_commands)

    def test_message_is_received_by_recorder2(self):
        """
        Test that recorder2 receives the forwarded message.
        """
        # uncomment the next line to enable logging during this test
        #simlogging.logger.propagate = True
        simulate(until=float("inf"))
        received_messages = self.recorder2.get_recorded_messages()
        self.assertTrue(
            self.messages_to_transmit[0].is_equivalent(received_messages[0]))

    def test_no_message_is_received_by_recorder1(self):
        """
        Test that recorder1 does not receive any message.
        """
        # uncomment the next line to enable logging during this test
        #simlogging.logger.propagate = True
        simulate(until=float("inf"))
        received_messages = self.recorder1.get_recorded_messages()
        self.assertEqual(len(received_messages), 0)


class TestSingleMessageForRecorder1AndRecorder2(Test1Player1Switch2Recorders):

    def setUp(self):
        """
        Set up the player sending a single multicast message to recorder1 and
        recorder2.
        """
        Test1Player1Switch2Recorders.setUp(self)
        tx_start_time = 0
        message_size_bytes = Ethernet.MAX_FRAME_SIZE_BYTES
        self.messages_to_transmit = [Message(self.player,
            [self.recorder1, self.recorder2],
            message_size_bytes, "message for recorder 1 and 2")]
        outlink = self.player.outlinks[0]
        transmission_command = {outlink: self.messages_to_transmit}
        list_of_commands = {tx_start_time: transmission_command}
        self.player.load_transmission_commands(list_of_commands)

    def test_equivalent_message_is_rx_by_recorder1(self):
        """
        Test that recorder1 receives the forwarded message.
        """
        # uncomment the next line to enable logging during this test
        #simlogging.logger.propagate = True
        simulate(until=float("inf"))
        received_messages = self.recorder1.get_recorded_messages()
        self.assertTrue(
            self.messages_to_transmit[0].is_equivalent(received_messages[0]))

    def test_equivalent_message_is_rx_by_recorder2(self):
        """
        Test that recorder2 receives the forwarded message.
        """
        # uncomment the next line to enable logging during this test
        #simlogging.logger.propagate = True
        simulate(until=float("inf"))
        received_messages = self.recorder2.get_recorded_messages()
        self.assertTrue(
            self.messages_to_transmit[0].is_equivalent(received_messages[0]))


if __name__ == '__main__':
    unittest.main()
