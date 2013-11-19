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
