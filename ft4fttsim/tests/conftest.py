# author: David Gessner <davidges@gmail.com>

import pytest
import simpy

import ft4fttsim.simlogging


@pytest.fixture
def env():
    new_env = simpy.Environment()
    ft4fttsim.simlogging.env = new_env
    return new_env
