# author: David Gessner <davidges@gmail.com>
"""
Provides constants for the length in bytes of Ethernet frame fields.

All constants indicate length measured in bytes.

"""

# Ethernet IEEE 802.3 preamble length
PREAMBLE_SIZE_BYTES = 7
# Ethernet IEEE 802.3 start of frame delimiter length
SFD_SIZE_BYTES = 1
# Length of a source or destination address field
MAC_ADDRESS_SIZE_BYTES = 6
# Length of the ethertype field
ETHERTYPE_SIZE_BYTES = 2
# Length of the frame check sequence
FCS_SIZE_BYTES = 4
# Ethernet interframe gap length
IFG_SIZE_BYTES = 12
# minimum payload length
MIN_PAYLOAD_SIZE_BYTES = 46
# minimum frame length
MIN_FRAME_SIZE_BYTES = (
    2 * MAC_ADDRESS_SIZE_BYTES + ETHERTYPE_SIZE_BYTES +
    MIN_PAYLOAD_SIZE_BYTES + FCS_SIZE_BYTES)
# maximum payload length
MAX_PAYLOAD_SIZE_BYTES = 1500
# maximum frame length
MAX_FRAME_SIZE_BYTES = (
    2 * MAC_ADDRESS_SIZE_BYTES + ETHERTYPE_SIZE_BYTES +
    MAX_PAYLOAD_SIZE_BYTES + FCS_SIZE_BYTES)
