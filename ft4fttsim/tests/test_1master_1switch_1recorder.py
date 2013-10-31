# author: David Gessner <davidges@gmail.com>

import unittest
from ft4fttsim.networking import *
from ft4fttsim.masterslave import *
from ft4fttsim.ethernet import *
from ft4fttsim import simlogging


class Test1Master1Switch1Recorder(unittest.TestCase):

    def setUp(self):
        """
        Set up the following network:

        +--------+      +--------+      +----------+
        | master | ---> | switch | ---> | recorder |
        +--------+      +--------+      +----------+
        """
        self.env = simpy.Environment()
        self.switch = Switch(self.env, "test switch")
        self.recorder = MessageRecordingDevice(self.env, "recorder")
        # configured elementary cycle duration in microseconds
        self.EC_duration_us = 10 ** 9
        self.master = Master(self.env, "test master", [self.recorder],
            self.EC_duration_us)
        link_master_switch = Link(self.env, 100, 0)
        link_switch_recorder = Link(self.env, 100, 0)
        self.master.connect_outlink(link_master_switch)
        self.switch.connect_inlink(link_master_switch)
        self.switch.connect_outlink(link_switch_recorder)
        self.recorder.connect_inlink(link_switch_recorder)
        simlogging.env = self.env

    def tearDown(self):
        simlogging.logger.propagate = False

    def test_1EC_simulated__record_1_msg(self):
        """
        Test that if we simulate for the duration of one elementary cycle, the
        recorder records one message.
        """
        # uncomment the next line to enable logging during this test
        #simlogging.logger.propagate = True
        self.env.run(until=self.EC_duration_us)
        received_messages = self.recorder.recorded_messages
        self.assertEqual(len(received_messages), 1)

    def test_2EC_simulated__record_2_msg(self):
        """
        Test that if we simulate for the duration of two elementary cycles, the
        recorder records two messages.
        """
        # uncomment the next line to enable logging during this test
        #simlogging.logger.propagate = True
        self.env.run(until=2 * self.EC_duration_us)
        received_messages = self.recorder.recorded_messages
        self.assertEqual(len(received_messages), 2)

    def test_3EC_simulated__record_3_msg(self):
        """
        Test that if we simulate for the duration of 3 elementary cycles, the
        recorder records 3 messages.
        """
        # uncomment the next line to enable logging during this test
        #simlogging.logger.propagate = True
        self.env.run(until=3 * self.EC_duration_us)
        received_messages = self.recorder.recorded_messages
        self.assertEqual(len(received_messages), 3)


if __name__ == '__main__':
    unittest.main()
