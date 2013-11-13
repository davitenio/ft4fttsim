# author: David Gessner <davidges@gmail.com>

import pytest
from unittest.mock import sentinel, Mock
from ft4fttsim.networking import *


def test_link_has_correct_transmitter_port(env):
    device = NetworkDevice(env, "test device")
    link = Link(env, device.output_ports[0], Mock(spec_set=InputPort), 1, 1)
    assert device.output_ports == [link.transmitter_port]


@pytest.fixture(params=list(range(3)) + [20])
def test_links_have_correct_transmitter_ports(env):
    num_links = request.param
    device = NetworkDevice(env, "test device", num_ports=num_links)
    multiple_links = []
    for i in range(num_links):
        multiple_links.append(
            Link(env, device.output_ports[i],
                 Mock(spec_set=InputPort), 100, 0))
    assert device.output_ports == [L.transmitter_port for L in multiple_links]


def test_link_has_correct_receiver_port(env):
    device = NetworkDevice(env, "test device")
    stub_output_port = Mock(spec=OutputPort)
    stub_output_port.is_free = True
    link = Link(env, stub_output_port, device.input_port, 1, 1)
    assert device.input_port == link.receiver_port


@pytest.fixture(params=list(range(3)) + [20])
def test_links_have_correct_receiver_ports(env):
    num_links = request.param
    device = NetworkDevice(env, "test device")
    multiple_links = []
    for i in range(num_links):
        multiple_links.append(
            Link(env, Mock(spec_set=OutputPort),
                 device.input_port, 100, 0))
    assert all(
        [L.receiver_port == device.input_port for L in multiple_links])
