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


def test_new_device__has_no_output_ports(new_device):
    assert new_device.output_ports == []


def test_connect_output_ports(new_device, links):
    for outlink in links:
        new_device.connect_outlink(outlink)
    assert new_device.output_ports == [L.transmitter_port for L in links]


def test_connect_outlink_list(new_device, links):
    new_device.connect_outlink_list(links)
    assert new_device.output_ports == [L.transmitter_port for L in links]


def test_connect_inlinks(new_device, links):
    for inlink in links:
        new_device.connect_inlink(inlink)
    assert all([new_device.input_port == L.receiver_port for L in links])


def test_inlink_list(new_device, links):
    new_device.connect_inlink_list(links)
    assert all([new_device.input_port == L.receiver_port for L in links])


def test_instruct_transmission_through_non_existing_port__raise_exception(
        new_device):
    from ft4fttsim.networking import FT4FTTSimException
    from unittest.mock import sentinel
    with pytest.raises(FT4FTTSimException):
        next(new_device.instruct_transmission(
            sentinel.message, sentinel.bogus_port))
