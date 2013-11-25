# author: David Gessner <davidges@gmail.com>

import pytest

from ft4fttsim.ft4ftt import Master
from ft4fttsim.networking import MessageRecordingDevice


@pytest.fixture
def recorder(env):
    recorder = MessageRecordingDevice(env, "recorder", 1)
    return recorder


@pytest.fixture(params=range(4))
def master(request, env, recorder):
    # number of trigger messages per elementary cycle
    num_TMs_per_EC = request.param
    # configured elementary cycle duration in microseconds
    EC_duration_us = 10 ** 9
    new_master = Master(env, "master", 1, [recorder], EC_duration_us,
                        num_TMs_per_EC)
    return new_master
