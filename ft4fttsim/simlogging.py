# author: David Gessner <davidges@gmail.com>

import logging


# Instance of simpy.Environment to use to timestamp logging entries.
# Code using this module should set a value for this.
env = None  # pylint: disable-msg=C0103


class _SimLoggerAdapter(logging.LoggerAdapter):
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


_LOGGER = logging.getLogger('ft4fttsim')
log = _SimLoggerAdapter(_LOGGER, {})  # pylint: disable-msg=C0103
