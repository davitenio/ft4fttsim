# author: David Gessner <davidges@gmail.com>

import pytest


@pytest.fixture
def env():
    import simpy
    return simpy.Environment()
