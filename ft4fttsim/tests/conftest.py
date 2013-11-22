# author: David Gessner <davidges@gmail.com>

import pytest


@pytest.fixture
def env():
    import simpy
    import ft4fttsim.simlogging
    new_env = simpy.Environment()
    ft4fttsim.simlogging.env = new_env
    return new_env


@pytest.fixture
def switch2(env):
    from ft4fttsim.networking import Switch
    return Switch(env, "switch", 2)


@pytest.fixture
def switch4(env):
    from ft4fttsim.networking import Switch
    return Switch(env, "switch4", num_ports=4)


@pytest.fixture
def recorder(env):
    from ft4fttsim.networking import MessageRecordingDevice
    recorder = MessageRecordingDevice(env, "recorder", 1)
    return recorder


@pytest.fixture(params=range(4))
def master(request, env, recorder):
    from ft4fttsim.master import Master
    # number of trigger messages per elementary cycle
    num_TMs_per_EC = request.param
    # configured elementary cycle duration in microseconds
    EC_duration_us = 10 ** 9
    new_master = Master(env, "master", 1, [recorder], EC_duration_us,
                        num_TMs_per_EC)
    return new_master
