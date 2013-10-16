# author: David Gessner <davidges@gmail.com>

from SimPy.Simulation import *
from ethernet import Ethernet
from exceptions import FT4FTTSimException


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
        self.name = "{:s}->{:s}".format(self.start_point, self.end_point)
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
        return self.name


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
        if outlink not in self.get_outlinks():
            raise FT4FTTSimException("{} is not an outlink of {}".format(
                outlink, self))
        activate(new_message, message.transmit(link))

    def __str__(self):
        return self.name


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
            # sleep until a message is received
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
        self.name = "({:03d}, {:s}, {:s}, {:s})".format(self.ID, self.source,
            self.destination_list, self.message_type)

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
        yield request, self, link
        transmission_time = self.length
        link.put_message(self)
        yield hold, self, (transmission_time + link.propagation_time +
            Ethernet.IFG)
        yield release, self, link
        reactivate(link.end_point)

    def is_trigger_message(self):
        return self.message_type == "TM"

    def __str__(self):
        return self.name
