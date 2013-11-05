# author: David Gessner <davidges@gmail.com>

import pytest
from ft4fttsim.networking import Link
from ft4fttsim.exceptions import FT4FTTSimException


@pytest.mark.parametrize("megabits,propagation_delay", [
    # negative propagation delay raises exception
    (10, -1),
    # zero megabits per second raises exception
    (0, 1),
    # negative megabits per second raises exception
    (-1, 1),
    # negative megabits per second and negative propagation delay raises
    # exception
    (-5, -5),
])
def test_link_constructor_raises_exception(env, megabits, propagation_delay):
    with pytest.raises(FT4FTTSimException):
        Link(env, megabits, propagation_delay)


@pytest.mark.parametrize("megabits,propagation_delay", [
    # zero propagation delay does not raise an exception
    (10, 0),

    # example constructor parameters that should not raise an exception
    (1, 1),
    (5, 5),
    (100000, 100000),
    (0.00001, 0.00001),
    (0.00001, 100000),
    (100000, 0.00001),
])
def test_link_constructor_does_not_raise_exception(
        env, megabits, propagation_delay):
    try:
        Link(env, megabits, propagation_delay)
    except:
        assert False, "Link constructor should not raise exception."


def test_link_created__receiver_is_None(env):
    link = Link(env, 10, 0)
    assert link.receiver is None
