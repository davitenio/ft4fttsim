# author: David Gessner <davidges@gmail.com>
"""
Perform tests under the following network:

  +--------+       +---------------+
  | player 0 ----- 0 FT4FTT switch |
  +--------+       |               |
                   |  +---0----+   |
                   |  | master |   |
                   |  +--------+   |
                   +---------------+

"""

from unittest.mock import sentinel

import pytest

from ft4fttsim.networking import Link, Message, MessagePlaybackDevice
from ft4fttsim.ft4ftt import SyncStreamConfig, MessageType
from ft4fttsim.ft4ftt import FT4FTTSwitch


@pytest.fixture
def update_request_message(env, master):
    new_sync_config = SyncStreamConfig(
        transmission_time_ECs=1,
        deadline_ECs=5,
        period_ECs=20,
        offset_ECs=123
    )
    update_request_data = ("synchronous stream 1", new_sync_config)
    new_update_request_message = Message(
        env, sentinel.dummy_source, master, 1234, MessageType.UPDATE_REQUEST,
        update_request_data)
    return new_update_request_message


@pytest.fixture
def player(env, update_request_message):
    new_player = MessagePlaybackDevice(env, "player", 1)
    messages = [update_request_message]
    new_player.load_transmission_commands(
        {
            0: {new_player.ports[0]: messages}
        }
    )
    return new_player


@pytest.fixture
def switch(env, master, player):
    new_switch = FT4FTTSwitch(env, "FT4FTT switch", 1, master)
    Link(env, player.ports[0], new_switch.ports[0], 100, 5)
    return new_switch


@pytest.mark.usefixtures("switch")
def test_update_request(env, master, update_request_message):
    env.run(until=master.EC_duration_us * 1)
    assert master.sync_requirements == dict([update_request_message.data])
