# author: David Gessner <davidges@gmail.com>

import pytest
from mock import sentinel, Mock
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


def test_get_outlinks__connect_1_outlink__returns_new_outlink(device, link):
    device.connect_outlink(link)
    assert device.outlinks == [link]


def test_connect_outlinks__returns_outlinks(device, multiple_links):
    for link in multiple_links:
        device.connect_outlink(link)
    assert device.outlinks == multiple_links


def test_connect_outlink_list__returns_outlinks(device, multiple_links):
    device.connect_outlink_list(multiple_links)
    assert device.outlinks == multiple_links


def test_get_inlinks__connect_1_inlink__returns_new_inlink(device, link):
    device.connect_inlink(link)
    assert device.inlinks == [link]


def test_connect_inlinks__returns_inlinks(device, multiple_links):
    for link in multiple_links:
        device.connect_inlink(link)
    assert device.inlinks == multiple_links


def test_connect_inlink_list__returns_inlinks(device, multiple_links):
    device.connect_inlink_list(multiple_links)
    assert device.inlinks == multiple_links
