# author: David Gessner <davidges@gmail.com>

import pytest

from ft4fttsim.ft4ftt import Master


@pytest.fixture
def master(env):
    new_master = Master(env, "master", 1, [], 10 ** 9, 1)
    return new_master
