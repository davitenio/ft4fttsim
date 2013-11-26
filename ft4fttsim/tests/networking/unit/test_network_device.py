# author: David Gessner <davidges@gmail.com>

import pytest
from ft4fttsim.networking import NetworkDevice


@pytest.fixture
def new_device(env):
    return NetworkDevice(env, "new device", 1)


def test_instruct_transmission_through_non_existing_port__raise_exception(
        new_device):
    from ft4fttsim.networking import FT4FTTSimException
    from unittest.mock import sentinel
    with pytest.raises(FT4FTTSimException):
        next(new_device.instruct_transmission(
            sentinel.message, sentinel.bogus_port))


@pytest.mark.parametrize("num_ports", range(1, 5))
def test_repr_of_last_port(env, num_ports):
    device = NetworkDevice(env, "foo", num_ports)
    assert str(device.ports[-1]) == "foo-port{}".format(num_ports - 1)
