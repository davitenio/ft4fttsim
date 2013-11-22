# author: David Gessner <davidges@gmail.com>

import simpy
from ft4fttsim.networking import NetworkDevice, Message
from ft4fttsim.ethernet import Ethernet
from ft4fttsim.simlogging import log
from collections import namedtuple


SyncStreamConfig = namedtuple(
    'SyncStreamConfig',
    # The SyncStreamConfig parameters are expressed as integer multiples of the
    # Elementary Cycle duration.
    'transmission_time_ECs, deadline_ECs, period_ECs, offset_ECs'
)


class Master(NetworkDevice):
    """
    Class for FTT masters.

    """

    def __init__(
            self, env, name, num_ports, slaves, elementary_cycle_us,
            num_TMs_per_EC=1, sync_requirements=None):
        """
        Constructor for FTT masters.

        Arguments:
            env: A simpy.Environment instance.
            name: A string used to identify the new Master instance.
            num_ports: The number of ports that the new Master instance should
                have.
            slaves: Slaves for which the master is responsible.
            elementary_cycle_us: Duration of the elementary cycles in
                microseconds.
            num_TMs_per_EC: Number of trigger messages to transmit per
                elementary cycle.
            sync_requirements: A dictionary whose keys identify synchronous
                stream configurations (i.e., instances of SyncStreamConfig) and
                whose values are synchronous streams.

        """
        assert isinstance(num_TMs_per_EC, int)
        NetworkDevice.__init__(self, env, name, num_ports)
        self.proc = env.process(self.run())
        self.slaves = slaves
        self.EC_duration_us = elementary_cycle_us
        self.num_TMs_per_EC = num_TMs_per_EC
        if sync_requirements is None:
            self.sync_requirements = {}
        else:
            self.sync_requirements = sync_requirements
        # This counter is incremented after each successive elementary cycle
        self.EC_count = 0
        self.env.process(
            self.listen_for_messages(self.process_received_messages))

    def passes_admission_control(self, update_request_message):
        """
        Return True if 'update_request' can be allowed to update the
        sync_requirements.

        """
        assert isinstance(update_request_message, Message)
        # TODO: implement a proper admission control check.  For now we always
        # return true.
        return True

    def process_update_request_message(self, message):
        if self.passes_admission_control(message):
            stream_ID, new_sync_stream_config = message.data
            self.sync_requirements[stream_ID] = new_sync_stream_config

    def process_received_messages(self, messages):
        for m in messages:
            if m.message_type == Message.Type.UPDATE_REQUEST:
                process_update_request_message(m)

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
