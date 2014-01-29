import logging
import lagr.client
from lagr.server import plugins

logger = logging.getLogger(__name__)

logger.setLevel(logging.DEBUG)
handler = lagr.client.LagrHandler(application='Test app', host='localhost:8080', proto='http', url='lagr/api/v1/', level=logging.DEBUG)
logger.addHandler(handler)


alert = plugins.HideBelowThreshold(plugins=[plugins.HipChatAlert(room='python-temp')])

logger.info('Hello, World', extra={'trigger': [alert,]})
logger.debug('Hello, %s', 'Fucker')


