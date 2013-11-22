# author: David Gessner <davidges@gmail.com>

import simpy
from ft4fttsim.networking import NetworkDevice, Port, Link, Message
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
        # Port leading to the embedded master.
        self.internal_port = Port(env, self)
        # All ports of the switch.
        self.ports.append(self.internal_port)
        # Ports leading to devices other than the embedded master.
        self.external_ports = self.ports[:-1]
        Link(env, self.internal_port, master.ports[0], float("inf"), 0)
        self.master = master
        env.process(self.listen_for_messages(self.process_received_messages))

    def flood_message(self, message):
        for port in self.external_ports:
            self.env.process(
                self.instruct_transmission(message, port))

    def process_received_messages(self, messages):
        for m in messages:
            if m.destination == self.master:
                self.env.process(
                    self.instruct_transmission(m, self.internal_port))
            elif m.message_type == Message.Type.TRIGGER_MESSAGE:
                self.flood_message(m)
