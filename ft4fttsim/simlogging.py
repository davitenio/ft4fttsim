# author: David Gessner <davidges@gmail.com>

from SimPy.Simulation import now
import logging


class SimLoggerAdapter(logging.LoggerAdapter):
    def process(self, log_msg, kwargs):
        return "{:>8.2f}: {:s}".format(now(), log_msg), kwargs

logging.basicConfig(level=logging.DEBUG, format="%(levelname)5s %(message)s")

log = SimLoggerAdapter(logging.getLogger('ft4fttsim'), {})
