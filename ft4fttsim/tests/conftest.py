# author: David Gessner <davidges@gmail.com>

import pytest


@pytest.fixture
def env():
    import simpy
    import ft4fttsim.simlogging
    new_env = simpy.Environment()
    ft4fttsim.simlogging.env = new_env
    return new_env


@pytest.fixture(params=[(10, 3), (100, 0), (1000, 9)])
def link(env, request):
    from ft4fttsim.networking import Link
    Mbps, delay = request.param
    return Link(env, megabits_per_second=Mbps, propagation_delay_us=delay)


@pytest.fixture
def switch(env):
    from ft4fttsim.networking import Switch
    return Switch(env, "switch")


@pytest.fixture(params=[
    "single message",
    "single message where destination is list",
    "2 messages",
    "8 messages",
    "3 batches of 2 messages",
])
def player(request, env, recorder, link):
    from ft4fttsim.networking import MessagePlaybackDevice, Message
    player = MessagePlaybackDevice(env, "player")
    player.connect_outlink(link)
    if request.param == "single message":
        messages = [Message(env, player, recorder, 1518, "message")]
        player.load_transmission_commands(
            {
                0: {link: messages}
            }
        )
        player.messages_to_transmit = messages
    elif request.param == "single message where destination is list":
        messages = [Message(env, player, [recorder], 158, "message")]
        player.load_transmission_commands(
            {
                0: {link: messages}
            }
        )
        player.messages_to_transmit = messages
    elif request.param == "2 messages":
        message_lists = [
            [Message(env, player, recorder, 1200, "message0")],
            [Message(env, player, recorder, 1000, "message1")],
        ]
        player.load_transmission_commands(
            {
                0: {link: message_lists[0]},
                1: {link: message_lists[1]},
            }
        )
        player.messages_to_transmit = [message for message_list in
            message_lists for message in message_list]
    elif request.param == "8 messages":
        message_lists = [
            [Message(env, player, recorder, 1200, "message0")],
            [Message(env, player, recorder, 1000, "message1")],
            [Message(env, player, recorder, 958, "message2")],
            [Message(env, player, recorder, 958, "message3")],
            [Message(env, player, recorder, 1508, "message4")],
            [Message(env, player, recorder, 90, "message5")],
            [Message(env, player, recorder, 1111, "message6")],
            [Message(env, player, recorder, 1234, "message7")],
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
    elif request.param == "3 batches of 2 messages":
        message_lists = [
            [Message(env, player, recorder, 142, "batch0 message0"),
                Message(env, player, recorder, 1000, "batch0 message1")],
            [Message(env, player, recorder, 218, "batch1 message0"),
                Message(env, player, recorder, 1050, "batch1 message1")],
            [Message(env, player, recorder, 1381, "batch2 message0"),
                Message(env, player, recorder, 150, "batch2 message1")],
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
