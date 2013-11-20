# author: David Gessner <davidges@gmail.com>

from ft4fttsim.networking import NetworkDevice, Message


# TODO: update this class.  It is currently obsolete.
class Slave(NetworkDevice):
    """
    Class for FTT slaves.

    """

    def transmit_synchronous_messages(self, number, links):
        """
        Constructor for FTT slaves.

        ARGUMENTS:
            number: number of messages to transmit.
            links: links on which to transmit each of the messages.

        """
        assert isinstance(number, int)
        for message_count in range(number):
            # TODO: decide who each message should be transmitted to. For now
            # we simply send it to ourselves.
            new_message = Message(self.env, self, [self],
                                  Ethernet.MAX_FRAME_SIZE_BYTES, "sync")
            # order the transmission of the message on the specified links
            for outlink in links:
                self.instruct_transmission(new_message, outlink)

    def run(self):
        while True:
            # sleep until a message is received
            yield waitevent, self, [link.message_is_transmitted for link in
                                    self.inlinks]
            received_messages = self.read_inlinks()
            has_received_trigger_message = False
            for message in received_messages:
                if message.is_trigger_message():
                    has_received_trigger_message = True
            if has_received_trigger_message:
                # transmit on all outlinks
                self.transmit_synchronous_messages(2, self.outlinks)
                # wait before we order the next transmission
                delay_before_next_tx_order = 0.0
                yield self.env.timeout(delay_before_next_tx_order)
