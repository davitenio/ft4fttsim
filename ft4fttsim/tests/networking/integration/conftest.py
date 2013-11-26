# author: David Gessner <davidges@gmail.com>

import pytest

from ft4fttsim.networking import MessageRecordingDevice
from ft4fttsim.tests.networking.fixturehelper import make_playback_device
from ft4fttsim.tests.networking.fixturehelper import PLAYBACK_CONFIGS


@pytest.fixture
def recorder1(env):
    recorder = MessageRecordingDevice(env, "recorder", 1)
    return recorder


@pytest.fixture
def recorder2(env):
    recorder = MessageRecordingDevice(env, "recorder2", 1)
    return recorder


@pytest.fixture
def recorder3(env):
    recorder = MessageRecordingDevice(env, "recorder3", 1)
    return recorder


@pytest.fixture(params=PLAYBACK_CONFIGS)
def player_rec1(request, env, recorder1):
    """
    Create a message playback device that sends messages to recorder 1 only.

    """
    config = request.param
    new_playback_device = make_playback_device(
        config, env, recorder1)
    return new_playback_device


@pytest.fixture(params=PLAYBACK_CONFIGS)
def player_rec2(request, env, recorder2):
    """
    Create a message playback device that sends messages to recorder 2 only.

    """
    config = request.param
    new_playback_device = make_playback_device(
        config, env, recorder2)
    return new_playback_device


@pytest.fixture(params=PLAYBACK_CONFIGS)
def player_rec12(request, env, recorder1, recorder2):
    """
    Create a player sending messages to recorder 1 and 2.

    """
    config = request.param
    new_playback_device = make_playback_device(
        config, env, [recorder1, recorder2])
    return new_playback_device


@pytest.fixture(params=PLAYBACK_CONFIGS)
def player_rec13(request, env, recorder1, recorder3):
    """
    Create a message playback device that sends messages to recorder 1 and 3.

    """
    config = request.param
    new_playback_device = make_playback_device(
        config, env, [recorder1, recorder3])
    return new_playback_device


@pytest.fixture(params=PLAYBACK_CONFIGS)
def player2_rec1(request, env, recorder1):
    """
    Second message playback device that sends messages to recorder 1 only.

    """
    config = request.param
    new_playback_device = make_playback_device(
        config, env, recorder1, name="player2")
    return new_playback_device


@pytest.fixture(params=PLAYBACK_CONFIGS)
def player2_rec2(request, env, recorder2):
    """
    Second message playback device that sends messages to recorder 2 only.

    """
    config = request.param
    new_playback_device = make_playback_device(
        config, env, recorder2, name="player2")
    return new_playback_device
