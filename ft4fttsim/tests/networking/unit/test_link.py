# author: David Gessner <davidges@gmail.com>

import pytest
from unittest.mock import Mock
from ft4fttsim.networking import Link, Port
from ft4fttsim.exceptions import FT4FTTSimException


@pytest.fixture
def port1():
    stub_port = Mock(spec=Port)
    stub_port.is_free = True
    return stub_port


@pytest.fixture
def port2():
    stub_port = Mock(spec=Port)
    stub_port.is_free = True
    return stub_port


@pytest.mark.parametrize("Mbps,propagation_delay", [
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
def test_link_constructor_raises_exception(
        env, port1, port2, Mbps, propagation_delay):
    with pytest.raises(FT4FTTSimException):
        Link(env, port1, port2, Mbps, propagation_delay)


@pytest.mark.parametrize("Mbps,propagation_delay", [
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
        env, port1, port2, Mbps, propagation_delay):
    # Constructing the link should pass and not raise any exception or error
    Link(env, port1, port2, Mbps, propagation_delay)


@pytest.mark.parametrize(
    "Mbps,num_bytes,expected_transmission_time",
    [(1, 1526, 12208), (10, 1526, 1220.8), (100, 1526, 122.08),
     (1000, 1526, 12.208), (100, 0, 0)]
)
def test_link__transmission_time_us(
        env, port1, port2, Mbps, num_bytes, expected_transmission_time):
    link = Link(env, port1, port2, Mbps, 0)
    assert link.transmission_time_us(num_bytes) == expected_transmission_time


def test_sublink_have_correct_ports(env, port1, port2):
    link = Link(env, port1, port2, 100, 0)
    assert (
        link.sublink[0].transmitter_port == link.sublink[1].receiver_port
        and
        link.sublink[1].transmitter_port == link.sublink[0].receiver_port)
