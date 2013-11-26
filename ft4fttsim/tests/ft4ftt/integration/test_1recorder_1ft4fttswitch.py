# author: David Gessner <davidges@gmail.com>
"""
Perform tests under the following network:

  +----------+     +---------------+
  | recorder 0 --- 0 FT4FTT switch |
  +----------+     |               |
                   |  +---0----+   |
                   |  | master |   |
                   |  +--------+   |
                   +---------------+

"""

import pytest

from ft4fttsim.ft4ftt import Link, FT4FTTSwitch


@pytest.fixture
def switch(env, master, recorder):
    new_switch = FT4FTTSwitch(env, "FT4FTT switch", 1, master)
    Link(env, recorder.ports[0], new_switch.ports[0], 100, 5)
    return new_switch


@pytest.mark.parametrize("num_ecs", range(1, 4))
def test_num_ecs_simulated__record_correct_number_of_messages(
        env, switch, recorder, num_ecs):
    """
    Test that the recorder records master.num_tms_per_ec trigger messages in
    each elementary cycle.

    """
    env.run(until=num_ecs * switch.master.ec_duration_us)
    received_messages = recorder.recorded_messages
    assert len(received_messages) == num_ecs * switch.master.num_tms_per_ec
