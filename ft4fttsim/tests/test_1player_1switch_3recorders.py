# author: David Gessner <davidges@gmail.com>

import unittest
from ft4fttsim.networking import *
from ft4fttsim.masterslave import *
from ft4fttsim.ethernet import *
from ft4fttsim import simlogging


class Test1Player1Switch3Recorders(unittest.TestCase):

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
                             |
                             v
                       +-----------+
                       | recorder3 |
                       +-----------+
        """
        self.env = simpy.Environment()
        self.player = MessagePlaybackDevice(self.env, "player")
        self.switch = Switch(self.env, "switch")
        self.recorder1 = MessageRecordingDevice(self.env, "recorder1")
        self.recorder2 = MessageRecordingDevice(self.env, "recorder2")
        self.recorder3 = MessageRecordingDevice(self.env, "recorder3")
        self.link_Mbps = 100
        self.link_propagation_delay_us = 3
        link_player_switch = Link(self.env, self.link_Mbps,
            self.link_propagation_delay_us)
        self.player.connect_outlink(link_player_switch)
        self.switch.connect_inlink(link_player_switch)
        link_switch_recorder1 = Link(self.env, self.link_Mbps,
            self.link_propagation_delay_us)
        self.switch.connect_outlink(link_switch_recorder1)
        self.recorder1.connect_inlink(link_switch_recorder1)
        link_switch_recorder2 = Link(self.env, self.link_Mbps,
            self.link_propagation_delay_us)
        self.switch.connect_outlink(link_switch_recorder2)
        self.recorder2.connect_inlink(link_switch_recorder2)
        link_switch_recorder3 = Link(self.env, self.link_Mbps,
            self.link_propagation_delay_us)
        self.switch.connect_outlink(link_switch_recorder3)
        self.recorder3.connect_inlink(link_switch_recorder3)

    def tearDown(self):
        simlogging.logger.propagate = False


class TestSingleMessageForRecorder1AndRecorder3(Test1Player1Switch3Recorders):

    def setUp(self):
        """
        Set up player sending a single multicast message to recorder1 and
        recorder3.
        """
        Test1Player1Switch3Recorders.setUp(self)
        tx_start_time = 0
        message_size_bytes = Ethernet.MAX_FRAME_SIZE_BYTES
        self.messages_to_transmit = [Message(self.env, self.player,
            [self.recorder1, self.recorder3],
            message_size_bytes, "message for recorder 1 and 3")]
        outlink = self.player.outlinks[0]
        transmission_command = {outlink: self.messages_to_transmit}
        list_of_commands = {tx_start_time: transmission_command}
        self.player.load_transmission_commands(list_of_commands)

    def test_message_is_received_by_recorder1(self):
        """
        Test that recorder1 receives the forwarded message.
        """
        # uncomment the next line to enable logging during this test
        #simlogging.logger.propagate = True
        self.env.run(until=float("inf"))
        received_messages = self.recorder1.recorded_messages
        self.assertTrue(
            self.messages_to_transmit[0].is_equivalent(received_messages[0]))

    def test_message_is_received_by_recorder3(self):
        """
        Test that recorder3 receives the forwarded message.
        """
        # uncomment the next line to enable logging during this test
        #simlogging.logger.propagate = True
        self.env.run(until=float("inf"))
        received_messages = self.recorder3.recorded_messages
        self.assertTrue(
            self.messages_to_transmit[0].is_equivalent(received_messages[0]))

    def test_no_message_is_received_by_recorder2(self):
        """
        Test that recorder2 does not receive the message.
        """
        # uncomment the next line to enable logging during this test
        #simlogging.logger.propagate = True
        self.env.run(until=float("inf"))
        received_messages = self.recorder2.recorded_messages
        self.assertNotIn(self.messages_to_transmit[0], received_messages)


if __name__ == '__main__':
    unittest.main()
