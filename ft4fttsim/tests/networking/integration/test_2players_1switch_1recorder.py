# author: David Gessner <davidges@gmail.com>
"""
Execute tests under the following network:

                    +---------+ link_r1  +-----------+
                    |         1 -------> 0 recorder1 |
+---------+ link_p1 |         |          +-----------+
| player1 0 ------> 0 switch3 |
+---------+         |         |
                    |         |
                    +---2-----+
                        ^
                        | link_p2
                   +----0----+
                   | player2 |
                   +---------+

"""

import pytest

from ft4fttsim.tests.networking.fixturehelper import make_link


@pytest.fixture
def switch3(env):
    from ft4fttsim.networking import Switch
    return Switch(env, "switch3", num_ports=3)


@pytest.fixture(params=[(1000, 123)])
def link_p1r1(env, request, player_rec1, switch3):
    config = request.param
    new_link = make_link(
        config, env, player_rec1.ports[0], switch3.ports[0])
    return new_link


@pytest.fixture(params=[(1000, 123)])
def link_r1(env, request, switch3, recorder1):
    config = request.param
    new_link = make_link(
        config, env, switch3.ports[1], recorder1.ports[0])
    return new_link


@pytest.fixture(params=[(1000, 123)])
def link_p2r1(env, request, player2_rec1, switch3):
    config = request.param
    new_link = make_link(
        config, env, player2_rec1.ports[0], switch3.ports[2])
    return new_link


@pytest.mark.usefixtures("link_p1r1", "link_p2r1", "link_r1")
def test_recorder1_receives_all_messages_from_player_rec1(
        env, player_rec1, recorder1):
    """
    Test recorder1 receives all messages from player_rec1.

    """
    env.run(until=float("inf"))
    received_messages = recorder1.recorded_messages
    print("recorder1.recorded_messages: " + str(received_messages))
    print("player_rec1.messages_to_transmit: " +
          str(player_rec1.messages_to_transmit))
    assert all(
        message in received_messages
        for message in player_rec1.messages_to_transmit
    )


@pytest.mark.usefixtures("link_p1r1", "link_p2r1", "link_r1")
def test_recorder1_receives_all_messages_from_player2_rec1(
        env, player2_rec1, recorder1):
    """
    Test recorder1 receives all messages from player2_rec1.

    """
    env.run(until=float("inf"))
    received_messages = recorder1.recorded_messages
    print(received_messages)
    print(player2_rec1.messages_to_transmit)
    assert all(
        message in received_messages
        for message in player2_rec1.messages_to_transmit
    )
