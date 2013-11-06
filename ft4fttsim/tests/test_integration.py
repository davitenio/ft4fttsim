# author: David Gessner <davidges@gmail.com>

import unittest
import pytest
from mock import sentinel, Mock
from ft4fttsim.ethernet import Ethernet
from ft4fttsim.networking import *


@pytest.fixture
def device(env):
    return NetworkDevice(env, "test device")


@pytest.fixture
def link(env):
    return Link(env, 10, 0)


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


class TestNetworkDeviceIntegration(unittest.TestCase):

    def setUp(self):
        self.env = simpy.Environment()
        self.device = NetworkDevice(self.env, "test device")

    def test_read_inlinks__put_message_on_1_inlink__returns_message(self):
        link = Link(self.env, 10, 0)
        self.device.connect_inlink(link)
        test_message = Message(self.env, sentinel.dummy_source, [self.device],
            Ethernet.MAX_FRAME_SIZE_BYTES, "test message")
        link.message = test_message
        received_messages = yield self.device.receive_buffer.get()
        assert received_messages == [test_message]

    def test_read_inlinks__1_empty_inlink__returns_empty_list(self):
        inlink = Link(self.env, 10, 0)
        self.device.connect_inlink(inlink)
        received_messages = yield self.device.receive_buffer.get()
        assert received_messages == []


class TestNetworkDeviceWith2Inlinks(unittest.TestCase):

    def setUp(self):
        """
        Set up the following configuration:

                      +--------+
         inlink1 ---> |        |
                      | device |
         inlink2 ---> |        |
                      +--------+
        """
        self.env = simpy.Environment()
        self.device = NetworkDevice(self.env, "test device")
        self.inlink1 = Link(self.env, 10, 0)
        self.inlink2 = Link(self.env, 10, 0)
        self.device.connect_inlink(self.inlink1)
        self.device.connect_inlink(self.inlink2)

    def test_read_inlinks__2_empty_inlinks__returns_empty_list(self):
        received_messages = yield self.device.receive_buffer.get()
        assert received_messages == []

    def test_read_inlinks__put_message_on_2_inlinks__returns_messages(self):
        test_message = Message(self.env, sentinel.dummy_source, [self.device],
            Ethernet.MAX_FRAME_SIZE_BYTES, "test message")
        self.inlink1.message = test_message
        self.inlink2.message = test_message
        received_messages = yield self.device.receive_buffer.get()
        assert received_messages == [test_message, test_message]

    def test_read_inlinks__put_diff_msg_on_2_inlinks__returns_messages(self):
        test_message1 = Message(self.env, sentinel.dummy_source, [self.device],
            Ethernet.MAX_FRAME_SIZE_BYTES, "test message1")
        test_message2 = Message(self.env, sentinel.dummy_source, [self.device],
            Ethernet.MAX_FRAME_SIZE_BYTES, "test message2")
        self.inlink1.message = test_message1
        self.inlink2.message = test_message2
        received_messages = yield self.device.receive_buffer.get()
        assert received_messages == [test_message1, test_message2]
