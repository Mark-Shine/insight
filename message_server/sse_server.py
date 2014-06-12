#!/usr/bin/env python

# import gevent
# import gevent.monkey
from gevent.pywsgi import WSGIServer
import pika


connection = pika.BlockingConnection(pika.ConnectionParameters(
        host='127.0.0.1'))
channel = connection.channel()

# gevent.monkey.patch_all()

from flask import Flask, request, Response, render_template

app = Flask(__name__)
messages = []

# def event_stream():
#     count = 0
#     while True:
#         gevent.sleep(2)
#         yield 'data: %s\n\n' % count
#         count += 1

def rec():
    channel.queue_declare(queue='hello')
    def callback(ch, method, properties, body):
        messages.append(body)
        print "here"
        print body

    channel.basic_consume(callback,
                          queue='hello',
                          no_ack=True)
    channel.start_consuming()


@app.route('/alert', methods=['GET', 'POST'])
def sse_request():
    info =''
    print messages
    if messages:
        info = messages.pop()
        print info
    return Response(
        info,mimetype='text/event-stream')

@app.route('/')
def page():
    return render_template('sse.html')

if __name__ == '__main__':
    app.debug = True
    http_server = WSGIServer(('127.0.0.1', 8001), app)
    http_server.serve_forever()
