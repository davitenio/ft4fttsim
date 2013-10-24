# author: David Gessner <davidges@gmail.com>

import unittest
from ft4fttsim.networking import *
from ft4fttsim.masterslave import *
from ft4fttsim.ethernet import *
from ft4fttsim import simlogging


class Test2Players1Switch2Recorders(unittest.TestCase):

    def setUp(self):
        """
        Set up the following network:

                        +--------+     +-----------+
                        |        | --> | recorder1 |
       +---------+      |        |     +-----------+
       | player1 | ---> | switch |
       +---------+      |        |     +-----------+
                        |        | --> | recorder2 |
                        +--------+     +-----------+
                             ^
                             |
                       +---------+
                       | player2 |
                       +---------+
        """
        self.player1 = MessagePlaybackDevice("player1")
        self.player2 = MessagePlaybackDevice("player2")
        self.switch = Switch("switch")
        self.recorder1 = MessageRecordingDevice("recorder1")
        self.recorder2 = MessageRecordingDevice("recorder2")
        self.link_Mbps = 100
        self.link_propagation_delay_us = 3
        link_player1_switch = Link(self.link_Mbps,
            self.link_propagation_delay_us)
        self.player1.connect_outlink(link_player1_switch)
        self.switch.connect_inlink(link_player1_switch)
        link_player2_switch = Link(self.link_Mbps,
            self.link_propagation_delay_us)
        self.player2.connect_outlink(link_player2_switch)
        self.switch.connect_inlink(link_player2_switch)
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
        for device in [self.player1, self.player2, self.switch,
        self.recorder1, self.recorder2]:
            activate(device, device.run(), at=0.0)

    def tearDown(self):
        simlogging.logger.propagate = False


class Test2ParallelTransmissionPaths(Test2Players1Switch2Recorders):

    def setUp(self):
        """
        Set up player1 sending a message to recorder1 and player2
        simultaneously sending a message to recorder2.
        """
        Test2Players1Switch2Recorders.setUp(self)
        tx_start_time = 0
        message_size_bytes = Ethernet.MAX_FRAME_SIZE_BYTES

        self.messages_to_transmit1 = [Message(self.player1, self.recorder1,
            message_size_bytes, "message for rec1 from play1")]
        outlink1 = self.player1.get_outlinks()[0]
        transmission_command1 = {outlink1: self.messages_to_transmit1}
        list_of_commands1 = {tx_start_time: transmission_command1}
        self.player1.load_transmission_commands(list_of_commands1)

        self.messages_to_transmit2 = [Message(self.player2, self.recorder2,
            message_size_bytes, "message for rec2 from play2")]
        outlink2 = self.player2.get_outlinks()[0]
        transmission_command2 = {outlink2: self.messages_to_transmit2}
        list_of_commands2 = {tx_start_time: transmission_command2}
        self.player2.load_transmission_commands(list_of_commands2)

    def test_recorder1_receives_message_from_player1(self):
        """
        Test recorder1 receives the message from player1.
        """
        # uncomment the next line to enable logging during this test
        #simlogging.logger.propagate = True
        simulate(until=float("inf"))
        received_messages = self.recorder1.get_recorded_messages()
        self.assertTrue(
            self.messages_to_transmit1[0].is_equivalent(received_messages[0]))

    def test_recorder2_does_not_receive_message_from_player1(self):
        """
        Test recorder2 does not receive the message from player1.
        """
        # uncomment the next line to enable logging during this test
        #simlogging.logger.propagate = True
        simulate(until=float("inf"))
        received_messages = self.recorder2.get_recorded_messages()
        self.assertFalse(
            self.messages_to_transmit1[0].is_equivalent(received_messages[0]))

    def test_recorder2_receives_message_from_player2(self):
        """
        Test recorder2 receives the message from player2.
        """
        # uncomment the next line to enable logging during this test
        #simlogging.logger.propagate = True
        simulate(until=float("inf"))
        received_messages = self.recorder2.get_recorded_messages()
        self.assertTrue(
            self.messages_to_transmit2[0].is_equivalent(received_messages[0]))

    def test_recorder1_does_not_receive_message_from_player2(self):
        """
        Test recorder1 does not receive the message from player2.
        """
        # uncomment the next line to enable logging during this test
        #simlogging.logger.propagate = True
        simulate(until=float("inf"))
        received_messages = self.recorder1.get_recorded_messages()
        self.assertFalse(
            self.messages_to_transmit2[0].is_equivalent(received_messages[0]))


class TestSingleMessageForRecorder1(Test2Players1Switch2Recorders):

    def setUp(self):
        """
        Set up player1 sending a message to recorder1 and player2
        simultaneously also sending a message to recorder1.
        """
        Test2Players1Switch2Recorders.setUp(self)
        tx_start_time = 0
        message_size_bytes = Ethernet.MAX_FRAME_SIZE_BYTES

        self.messages_to_transmit1 = [Message(self.player1, self.recorder1,
            message_size_bytes, "message for rec1 from play1")]
        outlink1 = self.player1.get_outlinks()[0]
        transmission_command1 = {outlink1: self.messages_to_transmit1}
        list_of_commands1 = {tx_start_time: transmission_command1}
        self.player1.load_transmission_commands(list_of_commands1)

        self.messages_to_transmit2 = [Message(self.player2, self.recorder1,
            message_size_bytes, "message for rec1 from play2")]
        outlink2 = self.player2.get_outlinks()[0]
        transmission_command2 = {outlink2: self.messages_to_transmit2}
        list_of_commands2 = {tx_start_time: transmission_command2}
        self.player2.load_transmission_commands(list_of_commands2)

    def test_recorder1_receives_message_from_player1(self):
        """
        Test recorder1 receives the message from player1.
        """
        # uncomment the next line to enable logging during this test
        #simlogging.logger.propagate = True
        simulate(until=float("inf"))
        received_messages = self.recorder1.get_recorded_messages()
        self.assertTrue(
            self.messages_to_transmit1[0].is_equivalent(received_messages[0]))

    def test_recorder1_receives_exactly_2_messages(self):
        """
        Test recorder1 receives exactly two messages.
        """
        # uncomment the next line to enable logging during this test
        #simlogging.logger.propagate = True
        simulate(until=float("inf"))
        received_messages = self.recorder1.get_recorded_messages()
        self.assertEqual(len(received_messages), 2)

    def test_recorder2_receives_exactly_0_messages(self):
        """
        Test recorder2 receives exactly zero messages.
        """
        # uncomment the next line to enable logging during this test
        #simlogging.logger.propagate = True
        simulate(until=float("inf"))
        received_messages = self.recorder2.get_recorded_messages()
        self.assertEqual(len(received_messages), 0)

    def test_recorder1_receives_message_from_player2(self):
        """
        Test recorder1 receives the message from player2.
        """
        # uncomment the next line to enable logging during this test
        #simlogging.logger.propagate = True
        simulate(until=float("inf"))
        received_messages = self.recorder1.get_recorded_messages()
        self.assertTrue(
            self.messages_to_transmit2[0].is_equivalent(received_messages[0])
            or
            self.messages_to_transmit2[0].is_equivalent(received_messages[1]))


if __name__ == '__main__':
    unittest.main()
