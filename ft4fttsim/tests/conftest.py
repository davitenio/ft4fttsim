# author: David Gessner <davidges@gmail.com>

import pytest


@pytest.fixture
def env():
    import simpy
    import ft4fttsim.simlogging
    new_env = simpy.Environment()
    ft4fttsim.simlogging.env = new_env
    return new_env


@pytest.fixture(params=[(10, 3), (100, 0), (1000, 9)])
def link(env, request):
    from ft4fttsim.networking import Link
    Mbps, delay = request.param
    return Link(env, megabits_per_second=Mbps, propagation_delay_us=delay)
