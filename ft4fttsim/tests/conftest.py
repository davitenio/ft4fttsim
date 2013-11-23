# author: David Gessner <davidges@gmail.com>

import pytest


@pytest.fixture
def env():
    import simpy
    import ft4fttsim.simlogging
    new_env = simpy.Environment()
    ft4fttsim.simlogging.env = new_env
    return new_env
