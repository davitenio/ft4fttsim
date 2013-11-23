# author: David Gessner <davidges@gmail.com>
"""
Perform tests under the following network:

+--------+ link1 +---------+ link2 +----------+
| master | ----> | switch2 | ----> | recorder |
+--------+       +---------+       +----------+
"""

import pytest
from ft4fttsim.tests.networking.fixturehelper import make_link
from ft4fttsim.tests.networking.fixturehelper import LINK_CONFIGS


@pytest.fixture
def switch2(env):
    from ft4fttsim.networking import Switch
    return Switch(env, "switch", 2)


@pytest.fixture(params=LINK_CONFIGS)
def link1(env, request, master, switch2):
    config = request.param
    new_link = make_link(config, env, master.ports[0],
                         switch2.ports[0])
    return new_link


@pytest.fixture(params=LINK_CONFIGS)
def link2(env, request, switch2, recorder):
    config = request.param
    new_link = make_link(config, env, switch2.ports[1],
                         recorder.ports[0])
    return new_link


@pytest.mark.usefixtures("link1", "link2")
@pytest.mark.parametrize("num_ECs", range(1, 4))
def test_num_ECs_simulated__record_correct_number_of_messages(
        env, master, recorder, num_ECs):
    """
    Test that the recorder records master.num_TMs_per_EC trigger messages in
    each elementary cycle.
    """
    env.run(until=num_ECs * master.EC_duration_us)
    received_messages = recorder.recorded_messages
    assert len(received_messages) == num_ECs * master.num_TMs_per_EC
