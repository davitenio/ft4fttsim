# author: David Gessner <davidges@gmail.com>

import unittest
from mock import sentinel, Mock
from ft4fttsim.networking import *
from ft4fttsim.exceptions import FT4FTTSimException
import pytest


class TestSwitch(unittest.TestCase):

    def setUp(self):
        self.env = simpy.Environment()
        self.switch = Switch(self.env, "switch under test")

    def test_forward_messages__no_outlinks__no_instruct_transmission(self):
        """
        If the switch does not have any outlinks, then the function
        instruct_transmission should not be called.
        """
        self.switch.instruct_transmission = Mock()
        message_list = [Message(self.env, sentinel.source,
            sentinel.destinations, Ethernet.MAX_FRAME_SIZE_BYTES,
            sentinel.message_type) for i in range(10)]
        self.switch.forward_messages(message_list)
        self.assertFalse(self.switch.instruct_transmission.called)


if __name__ == '__main__':
    unittest.main()
