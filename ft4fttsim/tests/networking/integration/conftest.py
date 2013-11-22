# author: David Gessner <davidges@gmail.com>

import pytest


@pytest.fixture
def recorder1(env):
    from ft4fttsim.networking import MessageRecordingDevice
    recorder = MessageRecordingDevice(env, "recorder", 1)
    return recorder


@pytest.fixture
def recorder2(env):
    from ft4fttsim.networking import MessageRecordingDevice
    recorder = MessageRecordingDevice(env, "recorder2", 1)
    return recorder


@pytest.fixture
def recorder3(env):
    from ft4fttsim.networking import MessageRecordingDevice
    recorder = MessageRecordingDevice(env, "recorder3", 1)
    return recorder
