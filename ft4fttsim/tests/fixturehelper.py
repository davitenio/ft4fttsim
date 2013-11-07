# author: David Gessner <davidges@gmail.com>


PLAYBACK_CONFIGS = [
    "single message",
    "single message where destination is list",
    "2 messages",
    "8 messages",
    "3 batches of 2 messages",
]


def make_playback_device(config, env, msg_destination, link):
    """
    Return a new instance of MessagePlaybackDevice configured according to the
    arguments.

    ARGUMENTS:
        config: one of the values in the list PLAYBACK_CONFIGS.
        env: an instance of simpy.Environment
        msg_destination: value to put into the destination field of the
            messages to be transmitted by the playback device that will be
            created.
        link: an instance of Link that will be attached as the outlink for the
            playback device that will be created.

    """
    from ft4fttsim.networking import MessagePlaybackDevice, Message
    player = MessagePlaybackDevice(env, "player")
    player.connect_outlink(link)
    if config == "single message":
        messages = [Message(env, player, msg_destination, 1518, "message")]
        player.load_transmission_commands(
            {
                0: {link: messages}
            }
        )
        player.messages_to_transmit = messages
    elif config == "single message where destination is list":
        messages = [Message(env, player, [msg_destination], 158,
            "message")]
        player.load_transmission_commands(
            {
                0: {link: messages}
            }
        )
        player.messages_to_transmit = messages
    elif config == "2 messages":
        message_lists = [
            [Message(env, player, msg_destination, 1200, "message0")],
            [Message(env, player, msg_destination, 1000, "message1")],
        ]
        player.load_transmission_commands(
            {
                0: {link: message_lists[0]},
                1: {link: message_lists[1]},
            }
        )
        player.messages_to_transmit = [message for message_list in
            message_lists for message in message_list]
    elif config == "8 messages":
        message_lists = [
            [Message(env, player, msg_destination, 1200, "message0")],
            [Message(env, player, msg_destination, 1000, "message1")],
            [Message(env, player, msg_destination, 958, "message2")],
            [Message(env, player, msg_destination, 958, "message3")],
            [Message(env, player, msg_destination, 1508, "message4")],
            [Message(env, player, msg_destination, 90, "message5")],
            [Message(env, player, msg_destination, 1111, "message6")],
            [Message(env, player, msg_destination, 1234, "message7")],
        ]
        player.load_transmission_commands(
            {
                0: {link: message_lists[0]},
                1: {link: message_lists[1]},
                5: {link: message_lists[2]},
                6: {link: message_lists[3]},
                9: {link: message_lists[4]},
                15: {link: message_lists[5]},
                123: {link: message_lists[6]},
                11114: {link: message_lists[7]},
            }
        )
        player.messages_to_transmit = [message for message_list in
            message_lists for message in message_list]
    elif config == "3 batches of 2 messages":
        message_lists = [
            [Message(env, player, msg_destination, 142, "batch0 message0"),
            Message(env, player, msg_destination, 1000, "batch0 message1")],
            [Message(env, player, msg_destination, 218, "batch1 message0"),
            Message(env, player, msg_destination, 1050, "batch1 message1")],
            [Message(env, player, msg_destination, 1381, "batch2 message0"),
            Message(env, player, msg_destination, 150, "batch2 message1")],
        ]
        player.load_transmission_commands(
            {
                100: {link: message_lists[0]},
                111: {link: message_lists[1]},
                555: {link: message_lists[2]},
            }
        )
        player.messages_to_transmit = [message for message_list in
            message_lists for message in message_list]
    return player


# list of (Mbps, propagation delay) tuples
LINK_CONFIGS = [(10, 3), (100, 0), (1000, 9)]


def make_link(config, env):
    from ft4fttsim.networking import Link
    Mbps, delay = config
    return Link(env, megabits_per_second=Mbps, propagation_delay_us=delay)
