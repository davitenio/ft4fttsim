# author: David Gessner <davidges@gmail.com>

import pytest


@pytest.fixture
def master(env):
    from ft4fttsim.ft4ftt import Master
    new_master = Master(env, "master", 1, [], 10 ** 9, 1)
    return new_master
