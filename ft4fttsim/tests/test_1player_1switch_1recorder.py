# author: David Gessner <davidges@gmail.com>

import unittest
from ft4fttsim.networking import *
from ft4fttsim.masterslave import *
from ft4fttsim.ethernet import *
from ft4fttsim import simlogging


class Test1Player1Switch1Recorder(unittest.TestCase):

    def setUp(self):
        """
        Set up the following network:

        +--------+      +--------+     +----------+
        | player | ---> | switch | --> | recorder |
        +--------+      +--------+     +----------+
        """
        self.player = MessagePlaybackDevice("player")
        self.switch = Switch("switch")
        self.recorder = MessageRecordingDevice("recorder")
        self.link_Mbps = 100
        self.link_propagation_delay_us = 3
        link_player_switch = Link(self.link_Mbps,
            self.link_propagation_delay_us)
        self.player.connect_outlink(link_player_switch)
        self.switch.connect_inlink(link_player_switch)
        link_switch_recorder = Link(self.link_Mbps,
            self.link_propagation_delay_us)
        self.switch.connect_outlink(link_switch_recorder)
        self.recorder.connect_inlink(link_switch_recorder)
        # initialize SimPy
        initialize()
        for device in [self.player, self.switch, self.recorder]:
            activate(device, device.run(), at=0.0)

    def tearDown(self):
        simlogging.logger.propagate = False


class TestSingleMessageDestinationIsNotList(Test1Player1Switch1Recorder):

    def setUp(self):
        """
        Set up the player sending a single message with a destination field
        that is NOT a list. Such messages are intended to model unicast
        addressing.
        """
        Test1Player1Switch1Recorder.setUp(self)
        self.tx_start_time = 0
        self.message_size_bytes = Ethernet.MAX_FRAME_SIZE_BYTES
        self.messages_to_transmit = [Message(self.player, self.recorder,
            self.message_size_bytes, "message with NO list as destination")]
        outlink = self.player.outlinks[0]
        transmission_command = {outlink: self.messages_to_transmit}
        list_of_commands = {self.tx_start_time: transmission_command}
        self.player.load_transmission_commands(list_of_commands)

    def test_message_with_no_iterable_destination_is_received(self):
        """
        Test that an equivalent message to the one transmitted by the player is
        received by the recorder. Note that we do not expect the same message
        because the switch creates a new message instance when forwarding the
        message from one link to the other.
        """
        # uncomment the next line to enable logging during this test
        #simlogging.logger.propagate = True
        # create a message instance whose destination field is NOT a list
        simulate(until=float("inf"))
        received_messages = self.recorder.recorded_messages
        self.assertTrue(
            self.messages_to_transmit[0].is_equivalent(received_messages[0]))


class TestSingleMessageDestinationIsList(Test1Player1Switch1Recorder):

    def setUp(self):
        """
        Set up the player sending a single message with a destination field
        that IS a list. Such messages are intended to model multicast
        addressing.
        """
        Test1Player1Switch1Recorder.setUp(self)
        self.tx_start_time = 0
        self.message_size_bytes = Ethernet.MAX_FRAME_SIZE_BYTES
        self.messages_to_transmit = [Message(self.player, [self.recorder],
            self.message_size_bytes, "message with list as destination")]
        outlink = self.player.outlinks[0]
        transmission_command = {outlink: self.messages_to_transmit}
        list_of_commands = {self.tx_start_time: transmission_command}
        self.player.load_transmission_commands(list_of_commands)

    def test_message_with_list_destination_is_received(self):
        """
        Test that an equivalent message to the one transmitted by the player is
        received by the recorder. Note that we do not expect the same message
        because the switch creates a new message instance when forwarding the
        message from one link to the other.
        """
        # uncomment the next line to enable logging during this test
        #simlogging.logger.propagate = True
        # create a message instance whose destination field is a list
        simulate(until=float("inf"))
        received_messages = self.recorder.recorded_messages
        self.assertTrue(
            self.messages_to_transmit[0].is_equivalent(received_messages[0]))


if __name__ == '__main__':
    unittest.main()
