# author: David Gessner <davidges@gmail.com>

from ft4fttsim.networking import NetworkDevice, Message
from ft4fttsim.ethernet import Ethernet
from ft4fttsim.simlogging import log
import simpy


class Master(NetworkDevice):
    """
    Class for FTT masters.

    """

    def __init__(
            self, env, name, num_ports, slaves, elementary_cycle_us,
            num_TMs_per_EC=1):
        """
        Constructor for FTT masters.

        ARGUMENTS:
            slaves: slaves for which the master is responsible.
            elementary_cycle_us: duration of the elementary cycles in
                microseconds.
            num_TMs_per_EC: number of trigger messages to transmit per
                elementary cycle.

        """
        assert isinstance(num_TMs_per_EC, int)
        NetworkDevice.__init__(self, env, name, num_ports)
        self.proc = env.process(self.run())
        self.slaves = slaves
        self.EC_duration_us = elementary_cycle_us
        self.num_TMs_per_EC = num_TMs_per_EC
        # This counter is incremented after each successive elementary cycle
        self.EC_count = 0

    def broadcast_trigger_message(self):
        log.debug("{} broadcasting trigger message".format(self))
        for port in self.ports:
            trigger_message = Message(self.env, self, self.slaves,
                                      Ethernet.MAX_FRAME_SIZE_BYTES,
                                      Message.Type.TRIGGER_MESSAGE)
            log.debug(
                "{} instruct transmission of trigger message".format(self))
            self.env.process(
                self.instruct_transmission(trigger_message, port))

    def run(self):
        while True:
            self.EC_count += 1
            log.debug("{} starting EC ".format(self, self.EC_count))
            time_last_EC_start = self.env.now
            for message_count in range(self.num_TMs_per_EC):
                self.broadcast_trigger_message()
            # wait for the next elementary cycle to start
            while True:
                time_since_EC_start = self.env.now - time_last_EC_start
                delay_before_next_tx_order = float(self.EC_duration_us -
                                                   time_since_EC_start)
                if delay_before_next_tx_order > 0:
                    yield self.env.timeout(delay_before_next_tx_order)
                else:
                    break
