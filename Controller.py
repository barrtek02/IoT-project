import atexit
import json
import time

import paho.mqtt.client as mqtt
import requests
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, request

from sending_config import *

info = 'Controller'
print(info)
heater_temperature = [0, 0]
broker_topic = 'Heater'
URL_server_send = 'http://127.0.0.1:5015/change_status'


def collect_mqtt():
    def on_message(client, userdata, message):
        message = json.loads(str(message.payload.decode("utf-8")))
        heater_temperature.append(message['Data'])
        # print(message)

    client = mqtt.Client('controller')
    client.on_message = on_message
    client.connect('test.mosquitto.org')
    client.subscribe(broker_topic)
    client.loop_start()
    time.sleep(4)
    client.loop_stop()


def make_decision(heater_temperature, lower_limit, upper_limit):
    if heater_temperature[-1] < lower_limit and config['is_on'] != 'ON':
        print(heater_temperature[-1], 'out of range')
        requests.post(URL_server_send, json={'state': 'ON'})
        config['is_on'] = 'ON'
        print('state ON')

    elif heater_temperature[-1] > upper_limit and config['is_on'] != 'OFF':
        print(heater_temperature[-1], 'out of range')
        requests.post(URL_server_send, json={'state': 'OFF'})
        config['is_on'] = 'OFF'
        print('state OFF')

    else:
        if heater_temperature[-1] < lower_limit or heater_temperature[-1] > upper_limit:
            print(heater_temperature[-1], 'out of range')
        else:
            print(heater_temperature[-1], 'OK')


def check_temp():
    temp = 'Temperature out of range'
    if heater_temperature[-1] > config['lower_limit'] and heater_temperature[-1] < config['upper_limit']:
        temp = 'OK'
    else:
        pass

    return temp


app = Flask(__name__)
app.secret_key = "super secret key"
config = {'Sending Method': sending_method,
          'Sleep Time': str(sleep_time),
          'URL_server': URL_server_send,
          'broker_URL': broker_URL,
          'broker_topic': broker_topic,
          'broker_topic_send': broker_topic_send,
          'Apk_URL': 'http://127.0.0.1:5020',
          'state': state,
          'is_on': 'OFF',
          'Apk_name': 'Controller',
          'Collecting Method': collecting_method,
          'Current Datasets': 0,
          'upper_limit': 25,
          'lower_limit': 10,
          'power': 1000
          }


@app.route('/', methods=['POST'])
def modify():
    scheduler.reschedule_job(trigger='interval',
                             seconds=request.json['Sleep Time'], job_id='20')

    config['lower_limit'] = int(request.json['lower_limit'])
    config['upper_limit'] = int(request.json['upper_limit'])
    config['broker_topic_send'] = request.json['Where_send']

    scheduler.modify_job(job_id='20', args=[heater_temperature, config['lower_limit'], config['upper_limit']])

    return 'Modified', 201


@app.route('/', methods=['GET'])
def show_data():
    return str(heater_temperature[-1]) + '' + str(check_temp()), 201


if __name__ == "__main__":
    scheduler = BackgroundScheduler()
    scheduler.add_job(id='20', func=make_decision,
                      args=[heater_temperature, config['lower_limit'], config['upper_limit']], trigger='interval',
                      seconds=sleep_time)
    scheduler.add_job(id='21', func=collect_mqtt, trigger='interval', seconds=5)
    scheduler.start()
    scheduler.pause_job(job_id='20')
    requests.post(URL_Manager + 'register', json=config)

    app.run(port=5020)


def exit_handler():
    requests.post(URL_Manager + 'end', json=config)


atexit.register(exit_handler)
