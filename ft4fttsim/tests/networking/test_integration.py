# author: David Gessner <davidges@gmail.com>

from unittest.mock import sentinel, Mock

import pytest

from ft4fttsim.networking import Link, NetworkDevice, Port


@pytest.fixture
def port():
    stub_port = Mock(spec=Port)
    stub_port.is_free = True
    return stub_port


def test_link_has_correct_transmitter_port(env, port):
    device = NetworkDevice(env, "test device", 1)
    link = Link(env, device.ports[0], port, 1, 1)
    assert device.ports == [link.sublink[0].transmitter_port]


@pytest.fixture(params=list(range(3)) + [20])
def test_links_have_correct_transmitter_ports(env, port):
    num_links = request.param
    device = NetworkDevice(env, "test device", num_ports=num_links)
    multiple_links = []
    for i in range(num_links):
        multiple_links.append(
            Link(env, device.ports[i], port, 100, 0))
    assert device.ports == [L.transmitter_port for L in multiple_links]


def test_link_has_correct_receiver_port(env, port):
    device = NetworkDevice(env, "test device", 1)
    link = Link(env, port, device.ports[0], 1, 1)
    assert device.ports[0] == link.sublink[0].receiver_port


@pytest.fixture(params=list(range(3)) + [20])
def test_links_have_correct_receiver_ports(env, port):
    num_links = request.param
    device = NetworkDevice(env, "test device", 1)
    multiple_links = []
    for i in range(num_links):
        multiple_links.append(
            Link(env, port, device.ports[0], 100, 0))
    assert all(
        [L.receiver_port == device.ports[0] for L in multiple_links])
