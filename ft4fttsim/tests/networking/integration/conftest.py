# author: David Gessner <davidges@gmail.com>

import pytest


@pytest.fixture
def recorder(env):
    from ft4fttsim.networking import MessageRecordingDevice
    recorder = MessageRecordingDevice(env, "recorder", 1)
    return recorder
