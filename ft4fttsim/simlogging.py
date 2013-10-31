# author: David Gessner <davidges@gmail.com>

from SimPy.Simulation import now
import logging


class SimLoggerAdapter(logging.LoggerAdapter):
    def process(self, log_msg, kwargs):
        return "{:>8.2f}: {}".format(now(), log_msg), kwargs

logging.basicConfig(level=logging.DEBUG,
    format="%(levelname)5s:%(filename)s:%(lineno)4d: %(message)s")

logger = logging.getLogger('ft4fttsim')
# By default we prevent the logger from printing anything. If you need to see
# the logging output, set simlogging.logger.propagate = True within the file
# that imports the simlogging module.
logger.propagate = False
log = SimLoggerAdapter(logger, {})
