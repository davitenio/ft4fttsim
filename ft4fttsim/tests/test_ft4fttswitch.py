# author: David Gessner <davidges@gmail.com>

import pytest
from ft4fttsim.ft4ftt import FT4FTTSwitch, Master
from ft4fttsim.exceptions import FT4FTTSimException


@pytest.fixture
def master(env):
    new_master = Master(env, "embedded master", 1, [], 10 ** 9, 1)
    return new_master


def test_FT4FTT_switch_constructor_does_not_raise_exception(env, master):
    # Invoking the FT4FTTSwitch constructor should not raise exception or cause
    # any error.
    FT4FTTSwitch(env, "FT4FTT switch", 3, master)


def test_FT4FTT_switch_constructor_raises_exception(env):
    master_2ports = Master(env, "embedded master", 2, [], 10 ** 9, 1)
    with pytest.raises(FT4FTTSimException):
        # Invoking the FT4FTTSwitch constructor with a master that has not
        # exactly one port should raise exception.
        FT4FTTSwitch(env, "FT4FTT switch", 3, master_2ports)
