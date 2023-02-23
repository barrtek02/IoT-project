import atexit
import json
import random

import paho.mqtt.client as mqtt
import requests
from apscheduler.schedulers.background import BackgroundScheduler
from dateutil import parser
from flask import Flask, request

from sending_config import *

info = 'Uber pickups'
print(info)


def uber_data():
    with open(source2, 'r') as f:
        data = f.readlines()
    return data


uber = uber_data()
dates = []
for i in range(1, len(uber)):
    dates.append(parser.parse(uber[i][1:9]))


def random_ubers():
    ubers = []
    date = random.choice(dates)
    for i in range(1, len(uber)):
        try:
            if date == parser.parse(uber[i][1:9]):
                if parser.parse('00:06:00') < parser.parse(uber[i][10:17]) < parser.parse('00:10:00'):
                    ubers.append(uber[i])
        except ValueError:
            pass
    return ubers


def send_data(method):
    if method == 'HTTP':
        r1 = requests.post(URL_server, json={'Apk_name': config.get('Apk_name'), 'Data': random_ubers()})
        print('message sent http')
    if method == 'MQTT':
        client = mqtt.Client('Election-Results')
        client.connect(broker_URL)
        client.loop_start()
        client.publish(broker_topic, json.dumps({'Apk_name': config.get('Apk_name'), 'Data': random_ubers()}))
        print('message sent mqtt')
        client.loop_stop()


app = Flask(__name__)
app.secret_key = "super secret key"
config = {'Sending Method': sending_method,
          'Sleep Time': str(sleep_time),
          'URL_server': URL_server,
          'broker_URL': broker_URL,
          'broker_topic': broker_topic,
          'Apk_URL': 'http://127.0.0.1:5002',
          'state': state,
          'Apk_name': 'Uber pickups'}


@app.route('/', methods=['POST'])
def modify():
    scheduler.reschedule_job(trigger='interval',
                             seconds=request.json['Sleep Time'], job_id='2')
    scheduler.modify_job(job_id='2', args=[request.json['Sending Method']])

    return 'Modified', 201


if __name__ == "__main__":
    scheduler = BackgroundScheduler()
    scheduler.add_job(id='2', func=send_data, args=[sending_method], trigger='interval', seconds=sleep_time)
    scheduler.start()
    scheduler.pause_job(job_id='2')
    requests.post(URL_Manager + 'register', json=config)

    app.run(port=5002)


def exit_handler():
    requests.post(URL_Manager + 'end', json=config)


atexit.register(exit_handler)
