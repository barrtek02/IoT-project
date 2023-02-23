import atexit
import json
import random

import paho.mqtt.client as mqtt
import requests
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, request

from sending_config import *

info = 'taxi log'
print(info)


def taxi_data():
    number = str(random.randint(1, 10357))
    taxi_dict = {}
    with open(source4 + number + '.txt', 'r') as f:
        for i in range(1, 5):
            f.seek(0)
            taxi_dict[i] = f.readlines()[i][0:-2]
    return taxi_dict


def send_data(method):
    if method == 'HTTP':
        r1 = requests.post(URL_server, json={'Apk_name': config.get('Apk_name'), 'Data': taxi_data()})
        print('message sent http')
    if method == 'MQTT':
        client = mqtt.Client('Election-Results')
        client.connect(broker_URL)
        client.loop_start()
        client.publish(broker_topic, json.dumps({'Apk_name': config.get('Apk_name'), 'Data': taxi_data()}))
        print('message sent mqtt')
        client.loop_stop()


app = Flask(__name__)
app.secret_key = "super secret key"
config = {'Sending Method': sending_method,
          'Sleep Time': str(sleep_time),
          'URL_server': URL_server,
          'broker_URL': broker_URL,
          'broker_topic': broker_topic,
          'Apk_URL': 'http://127.0.0.1:5004',
          'state': state,
          'Apk_name': 'Taxi log'}


@app.route('/', methods=['POST'])
def modify():
    scheduler.reschedule_job(trigger='interval',
                             seconds=request.json['Sleep Time'], job_id='4')
    scheduler.modify_job(job_id='4', args=[request.json['Sending Method']])

    return 'Modified', 201


if __name__ == "__main__":
    scheduler = BackgroundScheduler()
    scheduler.add_job(id='4', func=send_data, args=[sending_method], trigger='interval', seconds=sleep_time)
    scheduler.start()
    scheduler.pause_job(job_id='4')
    requests.post(URL_Manager + 'register', json=config)

    app.run(port=5004)


def exit_handler():
    requests.post(URL_Manager + 'end', json=config)


atexit.register(exit_handler)
