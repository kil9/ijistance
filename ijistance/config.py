# -*- encoding: utf-8 -*-

import logging
import os
import sys

from logentries import LogentriesHandler


RABBITMQ_QUEUE = 'ijistance_jobqueue'

logentries_key = os.environ['LOGENTRIES_KEY']

USERS = ('kil9', 'totokki')

EGMOBILE_USERIDS = dict([(user, os.environ['EGMOBILE_USERID_' + user]) for user in USERS])
EGMOBILE_PASSWDS = dict([(user, os.environ['EGMOBILE_PASSWD_' + user]) for user in USERS])

NUMEROUS_AUTH_STRINGS = dict([(user, os.environ['NUMEROUS_AUTH_STRING_' + user]) for user in USERS])

RABBITMQ_RX_URL = os.environ['RABBITMQ_BIGWIG_RX_URL']
RABBITMQ_TX_URL = os.environ['RABBITMQ_BIGWIG_TX_URL']
#rabbitmq_url = os.environ['RABBITMQ_BIGWIG_URL']

LOG_FORMAT = '%(asctime)s [%(levelname)s] %(message)s'
logging.basicConfig(stream=sys.stdout, level=logging.INFO, format=LOG_FORMAT)
log = logging.getLogger(__name__)
log.addHandler(LogentriesHandler(logentries_key))


metric_map = {}
metric_map['kil9'] = {
        'paid_call':            '5497780356662936347',
        'current_data_charge':  '4514103156147167693',
        'free_call':            '6609814354450169229',
        'used_free_call':       '7065060043860950150',
        'remain_free_call':     '1090989293457867135',
        'current_total_charge': '6061124877899087878' }

metric_map['totokki'] = {
        'paid_call':            '3276876009954838618',
        'current_data_charge':  '1646276907762159272',
        'remain_free_call':     '9171948128073601887',
        'current_total_charge': '3239696783337913380' }
