# -*- encoding: utf-8 -*-

import logging
import os
import sys

from logentries import LogentriesHandler


logentries_key = os.environ['LOGENTRIES_KEY']

egmobile_userid = os.environ['EGMOBILE_USERID']
egmobile_passwd = os.environ['EGMOBILE_PASSWD']

numerous_auth_string = os.environ['NUMEROUS_AUTH_STRING']

LOG_FORMAT = '%(asctime)s [%(levelname)s] %(message)s'
logging.basicConfig(stream=sys.stdout, level=logging.INFO, format=LOG_FORMAT)
log = logging.getLogger(__name__)
log.addHandler(LogentriesHandler(logentries_key))
