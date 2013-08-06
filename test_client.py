import logging
import lagr.client

logger = logging.getLogger(__name__)

logger.setLevel(logging.DEBUG)
logger.addHandler(lagr.client.LagrHandler(logging.DEBUG))

print "FOO"
logger.info('Hello, World')
logger.debug('Hello, %s', 'Fucker')
print "BAR"

