# author: David Gessner <davidges@gmail.com>

from SimPy.Simulation import *
from ethernet import Ethernet
from exceptions import FT4FTTSimException
from simlogging import log
import collections


class Link(Resource):
    """
    Class for links used in the FT4FTT network. Objects of this class may
    interconnect arbitrary NetworkDevices.
    """
    def __init__(self,
            # speed of the link in megabits per second
            megabits_per_second,
            # propagation delay of the link in microseconds
            propagation_delay_us):
        """
        Creates a link whose propagation time is propagation_delay_us and
        that operates at a speed of megabits_per_second Mbps.
        """
        if megabits_per_second <= 0:
            raise FT4FTTSimException("Mbps must be a positive number.")
        if propagation_delay_us < 0:
            raise FT4FTTSimException("Propagation delay cannot be negative.")
        Resource.__init__(self, 1)
        self.start_point = None
        self.end_point = None
        self.megabits_per_second = megabits_per_second
        self.propagation_delay_us = propagation_delay_us
        self.message_is_transmitted = SimEvent()
        # message that is being transmitted in the link
        self.message = None

    def set_start_point(self, device):
        if self.start_point != None:
            raise FT4FTTSimException("Link already has a start point.")
        self.start_point = device

    def set_end_point(self, device):
        if self.end_point != None:
            raise FT4FTTSimException("Link already has an end point.")
        self.end_point = device

    def get_end_point(self):
        return self.end_point

    def has_message(self):
        return self.message != None

    def put_message(self, message):
        assert self.message == None
        self.message = message

    def get_message(self):
        tmp = self.message
        self.message = None
        return tmp

    def __str__(self):
        return "{:s}->{:s}".format(self.start_point, self.end_point)


class NetworkDevice(Process):

    def __init__(self, name):
        Process.__init__(self)
        # list of outlinks to which the network device is connected
        self.outlinks = []
        # list of inlinks to which the network device is connected
        self.inlinks = []
        self.name = name

    def connect_outlink(self, link):
        link.set_start_point(self)
        self.outlinks.append(link)

    def connect_inlink(self, link):
        link.set_end_point(self)
        self.inlinks.append(link)

    def connect_outlink_list(self, link_list):
        for link in link_list:
            self.connect_outlink(link)

    def connect_inlink_list(self, link_list):
        for link in link_list:
            self.connect_inlink(link)

    def get_outlinks(self):
        return self.outlinks

    def get_inlinks(self):
        return self.inlinks

    def read_inlinks(self):
        received_messages = []
        for inlink in self.get_inlinks():
            if inlink.has_message():
                message = inlink.get_message()
                received_messages.append(message)
        return received_messages

    def instruct_transmission(self, message, outlink):
        log.debug("{:s} instructing transmission of {} on {}".format(self,
            message, outlink))
        if outlink not in self.get_outlinks():
            raise FT4FTTSimException("{} is not an outlink of {}".format(
                outlink, self))
        activate(message, message.transmit(outlink))

    def __str__(self):
        return self.name


class MessageRecordingDevice(NetworkDevice):
    def __init__(self, name):
        NetworkDevice.__init__(self, name)
        self.reception_records = {}

    def connect_outlink(self, link):
        raise NotImplementedError()

    def connect_outlink_list(self, link):
        raise NotImplementedError()

    def instruct_transmission(self, message, outlink):
        raise NotImplementedError()

    def run(self):
        while True:
            log.debug("{:s} sleeping until next reception".format(self))
            # sleep until a message notifies that it has finished transmission
            yield waitevent, self, [link.message_is_transmitted for link in
                self.get_inlinks()]
            received_messages = self.read_inlinks()
            log.debug("{:s} received {}".format(self,
                received_messages))
            timestamp = now()
            self.reception_records[timestamp] = received_messages
            log.debug("{:s} recorded {}".format(self, self.reception_records))

    def get_recorded_messages(self):
        """
        Return a list of all recorded messages sorted by timestamp.
        """
        messages = []
        for time in sorted(self.reception_records):
            messages.extend(self.reception_records[time])
        return messages

    def get_recorded_timestamps(self):
        return self.reception_records.keys()


class MessagePlaybackDevice(NetworkDevice):
    def __init__(self, name):
        """
        """
        NetworkDevice.__init__(self, name)
        self.transmission_commands = {}

    def load_transmission_commands(self, transmission_commands):
        self.transmission_commands = transmission_commands
        log.debug("{:s} loaded transmissions: {}".format(self,
            self.transmission_commands))

    def connect_inlink(self, link):
        raise NotImplementedError()

    def connect_inlink_list(self, link):
        raise NotImplementedError()

    def read_inlinks(self):
        raise NotImplementedError()

    def run(self):
        for time in sorted(self.transmission_commands):
            delay_before_next_tx_order = time - now()
            log.debug("{:s} sleeping until next transmission".format(self))
            # sleep until next transmission time
            yield hold, self, delay_before_next_tx_order
            for outlink, messages_to_tx in \
                    self.transmission_commands[time].items():
                for message in messages_to_tx:
                    self.instruct_transmission(message, outlink)


class Switch(NetworkDevice):
    """
    Class for ethernet switches.
    """

    def forward_messages(self, message_list):
        """
        Forward each message in message_list to the appropriate outlink.
        Note that forwarding a message from an inlink to an outlink is
        implemented as creating a new message instance based on the message
        in the inlink, and transmitting the new message instance on the
        outlink.
        """

        def find_outlinks(destination):
            """
            Return a list of the outlinks that have as their endpoint one of
            the network devices in the list destination_list.
            """
            destination_outlinks = []
            if isinstance(destination, collections.Iterable):
                # the destination is multicast
                for outlink in self.get_outlinks():
                    if outlink.get_end_point() in destination:
                        destination_outlinks.append(outlink)
            else:
                # the destination is unicast
                for outlink in self.get_outlinks():
                    if outlink.get_end_point() == destination:
                        destination_outlinks.append(outlink)
            return destination_outlinks

        for message in message_list:
            destinations = message.get_destination_list()
            destination_outlinks = find_outlinks(destinations)
            for link in destination_outlinks:
                new_message = Message.from_message(message)
                self.instruct_transmission(new_message, link)

    def run(self):
        while True:
            # sleep until a message notifies that it has finished transmission
            yield waitevent, self, [link.message_is_transmitted for link in
                self.get_inlinks()]
            received_messages = self.read_inlinks()
            self.forward_messages(received_messages)


class Message(Process):
    """
    Class for messages sent by a NetworkDevice.
    """
    # next available ID for message objects
    next_ID = 0

    def __init__(self,
            # models the MAC source address
            source,
            # list of intended receivers of the message instance. It models
            # the MAC destination address. It is a list to support
            # multicast addressing.
            destination_list,
            # size of the message instance in bytes
            size_bytes,
            # models the ethertype field
            msg_type):
        Process.__init__(self)
        self.ID = Message.next_ID
        Message.next_ID += 1
        # source of the message. Models the source MAC address.
        self.source = source
        # destination of the message. It models the destination MAC address. It
        # is a list to allow multicast addressing.
        self.destination_list = destination_list
        assert (Ethernet.MIN_FRAME_SIZE_BYTES <= size_bytes
            <= Ethernet.MAX_FRAME_SIZE_BYTES)
        self.size_bytes = size_bytes
        self.message_type = msg_type
        self.name = "({:03d}, {:s}, {:s}, {:d}, {:s})".format(self.ID,
            self.source, self.destination_list, self.size_bytes,
            self.message_type)
        log.debug("{:s} created".format(self))

    @classmethod
    def from_message(cls, template_message):
        """
        Creates a new message instance using template_message as a template.
        """
        new_equivalent_message = cls(template_message.get_source(),
            template_message.get_destination_list(),
            template_message.size_bytes,
            template_message.message_type)
        return new_equivalent_message

    def get_source(self):
        """
        Return the source NetworkDevice for the message, which models the
        source MAC address.
        """
        return self.source

    def get_destination_list(self):
        """
        Return the destination NetworkDevice for the message, which models
        the destination MAC address.
        """
        return self.destination_list

    def get_size_in_bytes(self):
        return self.size_bytes

    def get_message_type(self):
        return self.message_type

    def transmit(self, link):
        """
        Transmit the message instance on the Link link.
        """
        log.debug("{:s} queued for transmission".format(self))
        # request access to, and possibly queue for, the link
        yield request, self, link
        log.debug("{:s} transmission started".format(self))
        BITS_PER_BYTE = 8
        # time in microseconds to load the message into the link (this does
        # not include the propagation time)
        transmission_time_us = (self.size_bytes * BITS_PER_BYTE /
            float(link.megabits_per_second))
        link.put_message(self)
        # wait for the transmission + propagation time to elapse
        yield hold, self, transmission_time_us + link.propagation_delay_us
        # transmission finished, notify the link's end point, but do not
        # release the link yet
        log.debug("{:s} transmission finished".format(self))
        link.message_is_transmitted.signal()
        # wait for the duration of the ethernet interframe gap to elapse
        IFG_duration_us = (Ethernet.IFG_SIZE_BYTES * BITS_PER_BYTE /
            float(link.megabits_per_second))
        yield hold, self, IFG_duration_us
        log.debug("{:s} inter frame gap finished".format(self))
        # release the link, allowing another message to gain access to it
        yield release, self, link

    def is_equivalent(self, message):
        """
        Returns true if self and message are identical except for the message
        ID.
        """
        return (self.get_source() == message.get_source() and
            self.get_destination_list() == message.get_destination_list() and
            self.get_size_in_bytes() == message.get_size_in_bytes() and
            self.get_message_type() == message.get_message_type())

    def is_trigger_message(self):
        return self.message_type == "TM"

    def __str__(self):
        return self.name
