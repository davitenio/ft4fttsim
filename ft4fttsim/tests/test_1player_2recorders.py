# author: David Gessner <davidges@gmail.com>

import unittest
from ft4fttsim.networking import *
from ft4fttsim.masterslave import *
from ft4fttsim.ethernet import *


class Test1Player2Recorder(unittest.TestCase):

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
        self.env = simpy.Environment()
        self.player = MessagePlaybackDevice(self.env, "player")
        self.recorder1 = MessageRecordingDevice(self.env, "recorder1")
        self.recorder2 = MessageRecordingDevice(self.env, "recorder2")
        self.link_Mbps = 100
        self.link_propagation_delay_us = 3
        link_player_recorder1 = Link(self.env, self.link_Mbps,
            self.link_propagation_delay_us)
        self.player.connect_outlink(link_player_recorder1)
        self.recorder1.connect_inlink(link_player_recorder1)
        link_player_recorder2 = Link(self.env, self.link_Mbps,
            self.link_propagation_delay_us)
        self.player.connect_outlink(link_player_recorder2)
        self.recorder2.connect_inlink(link_player_recorder2)


class TestOneMessagePerOutlink(Test1Player2Recorder):

    def setUp(self):
        """
        Set up player sending a separate message at a different instant of time
        to each recorder.
        """
        Test1Player2Recorder.setUp(self)
        tx_start_time1, tx_start_time2 = range(2)
        self.messages_to_transmit1 = [Message(self.env, self.player,
            self.recorder1, Ethernet.MAX_FRAME_SIZE_BYTES,
            "message for recorder1")]
        self.messages_to_transmit2 = [Message(self.env, self.player,
            self.recorder2, Ethernet.MAX_FRAME_SIZE_BYTES,
            "message for recorder2")]
        outlink1 = self.player.outlinks[0]
        outlink2 = self.player.outlinks[1]
        list_of_commands = {}
        transmission_command1 = {outlink1: self.messages_to_transmit1}
        list_of_commands[tx_start_time1] = transmission_command1
        transmission_command2 = {outlink2: self.messages_to_transmit2}
        list_of_commands[tx_start_time2] = transmission_command2
        self.player.load_transmission_commands(list_of_commands)

    def test_recorder1_gets_correct_message(self):
        self.env.run(until=float("inf"))
        received_messages1 = self.recorder1.recorded_messages
        assert self.messages_to_transmit1 == received_messages1

    def test_recorder2_gets_correct_message(self):
        self.env.run(until=float("inf"))
        received_messages2 = self.recorder2.recorded_messages
        assert self.messages_to_transmit2 == received_messages2


if __name__ == '__main__':
    unittest.main()
