# author: David Gessner <davidges@gmail.com>

import pytest


@pytest.fixture
def new_device(env):
    from ft4fttsim.networking import NetworkDevice
    return NetworkDevice(env, "new device")


@pytest.fixture(params=range(5))
def links(env, request):
    from ft4fttsim.networking import Link
    from unittest.mock import Mock
    num_links = request.param
    link_list = [
        Mock(spec_set=Link, name="link " + str(i))
        for i in range(num_links)]
    return link_list


def test_new_device__has_no_outlinks(new_device):
    assert new_device.outlinks == []


def test_new_device__has_no_inlinks(new_device):
    assert new_device.inlinks == []


def test_connect_outlinks(new_device, links):
    for outlink in links:
        new_device.connect_outlink(outlink)
    assert new_device.outlinks == links


def test_connect_outlink_list(new_device, links):
    new_device.connect_outlink_list(links)
    assert new_device.outlinks == links


def test_connect_inlinks(new_device, links):
    for inlink in links:
        new_device.connect_inlink(inlink)
    assert new_device.inlinks == links


def test_inlink_list(new_device, links):
    new_device.connect_inlink_list(links)
    assert new_device.inlinks == links


def test_instruct_transmission__no_outlink__raise_exception(new_device):
    from ft4fttsim.networking import FT4FTTSimException
    from unittest.mock import sentinel
    not_connected_outlink = sentinel.dummy_link
    with pytest.raises(FT4FTTSimException):
        new_device.instruct_transmission(
            sentinel.message, not_connected_outlink)
