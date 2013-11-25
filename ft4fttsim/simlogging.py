# author: David Gessner <davidges@gmail.com>
"""
This module allows to print log messages timestamped with the simulated time.

The format of the log messages is the following:

LOGLEVEL:FILENAME:LINENUMBER:SIMULATEDTIME:LOGMESSAGE

Example:

>>> import simpy
>>> import ft4fttsim.simlogging
>>> import sys
>>> # The following line is to redirect stderr to stdout in this doctest.
>>> sys.stderr.write = sys.stdout.write
>>> env = simpy.Environment()
>>> # Register the simulation environment with the logger.
>>> ft4fttsim.simlogging.env = env
>>> def hello(env):
...     ft4fttsim.simlogging.log.debug("hello started")
...     print("Hello ", end="")
...     yield env.timeout(1234)
...     print("World!")
...     ft4fttsim.simlogging.log.debug("hello finished")
...
>>> hello_process = hello(env)
>>> env.process(hello_process)
<Process(hello) object at 0x...>
>>> env.run(until=10000)
DEBUG:<doctest ft4fttsim.simlogging[6]>:    2:     0.00: hello started
Hello World!
DEBUG:<doctest ft4fttsim.simlogging[6]>:    6:  1234.00: hello finished

"""

import logging


# Instance of simpy.Environment to use to timestamp logging entries.
# Code using this module should set a value for this.
env = None  # pylint: disable-msg=C0103


class SimLoggerAdapter(logging.LoggerAdapter):
    """
    Class used to prefix the simulated time to the logging entries.

    """

    def process(self, log_msg, kwargs):
        if env is not None:
            return "{:>8.2f}: {}".format(env.now, log_msg), kwargs
        else:
            return "{}".format(log_msg), kwargs


logging.basicConfig(
    level=logging.DEBUG,
    format="%(levelname)5s:%(filename)15s:%(lineno)5d: %(message)s")


LOGGER = logging.getLogger('ft4fttsim')
log = SimLoggerAdapter(LOGGER, {})  # pylint: disable-msg=C0103
