from SimPy.Simulation import *
import logging

class SimLoggerAdapter(logging.LoggerAdapter):
    def process(self, log_msg, kwargs):
        return "{:>8.2f}: {:s}".format(now(), log_msg), kwargs

logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")
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
    """ Class for links between slaves and switches, and for interlinks between
    switches. Note that each link is unidirectional. """
    def __init__(self, source, destination, propagation_time):
        self.source = source
        self.destination = destination
        self.propagation_time = propagation_time
        self.name = "Link {:s}->{:s}".format(source, destination)
        self.resource = Resource(1, name="resource for " + self.name)
        # message that is being transmitted in the link
        self.message = None

    def put_message(self, m):
        self.message = m

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
        self.uplink0 = Link(self, Master.master_list[0], propagation_time=0)
        self.downlink0 = Link(Master.master_list[0], self, propagation_time=0)
        Slave.slave_set.add(self)

    def run(self):
        while True:
            # sleep until a message is received on downlink0
            yield passivate, self
            received_message = self.downlink0.get_message()
            log.info("{:s}: received message {:s}".format(self,
                received_message))
            number = 2
            for message_count in range(number):
                msg = Message()
                msg.length = Ethernet.MAX_FRAME_LENGTH
                # order the transmission of the message
                activate(msg, msg.transmit(self.uplink0))
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

    def run(self,
            # number of trigger messages to transmit per elementary cycle
            num_trigger_messages=1):
        while True:
            log.info("==== {:s}: EC {:d} ====".format(
                self, FTT.EC_count))
            FTT.EC_count += 1
            time_last_EC_start = now()
            for message_count in range(num_trigger_messages):
                for slave in Slave.slave_set:
                    trigger_msg = TriggerMessage()
                    trigger_msg.length = Ethernet.MAX_FRAME_LENGTH
                    log.info("{:s}: instructing transmission of {:s}".format(
                        self, trigger_msg))
                    activate(trigger_msg,
                        trigger_msg.transmit(slave.downlink0))
            while True:
                time_since_EC_start = now() - time_last_EC_start
                delay_before_next_tx_order = float(FTT.EC_LENGTH -
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

    def __init__(self):
        Process.__init__(self)
        self.ID = Message.next_ID
        Message.next_ID += 1
        self.name = "msg{:03d}".format(self.ID)

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
        reactivate(link.destination)

    def __str__(self):
        return self.name


class TriggerMessage(Message):
    """ Class for trigger messages sent by the FTT masters """

    def __init__(self):
        Message.__init__(self)
        self.name = "TM{:03d}".format(self.ID)



## Experiment configuration -------------------------

config = {
    'simulation_time': Ethernet.MAX_FRAME_LENGTH * 11,
    'num_slaves': 2,
}

## Model/Experiment ------------------------------

def create_slaves(number):
    for i in range(number):
        Slave()

def main():
    initialize()
    master0 = Master()
    create_slaves(config['num_slaves'])
    for slave in Slave.slave_set:
        activate(slave, slave.run(), at=0.0)
    activate(master0, master0.run(), at=0.0)
    simulate(until=config['simulation_time'])

if __name__ == '__main__': main()
