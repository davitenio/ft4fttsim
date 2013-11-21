# author: David Gessner <davidges@gmail.com>


import pytest
from ft4fttsim.master import Master, SyncStreamConfig
from ft4fttsim.networking import Message
from ft4fttsim.slave import Slave
from unittest.mock import sentinel


@pytest.mark.parametrize(
    "num_ports, num_slaves",
    [(1, 1), (2, 1), (1, 2)]
)
def test_master_constructor_does_not_raise_exception(
        env, num_ports, num_slaves):
    slaves = []
    for i in range(num_slaves):
        new_slave = Slave(env, "slave {}".format(i), 1)
        slaves.append(new_slave)
    # Invoking the master constructor should not raise exception or cause any
    # error.
    Master(env, "FTT master", num_ports, slaves, 1234)


@pytest.fixture
def master(env):
    new_master = Master(env, "FTT master", 1, [], 123)
    return new_master


def test_new_master__sync_requirements_is_empty(master):
    assert master.sync_requirements == {}


@pytest.fixture
def update_request_message(env, master):
    new_sync_config = SyncStreamConfig(
        transmission_time_ECs=1,
        deadline_ECs=5,
        period_ECs=20,
        offset_ECs=1
    )
    update_request_data = ("synchronous stream 1", new_sync_config)
    new_update_request_message = Message(
        env, sentinel.dummy_source, master, 1234, Message.Type.UPDATE_REQUEST,
        update_request_data)
    return new_update_request_message


def test_process_update_request_message(master, update_request_message):
    master.process_update_request_message(update_request_message)
    assert master.sync_requirements == dict([update_request_message.data])
