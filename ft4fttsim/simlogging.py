# author: David Gessner <davidges@gmail.com>

import simpy
import logging


# Instance of simpy.Environment to use to timestamp logging entries.
# Code using this module should set a value for this.
env = None


class SimLoggerAdapter(logging.LoggerAdapter):
    def process(self, log_msg, kwargs):
        if env is not None:
            return "{:>8.2f}: {}".format(env.now, log_msg), kwargs
        else:
            return "{}".format(log_msg), kwargs

logging.basicConfig(level=logging.DEBUG,
    format="%(levelname)5s:%(filename)s:%(lineno)4d: %(message)s")

logger = logging.getLogger('ft4fttsim')
log = SimLoggerAdapter(logger, {})
