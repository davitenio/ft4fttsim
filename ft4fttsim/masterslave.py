# author: David Gessner <davidges@gmail.com>

from networking import NetworkDevice, Message
from ethernet import Ethernet
from SimPy.Simulation import passivate, now, activate, hold


class Master(NetworkDevice):
    """
    Class for FTT masters.
    """

    def __init__(self,
            name,
            # slaves for which the master is responsible
            slaves,
            elementary_cycle_length,
            # number of trigger messages to transmit per elementary cycle
            num_TMs_per_EC=1):
        assert isinstance(num_TMs_per_EC, int)
        NetworkDevice.__init__(self, name)
        self.slaves = slaves
        self.EC_length = elementary_cycle_length
        self.num_TMs_per_EC = num_TMs_per_EC
        # This counter is incremented after each successive elementary cycle
        self.EC_count = 0

    def broadcast_trigger_message(self):
        for outlink in self.get_outlinks():
            trigger_message = Message(self, self.slaves,
                Ethernet.MAX_FRAME_LENGTH, "TM")
            self.instruct_transmission(trigger_message, outlink)

    def run(self):
        while True:
            self.EC_count += 1
            time_last_EC_start = now()
            for message_count in range(self.num_TMs_per_EC):
                self.broadcast_trigger_message()
            # wait for the next elementary cycle to start
            while True:
                time_since_EC_start = now() - time_last_EC_start
                delay_before_next_tx_order = float(self.EC_length -
                    time_since_EC_start)
                if delay_before_next_tx_order > 0:
                    yield hold, self, delay_before_next_tx_order
                else:
                    break


class Slave(NetworkDevice):
    """
    Class for FTT slaves.
    """

    def transmit_synchronous_messages(self,
            # number of messages to transmit
            number,
            # links on which to transmit each of the messages
            links):
        assert isinstance(number, int)
        for message_count in range(number):
            # TODO: decide who each message should be transmitted to. For now
            # we simply send it to ourselves.
            new_message = Message(self, [self],
                Ethernet.MAX_FRAME_LENGTH, "sync")
            # order the transmission of the message on the specified links
            for outlink in links:
                self.instruct_transmission(new_message, outlink)

    def run(self):
        while True:
            # sleep until a message is received
            yield passivate, self
            received_messages = self.read_inlinks()
            has_received_trigger_message = False
            for message in received_messages:
                if message.is_trigger_message():
                    has_received_trigger_message = True
            if has_received_trigger_message:
                # transmit on all outlinks
                self.transmit_synchronous_messages(2, self.get_outlinks())
                # wait before we order the next transmission
                delay_before_next_tx_order = 0.0
                yield hold, self, delay_before_next_tx_order
