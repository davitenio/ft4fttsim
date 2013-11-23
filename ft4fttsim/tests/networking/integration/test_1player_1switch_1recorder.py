# author: David Gessner <davidges@gmail.com>
"""
Execute tests under the following network:

+-------------+ link1 +---------+ link2 +-----------+
| player_rec1 | ----> | switch2 | ----> | recorder1 |
+-------------+       +---------+       +-----------+

"""


import pytest
from ft4fttsim.tests.networking.fixturehelper import make_link
from ft4fttsim.tests.networking.fixturehelper import LINK_CONFIGS


@pytest.fixture
def switch2(env):
    from ft4fttsim.networking import Switch
    return Switch(env, "switch", 2)


@pytest.fixture(params=LINK_CONFIGS)
def link1(env, request, player_rec1, switch2):
    config = request.param
    new_link = make_link(
        config, env, player_rec1.ports[0], switch2.ports[0])
    return new_link


@pytest.fixture(params=LINK_CONFIGS)
def link2(env, request, switch2, recorder1):
    config = request.param
    new_link = make_link(
        config, env, switch2.ports[1], recorder1.ports[0])
    return new_link


@pytest.mark.usefixtures("link1", "link2")
def test_messages_played__equals_messages_recorded(
        env, player_rec1, recorder1):
    """
    Test that the recorder1 receives the messages transmitted by player_rec1.

    """
    env.run(until=float("inf"))
    assert player_rec1.messages_to_transmit == recorder1.recorded_messages
