import atexit
import json
from math import e

import paho.mqtt.client as mqtt
import requests
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, request

from sending_config import *

info = 'Heater'

broker_topic = 'Heater'

config = {'Sending Method': sending_method,
          'Sleep Time': str(sleep_time),
          'URL_server': URL_server,
          'broker_URL': broker_URL,
          'broker_topic': broker_topic,
          'Apk_URL': 'http://127.0.0.1:5015',
          'state': state,
          'is_on': 'OFF',
          'Apk_name': 'Heater'}
print(info)
heater_temperature = [0]
k = 0.05
TemperatureSurround = 0
power = 1000


def Heater_temperature(TemperatureObject, state, power):
    if state == 'ON':
        heating_rate = 2.1 / 1000 * int(power)
        TemperatureObject.append(TemperatureObject[-1] + heating_rate)
        print(TemperatureObject[-1], state)
    if state == 'OFF':
        exact = (TemperatureObject[-1] - TemperatureSurround) * pow(e, -k) + TemperatureSurround
        TemperatureObject.append(exact)
        print(TemperatureObject[-1], state)


def send_data():
    client = mqtt.Client('Heater-temp')
    client.connect(broker_URL)
    client.loop_start()
    client.publish(broker_topic, json.dumps({'Data': heater_temperature[-1]}))
    print('message sent mqtt')
    client.loop_stop()


app = Flask(__name__)
app.secret_key = "super secret key"


@app.route('/', methods=['POST'])
def modify():
    scheduler.reschedule_job(trigger='interval',
                             seconds=request.json['Sleep Time'], job_id='15')
    scheduler.reschedule_job(trigger='interval',
                             seconds=request.json['Sleep Time'], job_id='16')
    scheduler.modify_job(job_id='16', args=[heater_temperature, config['is_on'], request.json['power']])

    return 'Modified', 201


@app.route('/change_status', methods=['POST'])
def change_status():
    scheduler.modify_job(job_id='16', args=[heater_temperature, request.json['state'], power])
    config['is_on'] = request.json['state']

    return 'Modified', 201


if __name__ == "__main__":
    scheduler = BackgroundScheduler()
    scheduler.add_job(id='15', func=send_data, trigger='interval', seconds=sleep_time)
    scheduler.add_job(id='16', func=Heater_temperature, args=[heater_temperature, state, power], trigger='interval',
                      seconds=sleep_time)

    scheduler.start()
    scheduler.pause_job(job_id='15')
    scheduler.pause_job(job_id='16')
    requests.post(URL_Manager + 'register', json=config)
    app.run(port=5015)


def exit_handler():
    requests.post(URL_Manager + 'end', json=config)


atexit.register(exit_handler)
