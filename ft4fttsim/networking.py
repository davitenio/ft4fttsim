# author: David Gessner <davidges@gmail.com>
"""
This module provides classes to define a simulated ethernet network.

"""

import collections

import simpy

import ft4fttsim.ethernet as ethernet
from ft4fttsim.exceptions import FT4FTTSimException
from ft4fttsim.simlogging import log


class Port(object):
    """
    Models physical Ethernet ports.

    Instances of class NetworkDevice can have several such ports, and to each
    one of them an instance of Link can be attached.

    Each port has an input queue and an output queue. The input queue is where
    messages that are received through the port are queued. The output queue is
    where messages that are to be transmitted through the port are queued.

    Input queues are modeled as simpy stores with infinite capacity. The
    waiting time in an input queue is therefore always zero for any message.
    That is, a message received in an input queue does not suffer any queuing
    delay. Output queues, on the other hand, are modeled by a simpy store with
    capacity 1. This means that messages transmitted through the output queue
    may suffer a queuing delay.

    """

    def __init__(self, env, name):
        """
        Constructor for Port instances.

        Arguments:
            env: A simpy.Environment instance.
            name: A string used to identify the Port instance.

        """
        self.in_queue = simpy.Store(env)
        self.out_queue = simpy.Store(env, capacity=1)
        # indicates whether the port is already connected to a link
        self.is_free = True
        self.name = name

    def __repr__(self):
        return self.name


class Link(object):
    """
    Models links used in an Ethernet network.

    A Link object models a bidirectional physical link between exactly 2
    network device ports (objects of class Port). A Link object has a certain
    transmission speed (expressed in megabits per second) and propagation delay
    (expressed in microseconds).

    """
    def __init__(
            self, env,
            port1, port2,
            megabits_per_second, propagation_delay_us):
        """
        Create a new instance of class Link.

        Arguments:
            env: A simpy.Environment instance.
            port1: An instance of Port to which the link will be connected. It
                models the port at one extreme of the modeled link.
            port2: Another instance of Port to which the link will be
                connected. It models the port at the other extreme of the
                modeled link.
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
        if not isinstance(port1, Port):
            raise FT4FTTSimException(
                "port1 argument must be a port and not {}.".format(
                    type(port1)))
        if not isinstance(port2, Port):
            raise FT4FTTSimException(
                "port2 argument must be a port and not {}.".format(
                    type(port2)))
        assert port1.is_free
        assert port2.is_free
        self.sublink = (
            _Sublink(env, self, port1, port2),
            _Sublink(env, self, port2, port1)
        )
        port1.is_free = False
        port2.is_free = False
        self.megabits_per_second = megabits_per_second
        self.propagation_delay_us = propagation_delay_us

    def transmission_time_us(self, num_bytes):
        """
        Gives the time in microseconds to transmit num_bytes on the link.

        Arguments:
            num_bytes: The number of bytes we want to know the transmission
                time for.

        Returns:
            A floating-point number representing the number of microseconds
            that it would take a Port attached to the link to transmit
            num_bytes, counting from when the first bit until the last bit has
            left the Port.

        Example:

        Assuming a link of 100 Mbps, and 1526 bytes to transmit, results in a
        transmission time of 1526 * 8 / 10**8 = 122.08 microseconds:

        >>> env = simpy.Environment()
        >>> d = NetworkDevice(env, "some device", 1)
        >>> d2 = NetworkDevice(env, "another device", 1)
        >>> link = Link(env, d.ports[0], d2.ports[0], 100, 0)
        >>> link.transmission_time_us(1526)
        122.08

        """
        bits_to_transmit = num_bytes * 8
        transmission_time_us = (bits_to_transmit / self.megabits_per_second)
        return transmission_time_us


class _Sublink(object):
    """
    Models a directional sublink of a Link.

    Link instances are comprised of 2 _Sublinks each, one for each direction.
    This means that _Sublinks are directional, i.e., they have a single
    transmitter and a single receiver port. Messages that are being modeled as
    being transmitted can only be transmitted from the transmitter to the
    receiver port, but not in the opposite direction. At any one time at most
    one message can be transmitted through a _Sublink. If the transmission of
    additional messages is ordered through the _Sublink when it already
    contains a message, then the additional messages will be queued in the
    output queue of the transmitter port of that _Sublink.

    """
    def __init__(
            self, env, link,
            transmitter_port, receiver_port):
        """
        Create a new instance of class _Sublink.

        Arguments:
            env: A simpy.Environment instance.
            link: The link that the _Sublink instance is a part of.
            transmitter_port: An instance of Port that will be attached to
                the link instance as the transmitter.
            receiver_port: An instance of Port that will be attached to
                the link instance as the receiver.

        """
        self.env = env
        self.link = link
        self._transmitter_port = transmitter_port
        self._receiver_port = receiver_port
        env.process(self.run())

    @property
    def transmitter_port(self):
        """
        The port that is at the transmitting end of the _Sublink.

        """
        return self._transmitter_port

    @property
    def receiver_port(self):
        """
        The port that is at the receiving end of the _Sublink.

        """
        return self._receiver_port

    def run(self):
        """
        Get a message from the transmitter port and simulate its transmission.

        """
        while True:
            get_request = self.transmitter_port.out_queue.get()
            message = yield get_request
            log.debug("{} transmission of {} started".format(self, message))
            bytes_to_transmit = (ethernet.PREAMBLE_SIZE_BYTES +
                                 ethernet.SFD_SIZE_BYTES +
                                 message.size_bytes)
            # wait for the transmission + propagation time to elapse
            yield self.env.timeout(
                self.link.transmission_time_us(bytes_to_transmit) +
                self.link.propagation_delay_us)
            log.debug("{} transmission of {} finished".format(self, message))
            self.receiver_port.in_queue.put(message)
            # wait for the duration of the ethernet interframe gap to elapse
            yield self.env.timeout(
                self.link.transmission_time_us(ethernet.IFG_SIZE_BYTES))
            log.debug("{} inter frame gap finished".format(self))

    def __repr__(self):
        return "{}->{}".format(self.transmitter_port, self.receiver_port)

    def __str__(self):
        return "{}->{}".format(self.transmitter_port, self.receiver_port)


class NetworkDevice(object):
    """
    Models generic network devices.

    A NetworkDevice instance models a generic network device with a certain
    number of ethernet ports. Network devices can be interconnected by means of
    links attached to their ports:

    >>> env = simpy.Environment()
    >>> d = NetworkDevice(env, "some device", 1)
    >>> d2 = NetworkDevice(env, "another device", 1)
    >>> L = Link(env, d.ports[0], d2.ports[0], 100, 3)

    The main purpose of this class is to serve as the superclass for specific
    network devices such as Switch, MessagePlaybackDevice,
    MessageRecordingDevice, etc.

    """

    def __init__(self, env, name, num_ports):
        """
        Constructor for NetworkDevice instances.

        Arguments:
            env: A simpy.Environment instance.
            name: A string used to identify the NetworkDevice instance.
            num_ports: The number of ports that the NetworkDevice instance
                should have.

        """
        self.env = env
        self.ports = [Port(self.env, "{}-port{}".format(name, i))
                      for i in range(num_ports)]
        self.name = name

    def listen_for_messages(self, callback):
        """
        Simpy process that calls callback when messages are received.

        Arguments:
            callback: The function to be called when one or more messages are
                received. The function should accept a single parameter that is
                the list of received messages.

        Note that a simpy process is a generator function (a.k.a., co-routine).
        It should therefore not be called directly. Instead, it should be
        registered with a simpy environment using simpy.Environment().process

        Example:

        >>> class MyNetworkDevice(NetworkDevice):
        ...     def __init__(self, env, name, num_ports):
        ...         NetworkDevice.__init__(self, env, name, num_ports)
        ...         env.process(self.listen_for_messages(self.hello))
        ...     def hello(self, messages):
        ...         for msg in messages:
        ...             print("Hello message {}".format(msg))
        ...
        >>> env = simpy.Environment()
        >>> d = MyNetworkDevice(env, "some device", 1)

        """
        # generate get requests for all input queues
        requests = [port.in_queue.get() for port in self.ports]
        while requests:
            # helper variable for the asserts
            queues_with_pending_requests = [req.resource for req in requests]
            # There is a request for each input queue.
            assert set(self.input_queues) == set(queues_with_pending_requests)
            # For each input queue there's exactly one request.
            assert (
                len(queues_with_pending_requests) ==
                len(set(queues_with_pending_requests)))

            log.debug("{} waiting for next reception".format(self))
            completed_requests = (yield self.env.any_of(requests))
            received_messages = list(completed_requests.values())
            log.debug("{} received {}".format(
                self, received_messages))

            callback(received_messages)

            # Only leave the requests which have not been completed yet
            remaining_requests = [
                req for req in requests if req not in completed_requests]
            # Input queues that have been emptied since the last wake up.
            emptied_queues = [req.resource for req in completed_requests]
            # Add new get requests for the input queues that have been emptied.
            new_requests = []
            for input_queue in emptied_queues:
                new_requests.append(input_queue.get())
            requests = remaining_requests + new_requests

    def instruct_transmission(self, message, port):
        """
        Simpy process that transmits a given message through a given port.

        Arguments:
            message: Message instance to be transmitted.
            port: Port of self through which to transmit the message.

        Raises:
            FT4FTTSimException if port is not an element of self.ports.

        Note that instruct_transmission() is a generator function. It should
        not be called directly, but only passed as a parameter to the process()
        method of a simpy Environment instance.

        Example:

        >>> env = simpy.Environment()
        >>> d = NetworkDevice(env, "some device", 1)
        >>> d2 = NetworkDevice(env, "another device", 1)
        >>> L = Link(env, d.ports[0], d2.ports[0], 100, 3)
        >>> m = Message(env, d, d2, 1234, "some message")
        >>> env.process(d.instruct_transmission(m, d.ports[0]))
        <Process(instruct_transmission) object at 0x...>

        """
        log.debug("{} instructing transmission of {} on {}".format(
            self, message, port))
        if port not in self.ports:
            raise FT4FTTSimException("{} is not a port of {}".format(
                port, self))
        log.debug("{} queued for transmission".format(message))
        yield port.out_queue.put(message)

    @property
    def input_queues(self):
        """
        Returns a list of all the input queues of the NetworkDevice instance.

        """
        return [port.in_queue for port in self.ports]

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name


class EchoDevice(NetworkDevice):
    """
    Models a device that retransmits any message it receives.

    Instances of this class are mainly used for testing purposes.

    """

    def __init__(self, env, name):
        """
        Creates a new EchoDevice instance.

        Arguments:
            env: A simpy.Environment instance.
            name: A string used to identify the EchoDevice instance.

        """
        NetworkDevice.__init__(self, env, name, 1)
        self.env.process(self.listen_for_messages(self.echo))

    def echo(self, messages):
        """
        Transmits messages through port number 0 of self.

        Arguments:
            messages: An iterable of the messages to transmit.

        """
        for msg in messages:
            self.env.process(self.instruct_transmission(msg, self.ports[0]))


class MessageRecordingDevice(NetworkDevice):
    """
    Models receivers that record and timestamp each received message.

    The main purpose of instances of this class is to make testing easier.

    """

    def __init__(self, env, name, num_ports):
        """
        Create a new MessageRecordingDevice instance.

        Arguments:
            env: A simpy.Environment instance.
            name: A string used to identify the MessageRecordingDevice
                instance.
            num_ports: The number of ports that the MessageRecordingDevice
                instance should have.

        """
        NetworkDevice.__init__(self, env, name, num_ports)
        self.reception_records = {}
        self.env.process(self.listen_for_messages(self.do_timestamp_messages))

    def do_timestamp_messages(self, messages):
        """
        Timestamp each message in messages with the current time.

        """
        timestamp = self.env.now
        self.reception_records[timestamp] = messages
        log.debug("{} recorded {}".format(self, self.reception_records))

    @property
    def recorded_messages(self):
        """
        Return the messages so far received by self.

        """
        messages = []
        for time in sorted(self.reception_records):
            messages.extend(self.reception_records[time])
        return messages

    @property
    def recorded_timestamps(self):
        """
        Return list of instants of time when messages have been received.

        The list is sorted from earlier time instants to later time instants.

        """
        return sorted(self.reception_records.keys())


class MessagePlaybackDevice(NetworkDevice):
    """
    Instances of this class model devices that transmit prespecified messages.

    Instances of this class accept a series of transmission commands and then
    execute them. Each transmission command specifies what message to transmit,
    at what time, and through which port.

    The main purpose of instances of this class is to make testing easier.

    """

    def __init__(self, env, name, num_ports):
        NetworkDevice.__init__(self, env, name, num_ports)
        env.process(self.run())
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
                the ports on which transmissions should be ordered and
                whose values are lists of messages to be transmitted through
                the corresponding port. Example:

                {
                    0.0:  {port1: [message1, message2]},
                    12.0: {port1: [message3]},
                    13.5: {port3: [message4, message5, message6]}
                }

        """
        self.transmission_commands = transmission_commands
        log.debug("{} loaded transmissions: {}".format(
            self, self.transmission_commands))

    def run(self):
        """
        Simpy process that executes previously loaded transmission commands.

        """
        for time in sorted(self.transmission_commands):
            delay_before_next_tx_order = time - self.env.now
            log.debug("{} waiting for next transmission time".format(self))
            # wait until next transmission time
            yield self.env.timeout(delay_before_next_tx_order)
            for port, messages_to_tx in \
                    self.transmission_commands[time].items():
                for message in messages_to_tx:
                    self.env.process(
                        self.instruct_transmission(message, port))

    @property
    def transmission_start_times(self):
        """
        Returns a list of time instants when transmissions will be instructed.

        """
        return sorted(self.transmission_commands.keys())


class MessagePlaybackAndRecordingDevice(
        MessagePlaybackDevice, MessageRecordingDevice):
    """
    Models devices that transmit pre-specified messages and record messages.

    """

    def __init__(self, env, name, num_ports):
        MessagePlaybackDevice.__init__(self, env, name, num_ports)
        self.reception_records = {}
        self.env.process(self.listen_for_messages(self.do_timestamp_messages))


class Switch(NetworkDevice):
    """
    Models standard Ethernet switches.

    """

    def __init__(self, env, name, num_ports, forwarding_table=None):
        """
        Creates a new Switch instance.

        Arguments:
            env: A simpy.Environment instance.
            name: A string used to identify the new switch instance.
            num_ports: The number of ports that the new switch instance should
                have.
            forwarding_table: Dictionary whose keys are network devices and
                whose values are ports of the Switch instance.

        """
        NetworkDevice.__init__(self, env, name, num_ports)
        env.process(self.listen_for_messages(self.forward_messages))
        if forwarding_table is None:
            self.forwarding_table = {}
        else:
            self.forwarding_table = forwarding_table

    def forward_messages(self, message_list):
        """
        Forward each message in 'message_list' through the appropriate port.

        Note that forwarding a message from one port to another port is
        implemented as creating a new message instance based on the message
        in the first port, and transmitting the new message instance on the
        second port.

        """

        def find_ports(destination):
            """
            Return a list of the ports that according to the forwarding table
            lead to 'destination'.

            Arguments:
                destination: an instance of class NetworkDevice or an iterable
                    of NetworkDevice instances.

            Returns:
                A set of the ports that lead to the devices in 'destination'.

            """
            output_ports = set()
            if isinstance(destination, collections.Iterable):
                for device in destination:
                    # ports leading to device
                    ports_towards_device = self.forwarding_table.get(
                        device, self.ports)
                    output_ports.update(ports_towards_device)
            else:
                output_ports.update(
                    self.forwarding_table.get(destination, self.ports))
            return output_ports

        for message in message_list:
            destinations = message.destination
            output_ports = find_ports(destinations)
            for port in output_ports:
                new_message = Message.from_message(message)
                self.env.process(
                    self.instruct_transmission(new_message, port))


class Message(object):
    """
    Class for messages that model Ethernet frames.

    """
    # next available identifier for message objects
    next_identifier = 0

    def __init__(
            self, env, source, destination, size_bytes, message_type,
            data=None):
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
            data: The data to be carried within the message. It models the
                Ethernet data field.

        """
        if not isinstance(size_bytes, int):
            raise FT4FTTSimException("Message size must be integer")
        if not (ethernet.MIN_FRAME_SIZE_BYTES <= size_bytes <=
                ethernet.MAX_FRAME_SIZE_BYTES):
            raise FT4FTTSimException(
                "Message size must be between {} and {}, but is {}".format(
		    ethernet.MIN_FRAME_SIZE_BYTES, ethernet.MAX_FRAME_SIZE_BYTES,
		    size_bytes))
        self.env = env
        self._identifier = Message.next_identifier
        Message.next_identifier += 1
        # source of the message. Models the source MAC address.
        self.source = source
        # destination of the message. It models the destination MAC address. It
        # is a list to allow multicast addressing.
        self.destination = destination
        self.size_bytes = size_bytes
        self.message_type = message_type
        self.data = data
        self.name = "({:03d}, {}, {}, {:d}, {}, {})".format(
            self.identifier, self.source, self.destination, self.size_bytes,
            self.message_type, self.data)
        log.debug("{} created".format(self))

    @property
    def identifier(self):
        """
        Integer that uniquely identifies the Message instance.

        """
        return self._identifier

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
            template_message.message_type,
            template_message.data)
        return new_equivalent_message

    def __eq__(self, message):
        """
        Returns true if self and message are identical except for the message
        identifier.

        """
        return (self.source == message.source and
                self.destination == message.destination and
                self.size_bytes == message.size_bytes and
                self.message_type == message.message_type and
                self.data == message.data)

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name
