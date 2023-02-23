import atexit
import json

import paho.mqtt.client as mqtt
import requests
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, request

from sending_config import *

info = 'Geo data'
print(info)


def geo_data(i):
    geo_dict = {}
    with open(source1, 'r') as f:
        geo_dict[i - 2] = f.readlines()[i + 5]
    return geo_dict


def send_data(method):
    send_data.counter += 1
    i = send_data.counter
    if method == 'HTTP':
        r1 = requests.post(URL_server, json={'Apk_name': config.get('Apk_name'), 'Data': geo_data(i)})
        print('message sent http')
    if method == 'MQTT':
        client = mqtt.Client('Election-Results')
        client.connect(broker_URL)
        client.loop_start()
        client.publish(broker_topic, json.dumps({'Apk_name': config.get('Apk_name'), 'Data': geo_data(i)}))
        print('message sent mqtt')
        client.loop_stop()


send_data.counter = 0

app = Flask(__name__)
app.secret_key = "super secret key"
config = {'Sending Method': sending_method,
          'Sleep Time': str(sleep_time),
          'URL_server': URL_server,
          'broker_URL': broker_URL,
          'broker_topic': broker_topic,
          'Apk_URL': 'http://127.0.0.1:5001',
          'state': state,
          'Apk_name': 'Geo Data'}


@app.route('/', methods=['POST'])
def modify():
    scheduler.reschedule_job(trigger='interval',
                             seconds=request.json['Sleep Time'], job_id='1')
    scheduler.modify_job(job_id='1', args=[request.json['Sending Method']])

    return 'Modified', 201


if __name__ == "__main__":
    scheduler = BackgroundScheduler()
    scheduler.add_job(id='1', func=send_data, args=[sending_method], trigger='interval', seconds=sleep_time)
    scheduler.start()
    scheduler.pause_job(job_id='1')
    requests.post(URL_Manager + 'register', json=config)

    app.run(port=5001)


def exit_handler():
    requests.post(URL_Manager + 'end', json=config)


atexit.register(exit_handler)
