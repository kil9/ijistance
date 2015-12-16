# -*- encoding: utf-8 -*-

import json
import logging
import os
import re
import sys

from bs4 import BeautifulSoup
from flask import Flask
import requests


LOG_FORMAT = '%(asctime)s [%(levelname)s] %(message)s'
logging.basicConfig(stream=sys.stdout, level=logging.INFO, format=LOG_FORMAT)
log = logging.getLogger(__name__)

app = Flask(__name__)

egmobile_userid = os.environ['EGMOBILE_USERID']
egmobile_passwd = os.environ['EGMOBILE_PASSWD']

numerous_auth_string = os.environ['NUMEROUS_AUTH_STRING']

@app.route('/')
def main():
    log.info('main called')
    return 'automatic report servie for i-jistance'

@app.route('/activate')
def activate():
    log.info('activate called')

    LOGIN_URL = 'https://www.egmobile.co.kr/member/loginOK.php'
    BILL_URL = 'https://www.egmobile.co.kr/customer_center/bill_time.php'

    data = {'return_url': '/member/login.php?return_url=/',
            'userid': egmobile_userid,
            'passwd': egmobile_passwd,
            'mode': 'login' }

    resp = requests.post(LOGIN_URL, data=data)
    if (resp.status_code != 200):
        log.error('failed to sign in')
        return 'failed to sign in'

    cookies = resp.cookies # PHPSESSID is required

    resp = requests.get(BILL_URL, cookies=cookies)
    if (resp.status_code != 200):
        log.error('failed to get bill page')
        return 'failed to get bill page'

    report = parse_ijireport(resp.text)
    msg, is_ok = update_numerous(report)
    if not is_ok:
        log.error(msg)
        return msg
    return u'activated. current total charge: {}'.format(report['current_total_charge'])

def parse_metric(metric):
    log.debug(u'metric: {}'.format(metric))
    digits = re.sub('\D', '', metric)
    if 'KB' in metric:
        digits = digits[:-3]
    return digits if digits else 0

def update_numerous(report):
    keys = { 'paid_call':            '5497780356662936347',
             'current_data_charge':  '4514103156147167693',
             'free_call':            '6609814354450169229',
             'used_free_call':       '7065060043860950150',
             'remain_free_call':     '1090989293457867135',
             'current_total_charge': '6061124877899087878' }

    request_url_pattern = 'https://api.numerousapp.com/v2/metrics/{}/events'

    for key in report:
        request_url = request_url_pattern.format(keys[key])

        headers = {'Authorization': numerous_auth_string,
                   'Content-Type': 'application/json'}
        payload = {'Value': parse_metric(report[key]) }
        data = json.dumps(payload)

        resp = requests.post(request_url, headers=headers, data=data)
        if resp.status_code not in (200, 201):
            msg = 'failed to update metric'
            log.error(msg)
            return msg, False

    return 'ok', True

def parse_ijireport(markup):
    soup = BeautifulSoup(markup, "html.parser")
    center_table = soup.find('table', class_='centerTb')
    data = center_table.find('td', string='데이터')

    # 통화항목, 총통화, 과금대상통화, 과금대상금액, 당월무료, 이월무료, 총무료통화, 사용무료통화, 남은무료통화
    data_set = data.parent.find_all('td')

    log.debug(u'과금통화: {}'.format(data_set[2].text))
    log.debug(u'과금금액: {}'.format(data_set[3].text))
    log.debug(u'무료통화: {}'.format(data_set[6].text))
    log.debug(u'사용무료통화: {}'.format(data_set[7].text))
    log.debug(u'남은무료통화: {}'.format(data_set[8].text))

    total_charge = soup.find_all(string='당월요금계')[0].find_next('td')

    log.debug(u'전체 요금: {}'.format(total_charge.text))

    report = { 'paid_call': data_set[2].text,
               'current_data_charge': data_set[3].text,
               'free_call': data_set[6].text,
               'used_free_call': data_set[7].text,
               'remain_free_call': data_set[8].text,
               'current_total_charge': total_charge.text }

    return report

if __name__ == '__main__':
    app.run(port=21000, debug=True)
