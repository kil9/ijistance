# -*- encoding: utf-8 -*-

import logging
import os
import sys

from logentries import LogentriesHandler


RABBITMQ_QUEUE = 'ijistance_jobqueue'

logentries_key = os.environ['LOGENTRIES_KEY']

EGMOBILE_USERID = os.environ['EGMOBILE_USERID']
EGMOBILE_PASSWD = os.environ['EGMOBILE_PASSWD']

NUMEROUS_AUTH_STRING = os.environ['NUMEROUS_AUTH_STRING']

RABBITMQ_RX_URL = os.environ['RABBITMQ_BIGWIG_RX_URL']
RABBITMQ_TX_URL = os.environ['RABBITMQ_BIGWIG_TX_URL']
#rabbitmq_url = os.environ['RABBITMQ_BIGWIG_URL']

LOG_FORMAT = '%(asctime)s [%(levelname)s] %(message)s'
logging.basicConfig(stream=sys.stdout, level=logging.INFO, format=LOG_FORMAT)
log = logging.getLogger(__name__)
log.addHandler(LogentriesHandler(logentries_key))
