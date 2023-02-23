import atexit
import json
import random

import paho.mqtt.client as mqtt
import requests
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, request

from sending_config import *

info = 'Presidental Races results'
print(info)


def winning_names(source):
    r2 = requests.get(source)
    data = r2.text.splitlines()
    names = []
    cycles = []
    for i in range(1, len(data)):
        if int(data[i].rsplit(',')[7]) not in cycles:
            cycles.append(int(data[i].rsplit(',')[7]))
    cycle = random.choice(cycles)
    for i in range(1, len(data)):
        if int(data[i].rsplit(',')[7]) == cycle:
            names.append(data[i].rsplit(',')[13])
        if len(names) > 4:
            break
    dictionary = {cycle: names}
    return dictionary


def send_data(method):
    if method == 'HTTP':
        r1 = requests.post(URL_server, json={'Apk_name': config.get('Apk_name'), 'Data': winning_names(source3)})
        print('message sent http')
    if method == 'MQTT':
        client = mqtt.Client('Election-Results')
        client.connect(broker_URL)
        client.loop_start()
        client.publish(broker_topic, json.dumps({'Apk_name': config.get('Apk_name'), 'Data': winning_names(source3)}))
        print('message sent mqtt')
        client.loop_stop()


app = Flask(__name__)
app.secret_key = "super secret key"
config = {'Sending Method': sending_method,
          'Sleep Time': str(sleep_time),
          'URL_server': URL_server,
          'broker_URL': broker_URL,
          'broker_topic': broker_topic,
          'Apk_URL': 'http://127.0.0.1:5003',
          'state': state,
          'Apk_name': 'Presidental Races Result'}


@app.route('/', methods=['POST'])
def modify():
    scheduler.reschedule_job(trigger='interval',
                             seconds=request.json['Sleep Time'], job_id='3')
    scheduler.modify_job(job_id='3', args=[request.json['Sending Method']])

    return 'Modified', 201


if __name__ == "__main__":
    scheduler = BackgroundScheduler()
    scheduler.add_job(id='3', func=send_data, args=[sending_method], trigger='interval', seconds=sleep_time)
    scheduler.start()
    scheduler.pause_job(job_id='3')
    requests.post(URL_Manager + 'register', json=config)

    app.run(port=5003)


def exit_handler():
    requests.post(URL_Manager + 'end', json=config)


atexit.register(exit_handler)
