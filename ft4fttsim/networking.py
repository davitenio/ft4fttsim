# author: David Gessner <davidges@gmail.com>

from SimPy.Simulation import *
from ethernet import Ethernet
from exceptions import FT4FTTSimException
from simlogging import log


class Link(Resource):
    """
    Class for links used in the FT4FTT network. Objects of this class may
    interconnect arbitrary NetworkDevices.
    """
    def __init__(self, propagation_time):
        """
        Creates a link whose propagation time is propagation_time.
        """
        assert propagation_time >= 0
        Resource.__init__(self, 1)
        self.start_point = None
        self.end_point = None
        self.propagation_time = propagation_time
        # message that is being transmitted in the link
        self.message = None

    def set_start_point(self, device):
        self.start_point = device

    def set_end_point(self, device):
        self.end_point = device

    def get_end_point(self):
        return self.end_point

    def has_message(self):
        return self.message != None

    def put_message(self, message):
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
            link.set_start_point(self)
            self.connect_outlink(link)

    def connect_inlink_list(self, link_list):
        for link in link_list:
            link.set_end_point(self)
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
        self.recorded_messages = []

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
            yield passivate, self
            received_messages = self.read_inlinks()
            log.debug("{:s} received {}".format(self,
                received_messages))
            timestamp = now()
            self.recorded_messages.append((timestamp,
                received_messages))
            log.debug("{:s} recorded {}".format(self, self.recorded_messages))


class MessagePlaybackDevice(NetworkDevice):
    def __init__(self, name):
        """
        list_of_transmissions is a list of '(time, message_list)'
        tuples, where each 'time' indicates the instant of time when the
        messages in the list 'message_list' should be transmitted.
        """
        NetworkDevice.__init__(self, name)
        self.list_of_transmissions = []

    def load_transmissions(self, list_of_transmissions):
        self.list_of_transmissions = list_of_transmissions
        self.list_of_transmissions.sort()
        log.debug("{:s} loaded transmissions: {}".format(self,
            self.list_of_transmissions))

    def connect_inlink(self, link):
        raise NotImplementedError()

    def connect_inlink_list(self, link):
        raise NotImplementedError()

    def read_inlinks(self):
        raise NotImplementedError()

    def run(self):
        for time, message_list, outlink in self.list_of_transmissions:
            delay_before_next_tx_order = time - now()
            log.debug("{:s} sleeping until next transmission".format(self))
            # sleep until next transmission time
            yield hold, self, delay_before_next_tx_order
            for message in message_list:
                self.instruct_transmission(message, outlink)


class Switch(NetworkDevice):
    """
    Class for ethernet switches.
    """

    def forward_messages(self, message_list):
        """
        Forward each message in message_list to the appropriate outlink.
        """

        def find_outlinks(destination_list):
            """
            Return a list of the outlinks that have as their endpoint one of
            the network devices in the list destination_list.
            """
            destination_outlinks = []
            for outlink in self.get_outlinks():
                if outlink.get_end_point() in destination_list:
                    destination_outlinks.append(outlink)
            return destination_outlinks

        for message in message_list:
            destinations = message.get_destination_list()
            destination_outlinks = find_outlinks(destinations)
            for link in destination_outlinks:
                new_message = Message(message.get_source(),
                    message.get_destination_list(),
                    message.length,
                    message.message_type)
                self.instruct_transmission(new_message, link)

    def run(self):
        while True:
            # sleep until a message notifies that it has finished transmission
            yield passivate, self
            received_messages = self.read_inlinks()
            self.forward_messages(received_messages)


class Message(Process):
    """
    Class for messages sent by a NetworkDevice.
    """
    # next available ID for message objects
    next_ID = 0

    def __init__(self, source, destination_list, length, msg_type):
        Process.__init__(self)
        self.ID = Message.next_ID
        Message.next_ID += 1
        # source of the message. Models the source MAC address.
        self.source = source
        # destination of the message. It models the destination MAC address. It
        # is a list to allow multicast addressing.
        self.destination_list = destination_list
        assert (Ethernet.MIN_FRAME_LENGTH <= length
            <= Ethernet.MAX_FRAME_LENGTH)
        self.length = length
        self.message_type = msg_type
        self.name = "({:03d}, {:s}, {:s}, {:d}, {:s})".format(self.ID,
            self.source, self.destination_list, self.length,
            self.message_type)
        log.debug("{:s} created".format(self))

    def get_destination_list(self):
        """
        Return the destination NetworkDevice for the message, which models
        the destination MAC address.
        """
        return self.destination_list

    def get_source(self):
        """
        Return the source NetworkDevice for the message, which models the
        source MAC address.
        """
        return self.source

    def transmit(self, link):
        """
        Transmit the message instance on the Link link.
        """
        log.debug("{:s} queued for transmission".format(self))
        # request access to, and possibly queue for, the link
        yield request, self, link
        log.debug("{:s} transmission started".format(self))
        transmission_time = self.length
        link.put_message(self)
        # wait for the transmission + propagation time to elapse
        yield hold, self, transmission_time + link.propagation_time
        # transmission finished, notify the link's end point, but do not
        # release the link yet
        log.debug("{:s} transmission finished".format(self))
        reactivate(link.end_point)
        # wait for the duration of the ethernet interframe gap to elapse
        yield hold, self, Ethernet.IFG
        log.debug("{:s} inter frame gap finished".format(self))
        # release the link, allowing another message to gain access to it
        yield release, self, link

    def is_trigger_message(self):
        return self.message_type == "TM"

    def __str__(self):
        return self.name
