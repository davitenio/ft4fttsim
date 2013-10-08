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
    switches """
    def __init__(self, name, propagation_time):
        self.resource = Resource(1, name=name)
        self.propagation_time = propagation_time


class Slave(Process):
    """ Class for FTT slaves """

    def __init__(self):
        Process.__init__(self)
        self.uplink0 = Link(name="Uplink to switch 0", propagation_time=0)

    def order_message_transmissions(self, number):
        for i in range(number):
            m = Message(name = "Message{:03d}".format(i,))
            m.length = Ethernet.MIN_FRAME_LENGTH
            # order the transmission of the message
            activate(m, m.transmit(m, self.uplink0))
            # we wait zero units of time before we order the next transmission
            delay_before_next_tx_order = 0.0
            yield hold, self, delay_before_next_tx_order

class Message(Process):
    """ Class for messages sent by a slave """

    def transmit(self, message, link):
        transmission_time = message.length
        print "{:7.2f} {:s}: waiting for transmission".format(now(), self.name)
        yield request, self, link.resource
        print "{:7.2f} {:s}: transmission started".format(now(), self.name)
        yield hold, self, (transmission_time + link.propagation_time +
            Ethernet.IFG)
        yield release, self, link.resource
        print "{:7.2f} {:s}: transmission finished".format(now(), self.name)

## Experiment data -------------------------

maxNumber = 5
maxTime = Ethernet.MAX_FRAME_LENGTH * 100

## Model/Experiment ------------------------------

def main():
    initialize()
    s = Slave()
    activate(s, s.order_message_transmissions(number=maxNumber), at=0.0)
    simulate(until=maxTime)

if __name__ == '__main__': main()
