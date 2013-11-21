# author: David Gessner <davidges@gmail.com>

import simpy
from ft4fttsim.networking import NetworkDevice, Port, Link
from ft4fttsim.exceptions import FT4FTTSimException


class FT4FTTSwitch(NetworkDevice):

    def __init__(self, env, name, num_ports, master):
        """
        Arguments:
            env: A simpy.Environment instance.
            name: A string used to identify the new switch instance.
            num_ports: The number of ports that the new switch instance should
                have.
            master: An FTT master (i.e., instance of Master) to be embedded
                within the FT4FTTSwitch instance.

        """
        if len(master.ports) != 1:
            raise FT4FTTSimException(
                "An embedded master must have exactly one port")
        NetworkDevice.__init__(self, env, name, num_ports)
        self.internal_port = Port(env, self)
        Link(env, self.internal_port, master.ports[0], float("inf"), 0)
        self.master = master
