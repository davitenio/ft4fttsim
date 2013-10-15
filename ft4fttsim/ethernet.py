# author: David Gessner <davidges@gmail.com>


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
