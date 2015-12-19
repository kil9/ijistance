# -*- encoding: utf-8 -*-

import json
import re
import sys

from bs4 import BeautifulSoup
import pika
import requests

from config import *

def parse_metric(metric):
    log.debug(u'metric: {}'.format(metric))
    digits = re.sub('\D', '', metric)
    if 'KB' in metric:
        digits = digits[:-3]
    return digits if digits else 0

def update_numerous(report, user):

    metrics = metric_map[user]

    request_url_pattern = 'https://api.numerousapp.com/v2/metrics/{}/events'

    for key in metrics:
        request_url = request_url_pattern.format(metrics[key])

        headers = {'Authorization': NUMEROUS_AUTH_STRINGS[user],
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

def iji_callback(ch, method, properties, body):
    log.info(" [x] Received user: %r" % (body,))
    user = body

    LOGIN_URL = 'https://www.egmobile.co.kr/member/loginOK.php'
    BILL_URL = 'https://www.egmobile.co.kr/customer_center/bill_time.php'

    data = {'return_url': '/member/login.php?return_url=/',
            'userid': EGMOBILE_USERIDS[user],
            'passwd': EGMOBILE_PASSWDS[user],
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
    msg, is_ok = update_numerous(report, user)
    if not is_ok:
        log.error(msg)
        return msg
    msg = u'successfully activated. current total charge({}): {}'.format(user, report['current_total_charge'])
    log.info(msg)

def consume():
    connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_RX_URL))
    channel = connection.channel()
    channel.queue_declare(queue=RABBITMQ_QUEUE)

    channel.basic_consume(iji_callback, queue=RABBITMQ_QUEUE, no_ack=True)
    log.info(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()

    return 'consume finished'

if __name__ == '__main__':
    consume()
