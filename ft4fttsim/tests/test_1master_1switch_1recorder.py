# author: David Gessner <davidges@gmail.com>

import pytest
from ft4fttsim.networking import *
from ft4fttsim.masterslave import *
from ft4fttsim.ethernet import *


class Test1Master1Switch1Recorder:

    @pytest.fixture(autouse=True,
        params=range(5))
    def set_up_network(self, env, request):
        """
        Set up the following network:

        +--------+      +--------+      +----------+
        | master | ---> | switch | ---> | recorder |
        +--------+      +--------+      +----------+
        """
        self.env = env
        self.num_TMs_per_EC = request.param
        self.switch = Switch(self.env, "test switch")
        self.recorder = MessageRecordingDevice(self.env, "recorder")
        # configured elementary cycle duration in microseconds
        self.EC_duration_us = 10 ** 9
        self.master = Master(self.env, "test master", [self.recorder],
            self.EC_duration_us, self.num_TMs_per_EC)
        link_master_switch = Link(self.env, 100, 0)
        link_switch_recorder = Link(self.env, 100, 0)
        self.master.connect_outlink(link_master_switch)
        self.switch.connect_inlink(link_master_switch)
        self.switch.connect_outlink(link_switch_recorder)
        self.recorder.connect_inlink(link_switch_recorder)

    @pytest.mark.parametrize("num_ECs", range(1, 4))
    def test_num_ECs_simulated__record_correct_number_of_messages(
            self, num_ECs):
        """
        Test that if we simulate for the duration of num_ECs elementary
        cycles, the recorder records num_ECs * self.num_TMs_per_EC
        messages.
        """
        self.env.run(until=num_ECs * self.EC_duration_us)
        received_messages = self.recorder.recorded_messages
        assert len(received_messages) == num_ECs * self.num_TMs_per_EC
