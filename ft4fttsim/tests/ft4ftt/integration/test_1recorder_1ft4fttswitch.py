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


@pytest.mark.parametrize("num_ECs", range(1, 4))
def test_num_ECs_simulated__record_correct_number_of_messages(
        env, switch, recorder, num_ECs):
    """
    Test that the recorder records master.num_TMs_per_EC trigger messages in
    each elementary cycle.

    """
    env.run(until=num_ECs * switch.master.EC_duration_us)
    received_messages = recorder.recorded_messages
    assert len(received_messages) == num_ECs * switch.master.num_TMs_per_EC
