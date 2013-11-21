# author: David Gessner <davidges@gmail.com>

import pytest


@pytest.fixture
def master(env):
    from ft4fttsim.master import Master
    new_master = Master(env, "embedded master", 1, [], 10 ** 9, 1)
    return new_master


def test_FT4FTT_switch_constructor_does_not_raise_exception(env, master):
    from ft4fttsim.ft4fttswitch import FT4FTTSwitch
    # Invoking the FT4FTTSwitch constructor should not raise exception or cause
    # any error.
    FT4FTTSwitch(env, "FT4FTT switch", 3, master)
