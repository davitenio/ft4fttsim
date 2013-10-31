# author: David Gessner <davidges@gmail.com>

import simpy
from ft4fttsim.ethernet import Ethernet
from ft4fttsim.exceptions import FT4FTTSimException
from ft4fttsim.simlogging import log
import collections


class Link:
    """
    Class whose instances model links used in an Ethernet network.

    A Link object models a physical link between at most 2 network devices
    (objects of class NetworkDevice). A Link object has a certain transmission
    speed (expressed in megabits per second) and propagation delay (expressed
    in microseconds). Links are directional, i.e., they have a single start
    point and a single end point, and messages that are being modeled as being
    transmitted can only be transmitted from the start point to the end point,
    but not in the opposite direction. At any one time at most one message can
    be transmitted through a link. If the transmission of additional messages
    is ordered through the link, then they will be queued.

    """
    def __init__(self, env, megabits_per_second, propagation_delay_us):
        """
        Create a new instance of class Link.

        Arguments:
            megabits_per_second: Speed of the link in megabits per second.
            propagation_delay_us: Propagation delay of the link in
                microseconds.

        Raises:
            FT4FTTSimException: error if the arguments have invalid values,
                e.g., a negative value for the propagation delay.

        """
        if megabits_per_second <= 0:
            raise FT4FTTSimException("Mbps must be a positive number.")
        if propagation_delay_us < 0:
            raise FT4FTTSimException("Propagation delay cannot be negative.")
        self.env = env
        self.resource = simpy.Resource(self.env, capacity=1)
        self._start_point = None
        self._end_point = None
        self.megabits_per_second = megabits_per_second
        self.propagation_delay_us = propagation_delay_us

    @property
    def start_point(self):
        return self._start_point

    @start_point.setter
    def start_point(self, device):
        """
        Set the start point of the link.

        Arguments:
            device: The NetworkDevice instance to be set as the start point for
                the link, i.e., the transmitter for this link.

        """
        if self._start_point != None:
            raise FT4FTTSimException("Link already has a start point.")
        self._start_point = device

    @property
    def end_point(self):
        return self._end_point

    @end_point.setter
    def end_point(self, device):
        """
        Set the end point of the link.

        Arguments:
            device: The NetworkDevice instance to be set as the end point for
                the link, i.e., the receiver for this link.

        """
        if self._end_point != None:
            raise FT4FTTSimException("Link already has an end point.")
        self._end_point = device

    def __str__(self):
        return "{}->{}".format(self._start_point, self._end_point)


class NetworkDevice:

    def __init__(self, env, name):
        self.env = env
        # list of outlinks to which the network device is connected
        self.outlinks = []
        # list of inlinks to which the network device is connected
        self.inlinks = []
        self.receive_buffer = simpy.Store(self.env)
        self.name = name

    def connect_outlink(self, link):
        link.start_point = self
        self.outlinks.append(link)

    def connect_inlink(self, link):
        link.end_point = self
        self.inlinks.append(link)

    def connect_outlink_list(self, link_list):
        for link in link_list:
            self.connect_outlink(link)

    def connect_inlink_list(self, link_list):
        for link in link_list:
            self.connect_inlink(link)

    def instruct_transmission(self, message, outlink):
        log.debug("{} instructing transmission of {} on {}".format(self,
            message, outlink))
        if outlink not in self.outlinks:
            raise FT4FTTSimException("{} is not an outlink of {}".format(
                outlink, self))
        transmission = message.transmit(outlink)
        self.env.process(transmission)

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name


class MessageRecordingDevice(NetworkDevice):
    """
    Class whose instances model a passive receiver.

    Instances of this class cannot transmit messages. All they do is wait for
    the reception of a message on any one of their inlinks and record the
    received message in an internal buffer together with a timestamp of the
    reception time.

    The main purpose of instances of this class is to make testing easier.

    """

    def __init__(self, env, name):
        NetworkDevice.__init__(self, env, name)
        self.proc = env.process(self.run())
        self.reception_records = {}

    def connect_outlink(self, link):
        raise NotImplementedError()

    def connect_outlink_list(self, link):
        raise NotImplementedError()

    def instruct_transmission(self, message, outlink):
        raise NotImplementedError()

    def run(self):
        while True:
            log.debug("{} sleeping until next reception".format(self))
            # sleep until a message is in the receive buffer
            msg = yield self.receive_buffer.get()
            received_messages = [msg]
            log.debug("{} received {}".format(self,
                received_messages))
            timestamp = self.env.now
            self.reception_records[timestamp] = received_messages
            log.debug("{} recorded {}".format(self, self.reception_records))

    @property
    def recorded_messages(self):
        messages = []
        for time in sorted(self.reception_records):
            messages.extend(self.reception_records[time])
        return messages

    @property
    def recorded_timestamps(self):
        return list(self.reception_records.keys())


class MessagePlaybackDevice(NetworkDevice):
    """
    Instances of this class model devices that transmit prespecified messages.

    Instances of this class cannot receive messages. What they do is accept a
    series of transmission commands and then execute them. Each transmission
    command specifies what message to transmit at what time and through which
    outlink.

    The main purpose of instances of this class is to make testing easier.

    """

    def __init__(self, env, name):
        NetworkDevice.__init__(self, env, name)
        self.proc = env.process(self.run())
        self.transmission_commands = {}

    def load_transmission_commands(self, transmission_commands):
        """
        Load the transmission commands to execute once the run method is
        activated by simpy.

        Arguments:
            transmission_commands: The transmission commands to execute once
                the run method is activated by the simulator. This argument
                should be a dictionary whose keys are instants of time when
                message transmissions should be instructed. Each of the values
                of the dictionary should be another dictionary whose keys are
                the outlinks on which transmissions should be ordered and
                whose values are lists of messages to be transmitted through
                the corresponding outlink. Example:

                {
                    0.0:  {outlink1: [message1, message2]},
                    12.0: {outlink1: [message3]},
                    13.5: {outlink3: [message4, message5, message6]}
                }

        """
        self.transmission_commands = transmission_commands
        log.debug("{} loaded transmissions: {}".format(self,
            self.transmission_commands))

    def connect_inlink(self, link):
        raise NotImplementedError()

    def connect_inlink_list(self, link):
        raise NotImplementedError()

    def run(self):
        for time in sorted(self.transmission_commands):
            delay_before_next_tx_order = time - self.env.now
            log.debug("{} sleeping until next transmission".format(self))
            # sleep until next transmission time
            yield self.env.timeout(delay_before_next_tx_order)
            for outlink, messages_to_tx in \
                    self.transmission_commands[time].items():
                for message in messages_to_tx:
                    self.instruct_transmission(message, outlink)


class Switch(NetworkDevice):
    """
    Class whose instances model Ethernet switches.

    """

    def __init__(self, env, name):
        NetworkDevice.__init__(self, env, name)
        self.proc = env.process(self.run())

    def forward_messages(self, message_list):
        """
        Forward each message in 'message_list' to the appropriate outlink.

        Note that forwarding a message from an inlink to an outlink is
        implemented as creating a new message instance based on the message
        in the inlink, and transmitting the new message instance on the
        outlink.
        """

        def find_outlinks(destination):
            """
            Return a list of the outlinks that have as their endpoint
            'destination'.

            Arguments:
                destination: an instance of class NetworkDevice or an iterable
                of NetworkDevice instances.

            Returns:
                A list of the outlinks that have as their end point one of the
                devices in 'destination'.

            """
            destination_outlinks = []
            if isinstance(destination, collections.Iterable):
                # the destination is multicast
                for outlink in self.outlinks:
                    if outlink.end_point in destination:
                        destination_outlinks.append(outlink)
            else:
                # the destination is unicast
                for outlink in self.outlinks:
                    if outlink.end_point == destination:
                        destination_outlinks.append(outlink)
            return destination_outlinks

        for message in message_list:
            destinations = message.destination
            destination_outlinks = find_outlinks(destinations)
            for link in destination_outlinks:
                new_message = Message.from_message(message)
                self.instruct_transmission(new_message, link)

    def run(self):
        while True:
            # sleep until a message is in the receive buffer
            msg = yield self.receive_buffer.get()
            received_messages = [msg]
            self.forward_messages(received_messages)


class Message:
    """
    Class for messages that model Ethernet frames.

    """
    # next available ID for message objects
    next_ID = 0

    def __init__(self, env, source, destination, size_bytes, message_type):
        """
        Create an instance of Message.

        Arguments:
            source: usually an instance of NetworkDevice. It models the
                MAC source address field of an Ethernet frame.
            destination: usually an instance of NetworkDevice or a list of
                instances of NetworkDevice. It models the MAC destination
                address field of an Ethernet frame. If it is iterable, then it
                models a multicast address, otherwise it models a unicast
                address.
            size_bytes: indicates the size in bytes of the Ethernet frame
                modeled by the Message instance created. The size does not
                include the Ethernet preamble, the start of frame delimiter, or
                an IEEE 802.1Q tag.
            message_type: models the Ethertype field.

        """
        if not (Ethernet.MIN_FRAME_SIZE_BYTES <= size_bytes <=
                Ethernet.MAX_FRAME_SIZE_BYTES):
            raise FT4FTTSimException(
                "Message size must be between {} and {}, but is {}".format(
                Ethernet.MIN_FRAME_SIZE_BYTES, Ethernet.MAX_FRAME_SIZE_BYTES,
                size_bytes))
        self.env = env
        self.ID = Message.next_ID
        Message.next_ID += 1
        # source of the message. Models the source MAC address.
        self.source = source
        # destination of the message. It models the destination MAC address. It
        # is a list to allow multicast addressing.
        self.destination = destination
        self.size_bytes = size_bytes
        self.message_type = message_type
        self.name = "({:03d}, {}, {}, {:d}, {})".format(self.ID,
            self.source, self.destination, self.size_bytes,
            self.message_type)
        log.debug("{} created".format(self))

    @classmethod
    def from_message(cls, template_message):
        """
        Creates a new message instance using template_message as a template.

        """
        new_equivalent_message = cls(
            template_message.env,
            template_message.source,
            template_message.destination,
            template_message.size_bytes,
            template_message.message_type)
        return new_equivalent_message

    def transmit(self, link):
        """
        Transmit the message instance on the Link link.
        """
        log.debug("{} queued for transmission".format(self))
        with link.resource.request() as transmission_request:
            # request access to, and possibly queue for, the link
            yield transmission_request
            log.debug("{} transmission started".format(self))
            BITS_PER_BYTE = 8
            # time in microseconds to load the message into the link (this does
            # not include the propagation time)
            transmission_time_us = ((Ethernet.PREAMBLE_SIZE_BYTES +
                Ethernet.SFD_SIZE_BYTES + self.size_bytes) * BITS_PER_BYTE /
                float(link.megabits_per_second))
            link.message = self
            # wait for the transmission + propagation time to elapse
            yield self.env.timeout(transmission_time_us +
                link.propagation_delay_us)
            # transmission finished, notify the link's end point, but do not
            # release the link yet
            log.debug("{} transmission finished".format(self))
            link.end_point.receive_buffer.put(self)
            # wait for the duration of the ethernet interframe gap to elapse
            IFG_duration_us = (Ethernet.IFG_SIZE_BYTES * BITS_PER_BYTE /
                float(link.megabits_per_second))
            yield self.env.timeout(IFG_duration_us)
            log.debug("{} inter frame gap finished".format(self))

    def is_equivalent(self, message):
        """
        Returns true if self and message are identical except for the message
        ID.
        """
        return (self.source == message.source and
            self.destination == message.destination and
            self.size_bytes == message.size_bytes and
            self.message_type == message.message_type)

    def is_trigger_message(self):
        return self.message_type == "TM"

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name
