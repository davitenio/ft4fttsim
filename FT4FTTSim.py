# author: David Gessner <davidges@gmail.com>

from ft4fttsim.networking import Link, Switch
from ft4fttsim.masterslave import Slave, Master
from ft4fttsim.ethernet import Ethernet
from SimPy.Simulation import initialize, activate, simulate, now
import logging


class SimLoggerAdapter(logging.LoggerAdapter):
    def process(self, log_msg, kwargs):
        return "{:>8.2f}: {:s}".format(now(), log_msg), kwargs

logging.basicConfig(level=logging.DEBUG, format="%(levelname)5s %(message)s")
simlog = SimLoggerAdapter(logging.getLogger('ft4fttsim'), {})


def create_network(
        # number of slaves to create in the network
        num_slaves,
        # number of masters to create in the network
        num_masters,
        # number of switches to create in the network
        num_switches,
        # the length of the elementary cycles
        EC_length):
    def create_network_devices(
            num_slaves,
            num_masters,
            num_switches,
            EC_length):
        slaves = []
        masters = []
        switches = []
        for slave_idx in range(num_slaves):
            new_slave = Slave("slave{:d}".format(slave_idx))
            slaves.append(new_slave)
        for master_idx in range(num_masters):
            new_master = Master("master{:d}".format(master_idx), slaves,
                EC_length, 1)
            masters.append(new_master)
        for switch_idx in range(num_switches):
            new_switch = Switch("switch{:d}".format(switch_idx))
            switches.append(new_switch)
        return slaves, masters, switches

    def setup_network_topology(slaves, masters, switches):
        # connect each slave with all switches
        for slave in slaves:
            for switch in switches:
                slave_outlink = Link(0)
                slave_inlink = Link(0)
                slave.connect_outlink(slave_outlink)
                slave.connect_inlink(slave_inlink)
                switch.connect_outlink(slave_inlink)
                switch.connect_inlink(slave_outlink)
        # connect each master to a different single switch
        assert len(masters) == len(switches)
        for master, switch in zip(masters, switches):
            master_outlink = Link(0)
            master_inlink = Link(0)
            master.connect_outlink(master_outlink)
            master.connect_inlink(master_inlink)
            switch.connect_inlink(master_outlink)
            switch.connect_outlink(master_inlink)

    assert isinstance(num_slaves, int)
    assert isinstance(num_masters, int)
    assert isinstance(num_switches, int)
    network = create_network_devices(num_slaves, num_masters, num_switches,
        EC_length)
    setup_network_topology(*network)
    return network


class Network:
    # TODO: implement a proper class for Network. For now it is simply here to
    # hold the list of slaves so that this list can be accessed as if it was a
    # global variable.
    slaves = None


def activate_network(network):
    for list_of_devices in network:
        for device in list_of_devices:
            activate(device, device.run(), at=0.0)


def main():
    config = {
        'simulation_time': Ethernet.MAX_FRAME_LENGTH * 4,
        'num_slaves': 2,
        'num_masters':  1,
        'num_switches': 1,
        'FTT_EC_length': Ethernet.MAX_FRAME_LENGTH * 20
    }

    # initialize SimPy
    initialize()
    logging.info("Simulation initialized")
    network = create_network(config['num_slaves'], config['num_masters'],
        config['num_switches'], config['FTT_EC_length'])
    activate_network(network)
    Network.slaves = network[0]
    logging.info("Starting simulation...")
    simulate(until=config['simulation_time'])
    logging.info("Simulation finished")


if __name__ == '__main__':
    main()
