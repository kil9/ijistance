# -*- encoding: utf-8 -*-

import json

from flask import Flask
import pika

from config import *
from ijiworker import iji_report


app = Flask(__name__)

@app.route('/')
def main():
    log.info('i-jistance main page')
    return 'automatic report servie for i-jistance'

def enqueue_activate(message):
    log.debug('received event to publish: {}'.format(message))

    connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_TX_URL))
    channel = connection.channel()

    channel.queue_declare(queue=RABBITMQ_QUEUE)

    channel.basic_publish(exchange='', routing_key=RABBITMQ_QUEUE, body=message)

    connection.close()

    return 'published {}'.format(message)

@app.route('/report/<user>')
def report(user):
    report = iji_report(user)
    return json.dumps(report)

@app.route('/numeric/<user>')
def numeric(user):
    raw_report = iji_report(user)
    used_free_call = int(''.join(filter(unicode.isdigit, raw_report['used_free_call'])))
    payload = {
                'postfix': 'KB',
                'data': { 'value': used_free_call }
              }
    return json.dumps(payload)

@app.route('/activate/<user>')
def activate(user):
    log.info('i-jistance activated')
    if user not in USERS:
        msg = 'not a registered user: {}'.format(user)
        log.error(msg)
        return msg
    try:
        msg = enqueue_activate(user)
    except e:
        msg = 'failed to enqueue i-jistance event'
        log.error(msg)
        return msg
    return msg


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=21002, debug=True)
