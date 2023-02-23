import atexit
import json
import time

import paho.mqtt.client as mqtt
import requests
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, request

from sending_config import *

info = 'Filtered data'
print(info)
apps_names = ['Negro Players', 'Geo Data', 'Uber pickups', 'Taxi log', 'Presidental Races Result']
segregated_data = {'Negro Players': [], 'Geo Data': [], 'Uber pickups': [], 'Taxi log': [],
                   'Presidental Races Result': []}
filtered_data = {'Names': [], 'Nicks': [], 'Geo locations': []}
filters = {'Names': 'False', 'Nicks': 'False', 'Geo locations': 'False'}


def collect_mqtt(collect_method):
    if collect_method == 'MQTT':
        def on_message(client, userdata, message):
            message = json.loads(str(message.payload.decode("utf-8")))
            segregated_data.get(message['Apk_name']).append(message['Data'])
            # print(message)

        client = mqtt.Client('TEST_Aggregator')
        client.on_message = on_message
        client.connect('test.mosquitto.org')
        client.subscribe(broker_topic)
        client.loop_start()
        time.sleep(4)
        client.loop_stop()


def data_collect_filter(filters):
    temp = {'Names': [], 'Nicks': [], 'Geo locations': []}
    if filters['Names'] == 'True':
        if len(segregated_data.get('Negro Players')) != 0:
            temp['Names'].append(list(segregated_data.get('Negro Players').pop(0).values()))
        if len(segregated_data.get('Presidental Races Result')) != 0:
            temp['Names'].append(list(segregated_data.get('Presidental Races Result').pop(0).values()))

    if filters['Nicks'] == 'True':
        if len(segregated_data.get('Negro Players')) != 0:
            temp['Nicks'].append(list(segregated_data.get('Negro Players').pop(0).keys()))

    if filters['Geo locations'] == 'True':
        if len(segregated_data.get('Geo Data')) != 0:
            temp['Geo locations'].append(list(segregated_data.get('Geo Data').pop(0).values()))
        if len(segregated_data.get('Taxi log')) != 0:
            temp['Geo locations'].append(list(segregated_data.get('Taxi log').pop(0).values()))

    return temp


def send_data(method, topic, filters):
    if method == 'HTTP':
        r1 = requests.post(URL_server_send, json=data_collect_filter(filters))
        print('message sent http')
    if method == 'MQTT':
        client = mqtt.Client('TEST_Aggr_send')
        client.connect(broker_URL)
        client.loop_start()
        client.publish(str(topic), json.dumps(data_collect_filter(filters)))
        print('message sent mqtt')
        client.loop_stop()


app = Flask(__name__)
app.secret_key = "super secret key"
config = {'Sending Method': sending_method,
          'Sleep Time': str(sleep_time),
          'URL_server': URL_server_send,
          'broker_URL': broker_URL,
          'broker_topic': broker_topic,
          'broker_topic_send': broker_topic_send,
          'Apk_URL': 'http://127.0.0.1:5012',
          'state': state,
          'Apk_name': 'Filter',
          'Collecting Method': collecting_method,
          'Current Datasets': 0,
          'filters': filters}


@app.route('/collect', methods=['POST'])
def collectData():
    if config['Collecting Method'] == 'HTTP':
        segregated_data.get(request.json['Apk_name']).append(request.json['Data'])

    return 'Uploaded', 202


@app.route('/', methods=('GET', 'POST'))
def modify():
    scheduler.reschedule_job(trigger='interval',
                             seconds=request.json['Sleep Time'], job_id='8')
    filters['Names'] = request.json['filters']['Names']
    filters['Geo locations'] = request.json['filters']['Geo locations']
    filters['Nicks'] = request.json['filters']['Nicks']

    config['Sending Method'] = request.json['Sending Method']
    config['Collecting Method'] = request.json['Collecting Method']
    config['Current Datasets'] = request.json['Current Datasets']
    config['broker_topic_send'] = request.json['Where_send']
    config['URL_server'] = request.json['Where_send']

    scheduler.modify_job(job_id='8',
                         args=[request.json['Sending Method'], request.json['Where_send'], request.json['filters']])
    scheduler.modify_job(job_id='11', args=[request.json['Collecting Method']])
    scheduler.reschedule_job(trigger='interval',
                             seconds=request.json['Sleep Time'], job_id='11')

    return 'Modified', 201


@app.route('/mqtt', methods=['POST'])
def handle_mqtt():
    scheduler.pause_job(job_id='11')

    return 'Modified', 201


if __name__ == "__main__":
    scheduler = BackgroundScheduler()
    scheduler.add_job(id='8', func=send_data, args=[sending_method, broker_topic_send, filters],
                      trigger='interval', seconds=sleep_time)
    scheduler.add_job(id='11', func=collect_mqtt, trigger='interval', seconds=5, args=[collecting_method])
    scheduler.start()
    # scheduler.pause_job(job_id='8')
    # scheduler.pause_job(job_id='11')
    requests.post(URL_Manager + 'register', json=config)

    app.run(port=5012)


def exit_handler():
    requests.post(URL_Manager + 'end', json=config)


atexit.register(exit_handler)
