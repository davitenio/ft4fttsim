# author: David Gessner <davidges@gmail.com>

from collections import namedtuple

from ft4fttsim.simlogging import log
from ft4fttsim.networking import NetworkDevice, Port, Link, Message
from ft4fttsim.exceptions import FT4FTTSimException
import ft4fttsim.ethernet as ethernet


class MessageType(object):
    """
    Class used as an enumeration type for different types of FTT messages.

    The attributes of this class are intended to be used as the message_type
    attribute of ft4fttsim.networking.Message instances.

    Example:

    >>> import simpy
    >>> env = simpy.Environment()
    >>> d1 = NetworkDevice(env, "some device", 1)
    >>> d2 = NetworkDevice(env, "another device", 1)
    >>> msg = Message(env, d1, d2, 1234, MessageType.UPDATE_REQUEST)
    >>> msg.message_type
    'Update Req.'
    >>> msg.message_type == MessageType.UPDATE_REQUEST
    True

    """
    TRIGGER_MESSAGE = "TM"
    UPDATE_REQUEST = "Update Req."


SyncStreamConfig = namedtuple(
    'SyncStreamConfig',
    # The SyncStreamConfig parameters are expressed as integer multiples of the
    # Elementary Cycle duration.
    'transmission_time_ecs, deadline_ecs, period_ecs, offset_ecs'
)


class Master(NetworkDevice):
    """
    Class for FTT masters.

    """

    def __init__(
            self, env, name, num_ports, slaves, ec_duration_us,
            num_tms_per_ec=1, sync_requirements=None):
        """
        Constructor for FTT masters.

        Arguments:
            env: A simpy.Environment instance.
            name: A string used to identify the new Master instance.
            num_ports: The number of ports that the new Master instance should
                have.
            slaves: Slaves for which the master is responsible.
            ec_duration_us: Duration of the elementary cycles in
                microseconds.
            num_tms_per_ec: Number of trigger messages to transmit per
                elementary cycle.
            sync_requirements: A dictionary whose keys identify synchronous
                stream configurations (i.e., instances of SyncStreamConfig) and
                whose values are synchronous streams.

        """
        assert isinstance(num_tms_per_ec, int)
        NetworkDevice.__init__(self, env, name, num_ports)
        self.proc = env.process(self.run())
        self.slaves = slaves
        self.ec_duration_us = ec_duration_us
        self.num_tms_per_ec = num_tms_per_ec
        if sync_requirements is None:
            self.sync_requirements = {}
        else:
            self.sync_requirements = sync_requirements
        # This counter is incremented after each successive elementary cycle
        self.ec_count = 0
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
            stream_id, new_sync_stream_config = message.data
            self.sync_requirements[stream_id] = new_sync_stream_config

    def process_received_messages(self, messages):
        for msg in messages:
            if msg.message_type == MessageType.UPDATE_REQUEST:
                self.process_update_request_message(msg)

    def broadcast_trigger_message(self):
        """
        Broadcast the trigger message on all ports.

        """
        log.debug("{} broadcasting trigger message".format(self))
        for port in self.ports:
            # TODO: calculate a schedule to be transmitted in the trigger
            # message.
            trigger_message = Message(self.env, self, self.slaves,
                                      ethernet.MAX_FRAME_SIZE_BYTES,
                                      MessageType.TRIGGER_MESSAGE)
            log.debug(
                "{} instruct transmission of trigger message".format(self))
            self.env.process(
                self.instruct_transmission(trigger_message, port))

    def run(self):
        while True:
            self.ec_count += 1
            log.debug("{} starting EC ".format(self, self.ec_count))
            time_last_ec_start = self.env.now
            for _ in range(self.num_tms_per_ec):
                self.broadcast_trigger_message()
            # wait for the next elementary cycle to start
            while True:
                time_since_ec_start = self.env.now - time_last_ec_start
                delay_before_next_tx_order = float(self.ec_duration_us -
                                                   time_since_ec_start)
                if delay_before_next_tx_order > 0:
                    yield self.env.timeout(delay_before_next_tx_order)
                else:
                    break


class FT4FTTSwitch(NetworkDevice):

    def __init__(self, env, name, num_ports, master):
        """
        Arguments:
            env: A simpy.Environment instance.
            name: A string used to identify the new switch instance.
            num_ports: The number of ports that the new switch instance should
                have.
            master: An FTT master (i.e., instance of Master) to be embedded
                within the FT4FTTSwitch instance.

        """
        if len(master.ports) != 1:
            raise FT4FTTSimException(
                "An embedded master must have exactly one port")
        NetworkDevice.__init__(self, env, name, num_ports)
        # Port leading to the embedded master.
        self.internal_port = Port(env, name + "-internalport")
        # All ports of the switch.
        self.ports.append(self.internal_port)
        # Ports leading to devices other than the embedded master.
        self.external_ports = self.ports[:-1]
        Link(env, self.internal_port, master.ports[0], float("inf"), 0)
        self.master = master
        env.process(self.listen_for_messages(self.process_received_messages))

    def flood_message(self, message):
        """
        Instruct the transmission of message on all external ports.

        """
        for port in self.external_ports:
            self.env.process(
                self.instruct_transmission(message, port))

    def process_received_messages(self, messages):
        for msg in messages:
            if msg.destination == self.master:
                self.env.process(
                    self.instruct_transmission(msg, self.internal_port))
            elif msg.message_type == MessageType.TRIGGER_MESSAGE:
                self.flood_message(msg)


# TODO: update this class.  It is currently obsolete.
class Slave(NetworkDevice):
    """
    Class for FTT slaves.

    """

    # TODO: implement
    pass
