# author: David Gessner <davidges@gmail.com>

import pytest
from unittest.mock import sentinel, Mock
from ft4fttsim.networking import *
from ft4fttsim.tests.fixturehelper import make_link
from ft4fttsim.tests.fixturehelper import LINK_CONFIGS


@pytest.fixture(params=LINK_CONFIGS)
def link(env, request):
    config = request.param
    new_link = make_link(config, env)
    return new_link


@pytest.fixture
def device(env):
    return NetworkDevice(env, "test device")


@pytest.fixture(params=list(range(3)) + [20])
def multiple_links(env, request):
    num_links = request.param
    return [Link(env, 10, 0) for i in range(num_links)]


def test_connect_1_outlink__link_has_correct_receiver_port(device, link):
    device.connect_outlink(link)
    assert device.output_ports == [link.transmitter_port]


def test_connect_outlinks(device, multiple_links):
    for link in multiple_links:
        device.connect_outlink(link)
    assert device.output_ports == [L.transmitter_port for L in multiple_links]


def test_connect_outlink_list(device, multiple_links):
    device.connect_outlink_list(multiple_links)
    assert device.output_ports == [L.transmitter_port for L in multiple_links]


def test_get_inlinks__connect_1_inlink__returns_new_inlink(device, link):
    device.connect_inlink(link)
    assert device.input_port == link.receiver_port


def test_connect_inlinks(device, multiple_links):
    for link in multiple_links:
        device.connect_inlink(link)
    assert all(
        [L.receiver_port == device.input_port for L in multiple_links])


def test_connect_inlink_list(device, multiple_links):
    device.connect_inlink_list(multiple_links)
    assert all(
        [L.receiver_port == device.input_port for L in multiple_links])
