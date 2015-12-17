# -*- encoding: utf-8 -*-

from flask import Flask
import pika

from config import *


app = Flask(__name__)

@app.route('/')
def main():
    log.info('i-jistance main page')
    return 'automatic report servie for i-jistance'

def enqueue_activate(message='ijistance_event'):
    log.debug('received event to publish: {}'.format(message))

    connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_TX_URL))
    channel = connection.channel()

    channel.queue_declare(queue=RABBITMQ_QUEUE)

    channel.basic_publish(exchange='', routing_key=RABBITMQ_QUEUE, body=message)

    connection.close()

    return 'published {}'.format(message)

@app.route('/activate')
def activate():
    log.info('i-jistance activated')
    try:
        msg = enqueue_activate()
    except e:
        msg = 'failed to enqueue i-jistance event'
        log.error(msg)
        return msg
    return msg


if __name__ == '__main__':
    app.run(port=21000, debug=True)
