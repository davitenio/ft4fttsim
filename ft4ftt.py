from SimPy.Simulation import *

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

class Link:
    """ Class for links between slaves and switches, and for interlinks between
    switches. Note that each link is unidirectional. """
    def __init__(self, source, destination, propagation_time):
        self.source = source
        self.destination = destination
        self.propagation_time = propagation_time
        self.name = "Link {:s}->{:s}".format(source, destination)
        self.resource = Resource(1, name="resource for " + self.name)

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
        self.uplink0 = Link(self, Master.master_list[0], propagation_time=0)
        self.downlink0 = Link(Master.master_list[0], self, propagation_time=0)
        Slave.slave_set.add(self)

    def order_message_transmissions(self, number):
        for message_count in range(number):
            m = Message()
            m.length = Ethernet.MIN_FRAME_LENGTH
            # order the transmission of the message
            activate(m, m.transmit(m, self.uplink0))
            # wait before we order the next transmission
            delay_before_next_tx_order = 0.0
            yield hold, self, delay_before_next_tx_order

    def __str__(self):
        return self.name



class Master(Process):
    """ Class for FTT masters """
    # list of all of master objects
    master_list = []
    # next available ID for master objects
    next_ID = 0

    def __init__(self):
        Process.__init__(self)
        self.ID = Master.next_ID
        Master.next_ID += 1
        self.name = "master{:d}".format(self.ID)
        Master.master_list.append(self)

    def order_trigger_message_transmission(self, number):
        for message_count in range(number):
            for slave in Slave.slave_set:
                m = Message()
                m.length = Ethernet.MIN_FRAME_LENGTH
                # order the transmission of the trigger message
                activate(m, m.transmit(m, slave.downlink0))
                delay_before_next_tx_order = 0.0
                yield hold, self, delay_before_next_tx_order

    def __str__(self):
        return self.name



class Message(Process):
    """ Class for messages sent by a slave """
    # next available ID for message objects
    next_ID = 0

    def __init__(self):
        Process.__init__(self)
        self.ID = Message.next_ID
        Message.next_ID += 1
        self.name = "msg{:03d}".format(self.ID)

    def transmit(self, message, link):
        transmission_time = message.length
        print "{:7.2f} {link:s} {msg:s}: waiting for transmission".format(now(),
            link=link, msg=self)
        yield request, self, link.resource
        print "{:7.2f} {link:s} {msg:s}: transmission started".format(now(),
            link=link, msg=self)
        yield hold, self, (transmission_time + link.propagation_time +
            Ethernet.IFG)
        yield release, self, link.resource
        print "{:7.2f} {link:s} {msg:s}: transmission finished".format(now(),
            link=link, msg=self)

    def __str__(self):
        return self.name



## Experiment data -------------------------

maxNumber = 5
simulation_time = Ethernet.MAX_FRAME_LENGTH * 100

## Model/Experiment ------------------------------

def main():
    initialize()
    master0 = Master()
    slave0 = Slave()
    activate(slave0, slave0.order_message_transmissions(number=maxNumber),
        at=0.0)
    activate(master0,
        master0.order_trigger_message_transmission(number=maxNumber), at=0.0)
    simulate(until=simulation_time)

if __name__ == '__main__': main()
