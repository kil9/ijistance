# -*- encoding: utf-8 -*-

from flask import Flask
import pika

from config import *


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
    app.run(port=21000, debug=True)
