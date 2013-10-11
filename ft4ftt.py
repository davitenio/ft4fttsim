from SimPy.Simulation import *
import logging

class SimLoggerAdapter(logging.LoggerAdapter):
    def process(self, log_msg, kwargs):
        return "{:>8.2f}: {:s}".format(now(), log_msg), kwargs

logging.basicConfig(level=logging.DEBUG, format="%(levelname)5s %(message)s")
log = SimLoggerAdapter(logging.getLogger('ft4fttsim'), {})

## Model components ------------------------

class Ethernet:
    # All lengths are indicated in bytes
    # Ethernet IEEE 802.3 preamble length
    PREAMBLE_LENGTH = 7
    # Ethernet IEEE 802.3 start of frame delimiter length
    SFD_LENGTH = 1
    # Length of a source or destination address field
    MAC_ADDRESS_LENGTH = 6
    # Length of the ethertype field
    ETHERTYPE_LENGTH = 2
    # Length of the frame check sequence
    FCS_LENGTH = 4
    # Ethernet interframe gap length
    IFG = 12
    # minimum payload length
    MIN_PAYLOAD_LENGTH = 46
    # minimum frame length
    MIN_FRAME_LENGTH = (PREAMBLE_LENGTH + SFD_LENGTH + 2 * MAC_ADDRESS_LENGTH +
        ETHERTYPE_LENGTH + MIN_PAYLOAD_LENGTH + FCS_LENGTH)
    # maximum payload length
    MAX_PAYLOAD_LENGTH = 1500
    # maximum frame length
    MAX_FRAME_LENGTH = (PREAMBLE_LENGTH + SFD_LENGTH + 2 * MAC_ADDRESS_LENGTH +
        ETHERTYPE_LENGTH + MAX_PAYLOAD_LENGTH + FCS_LENGTH)


class FTT:
    EC_LENGTH = Ethernet.MAX_FRAME_LENGTH * 10
    # This counter is incremented after each successive elementary cycle
    EC_count = 0


class Link:
    """ Class for links used in the FT4FTT network. Objects of this class may
    interconnect arbitrary network components, e.g., slaves, masters, switches.
    """
    def __init__(self, start_point, end_point, propagation_time):
        self.start_point = start_point
        self.end_point = end_point
        self.propagation_time = propagation_time
        self.name = "{:s}->{:s}".format(start_point, end_point)
        self.resource = Resource(1, name="resource for " + self.name)
        # message that is being transmitted in the link
        self.message = None

    def has_message(self):
        return self.message != None

    def put_message(self, message):
        self.message = message
        log.debug("{:s}: accepted message {:s}".format(self, self.message))

    def get_message(self):
        tmp = self.message
        self.message = None
        return tmp

    def __str__(self):
        return self.name




class Slave(Process):
    """ Class for FTT slaves """
    # set of all slave objects
    slave_set = set()
    # next available ID for slave objects
    next_ID = 0

    def __init__(self):
        Process.__init__(self)
        self.ID = Slave.next_ID
        self.name = "slave{:d}".format(self.ID)
        Slave.next_ID += 1
        # list of outlinks to which the slave is connected
        self.outlinks = []
        # list of inlinks to which the slave is connected
        self.inlinks = []
        Slave.slave_set.add(self)

    def get_outlinks(self):
        return self.outlinks

    def get_inlinks(self):
        return self.inlinks

    def connect_outlink(self, link):
        self.outlinks.append(link)

    def connect_inlink(self, link):
        self.inlinks.append(link)

    def read_inlinks(self):
        received_messages = []
        for inlink in self.get_inlinks():
            if inlink.has_message():
                received_messages.append(inlink.get_message())
        log.info("{:s}: received messages {:s}".format(self,
            received_messages))
        return received_messages

    def transmit_synchronous_messages(self,
            # number of messages to transmit
            number,
            # links on which to transmit each of the messages
            links):
        for message_count in range(number):
            msg_destination = slave.slave_set - set([self])
            new_message = message(self, msg_destination, "sync")
            new_message.length = ethernet.max_frame_length
            # order the transmission of the message on the specified links
            for outlink in links:
                activate(new_message, new_message.transmit(outlink))

    def run(self):
        while True:
            # sleep until a message is received
            yield passivate, self
            received_messages = read_inlinks()
            has_received_trigger_message = false
            for message in received_messages:
                if message.is_trigger_message():
                    has_received_trigger_message = True
            if has_received_trigger_message:
                # transmit on all outlinks
                transmit_synchronous_messages(2, self.get_outlinks())
                # wait before we order the next transmission
                delay_before_next_tx_order = 0.0
                yield hold, self, delay_before_next_tx_order

    def __str__(self):
        return self.name



class Switch(Process):
    """ Class for ethernet switches """
    # list of all switch objects
    switch_list = []
    # next available ID for switch objects
    next_ID = 0

    def __init__(self):
        Process.__init__(self)
        self.ID = Switch.next_ID
        Switch.next_ID += 1
        self.name = "switch{:d}".format(self.ID)
        # list of outlinks to which the switch is connected
        self.outlinks = []
        # list of inlinks to which the switch is connected
        self.inlinks = []
        Switch.switch_list.append(self)

    def connect_outlink(self, link):
        self.outlinks.append(link)

    def connect_inlink(self, link):
        self.inlinks.append(link)

    def read_inlinks(self):
        received_messages = []
        for inlink in self.get_inlinks():
            log.debug("{:s}: checking {:s} for messages".format(self,
                inlink))
            if inlink.has_message():
                received_messages.append(inlink.get_message())
        log.info("{:s}: received messages {:s}".format(self,
            received_messages))
        return received_messages

    def get_outlinks(self):
        return self.outlinks

    def get_inlinks(self):
        return self.inlinks

    def run(self):
        while True:
            # sleep until a message is received
            yield passivate, self
            received_messages = self.read_inlinks()
            log.info("{:s}: received messages {:s}".format(self,
                received_messages))
            # TODO: implement switching


    def __str__(self):
        return self.name


class Master(Process):
    """ Class for FTT masters """
    # list of all of master objects
    master_list = []
    # next available ID for master objects
    next_ID = 0

    def __init__(self,
            elementary_cycle_length,
            # number of trigger messages to transmit per elementary cycle
            num_trigger_messages=1):
        Process.__init__(self)
        self.ID = Master.next_ID
        Master.next_ID += 1
        self.EC_length = elementary_cycle_length
        self.name = "master{:d}".format(self.ID)
        # list of outlinks to which the master is connected
        self.outlinks = []
        # list of inlinks to which the master is connected
        self.inlinks = []
        self.num_trigger_messages = num_trigger_messages
        Master.master_list.append(self)

    def get_outlinks(self):
        return self.outlinks

    def get_inlinks(self):
        return self.inlinks

    def connect_outlink(self, link):
        self.outlinks.append(link)

    def connect_inlink(self, link):
        self.inlinks.append(link)

    def broadcast_trigger_message(self):
        trigger_message = Message(self, Slave.slave_set, "TM")
        trigger_message.length = Ethernet.MAX_FRAME_LENGTH
        for outlink in self.get_outlinks():
            log.info("{:s}: instructing transmission of {:s}".format(
                self, trigger_message))
            activate(trigger_message,
                trigger_message.transmit(outlink))

    def run(self):
        while True:
            log.info("==== {:s}: EC {:d} ====".format(
                self, FTT.EC_count))
            FTT.EC_count += 1
            time_last_EC_start = now()
            for message_count in range(self.num_trigger_messages):
                self.broadcast_trigger_message()
            # wait for the next elementary cycle to start
            while True:
                time_since_EC_start = now() - time_last_EC_start
                delay_before_next_tx_order = float(self.EC_length -
                    time_since_EC_start)
                if delay_before_next_tx_order > 0:
                    log.info("{:s}: sleeping for {:7.2f} time units".format(
                        self, delay_before_next_tx_order))
                    yield hold, self, delay_before_next_tx_order
                else:
                    break

    def __str__(self):
        return self.name



class Message(Process):
    """ Class for messages sent by a slave """
    # next available ID for message objects
    next_ID = 0

    def __init__(self, source, destination, msg_type):
        Process.__init__(self)
        self.ID = Message.next_ID
        self.source = source
        self.destination = destination
        self.message_type = msg_type
        Message.next_ID += 1
        self.name = "({:03d}, {:s}, {:s}, {:s})".format(self.ID, self.source,
            self.destination, self.message_type)

    def transmit(self, link):
        log.info("{link:s} {msg:s}: waiting for transmission".format(
            link=link, msg=self))
        yield request, self, link.resource
        log.info("{link:s} {msg:s}: transmission started".format(
            link=link, msg=self))
        transmission_time = self.length
        link.put_message(self)
        yield hold, self, (transmission_time + link.propagation_time +
            Ethernet.IFG)
        yield release, self, link.resource
        log.info("{link:s} {msg:s}: transmission finished".format(
            link=link, msg=self))
        reactivate(link.end_point)

    def is_trigger_message(self):
        return self.message_type == "TM"

    def __str__(self):
        return self.name


class TriggerMessage(Message):
    """ Class for trigger messages sent by the FTT masters """

    def __init__(self):
        Message.__init__(self)
        self.name = "TM{:03d}".format(self.ID)



def create_network(
        # number of slaves to create in the network
        num_slaves,
        # number of masters to create in the network
        num_masters,
        # number of switches to create in the network
        num_switches):
    def create_network_components(
            num_slaves,
            num_masters,
            num_switches):
        slaves = []
        masters = []
        switches = []
        for i in range(num_slaves):
            new_slave = Slave()
            slaves.append(new_slave)
        for i in range(num_masters):
            new_master = Master(FTT.EC_LENGTH, 1)
            masters.append(new_master)
        for i in range(num_switches):
            new_switch = Switch()
            switches.append(new_switch)
        return slaves, masters, switches

    def setup_network_topology(slaves, masters, switches):
        # connect each slave with all switches
        for slave in slaves:
            for switch in switches:
                slave_outlink = Link(slave, switch, 0)
                slave_inlink = Link(switch, slave, 0)
                slave.connect_outlink(slave_outlink)
                slave.connect_inlink(slave_inlink)
                switch.connect_outlink(slave_inlink)
                switch.connect_inlink(slave_outlink)
        # connect each master to a different single switch
        assert len(masters) == len(switches)
        for master, switch in zip(masters, switches):
            master_outlink = Link(master, switch, 0)
            master_inlink = Link(switch, master, 0)
            master.connect_outlink(master_outlink)
            master.connect_inlink(master_inlink)
            switch.connect_inlink(master_outlink)
            switch.connect_outlink(master_inlink)

    network = create_network_components(num_slaves, num_masters, num_switches)
    setup_network_topology(*network)
    return network


## Model/Experiment ------------------------------

config = {
    'simulation_time': Ethernet.MAX_FRAME_LENGTH * 13,
    'num_slaves': 2,
    'num_masters':  1,
    'num_switches': 1,
}

def activate_network(network):
     for list_of_components in network:
        for component in list_of_components:
            activate(component, component.run(), at=0.0)

def main():
    # initialize SimPy
    initialize()
    network = create_network(
        config['num_slaves'], config['num_masters'], config['num_switches'])
    activate_network(network)
    simulate(until=config['simulation_time'])

if __name__ == '__main__': main()
