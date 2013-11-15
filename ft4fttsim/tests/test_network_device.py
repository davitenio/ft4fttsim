# author: David Gessner <davidges@gmail.com>

import pytest


@pytest.fixture
def new_device(env):
    from ft4fttsim.networking import NetworkDevice
    return NetworkDevice(env, "new device", 1)


def test_instruct_transmission_through_non_existing_port__raise_exception(
        new_device):
    from ft4fttsim.networking import FT4FTTSimException
    from unittest.mock import sentinel
    with pytest.raises(FT4FTTSimException):
        next(new_device.instruct_transmission(
            sentinel.message, sentinel.bogus_port))
