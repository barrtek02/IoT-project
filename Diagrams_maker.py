import io
import json
import time

import matplotlib.pyplot as plt
import paho.mqtt.client as mqtt
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, request, send_file, jsonify

from sending_config import *

info = 'Diagrams maker'
print(info)
apps_names = ['Negro Players', 'Geo Data', 'Uber pickups', 'Taxi log', 'Presidental Races Result']
segregated_data = {'Negro Players': [], 'Geo Data': [], 'Uber pickups': [], 'Taxi log': [],
                   'Presidental Races Result': []}


def collect_mqtt():
    def on_message(client, userdata, message):
        message = json.loads(str(message.payload.decode("utf-8")))
        segregated_data.get(message['Apk_name']).append(message['Data'])
        # print(message)

    client = mqtt.Client('TEST_Aggregator')
    client.on_message = on_message
    client.connect('test.mosquitto.org')
    client.subscribe(broker_topic)
    client.loop_start()
    time.sleep(5)
    client.loop_stop()


def data_collect():
    data = []
    if len(segregated_data.get('Negro Players')) != 0:
        data.append(segregated_data.get('Negro Players').pop(0))
    if len(segregated_data.get('Geo Data')) != 0:
        data.append(segregated_data.get('Geo Data').pop(0))
    if len(segregated_data.get('Uber pickups')) != 0:
        data.append(segregated_data.get('Uber pickups').pop(0))
    if len(segregated_data.get('Taxi log')) != 0:
        data.append(segregated_data.get('Taxi log').pop(0))
    if len(segregated_data.get('Presidental Races Result')) != 0:
        data.append(segregated_data.get('Presidental Races Result').pop(0))
    return data


app = Flask(__name__)
app.secret_key = "super secret key"
config = {'Sending Method': sending_method,
          'Sleep Time': str(sleep_time),
          'URL_server': URL_server_send,
          'broker_URL': broker_URL,
          'broker_topic': broker_topic,
          'broker_topic_send': broker_topic_send,
          'Apk_URL': 'http://127.0.0.1:5011',
          'state': state,
          'Apk_name': 'Diagrams Maker',
          'Collecting Method': collecting_method,
          'Current Datasets': 0}


@app.route('/collect', methods=['POST'])
def collectData():
    segregated_data.get(request.json['Apk_name']).append(request.json['Data'])

    return 'Uploaded', 202


@app.route('/show', methods=['GET'])
def show():
    return jsonify(segregated_data), 202


geo_data_count = []
geo_data_numbers = []

taxi_data_count = []
taxi_data_numbers = []


@app.route('/diagram/<app_name>', methods=('GET', 'POST'))
def get_diagram(app_name):
    # generate the diagram
    if app_name == 'Negro Players':
        count_a = 0
        count_b = 0
        count_c = 0
        count_d = 0
        count_e = 0
        for name in segregated_data['Negro Players']:
            for key in name.keys():
                if key[0].lower() == 'a':
                    count_a += 1
                elif key[0].lower() == 'b':
                    count_b += 1
                elif key[0].lower() == 'c':
                    count_c += 1
                elif key[0].lower() == 'd':
                    count_d += 1
                elif key[0].lower() == 'e':
                    count_e += 1

        # Plot the results
        plt.bar(['A', 'B', 'C', 'D', 'E'], [count_a, count_b, count_c, count_d, count_e])
        plt.ylabel('How many')
        plt.title("Negro players nicks starting with ABCDE")
    elif app_name == 'Geo Data':
        if len(geo_data_count) == 0:
            geo_data_count.append(1)
        else:
            geo_data_count.append(geo_data_count[-1] + 1)
        geo_data_numbers.append(len(segregated_data['Geo Data']))
        plt.bar(geo_data_count, geo_data_numbers)
        plt.ylabel('How many')
        plt.xlabel('Current iteration')
        plt.title("Geo data number of measures")
    elif app_name == 'Uber pickups':
        plt.plot([1, 2, 3, 4])
        plt.ylabel('some numbers nr ' + app_name)
    elif app_name == 'Taxi log':
        if len(taxi_data_count) == 0:
            taxi_data_count.append(1)
        else:
            taxi_data_count.append(taxi_data_count[-1] + 1)
        taxi_data_numbers.append(len(segregated_data['Taxi log']))
        plt.bar(taxi_data_count, taxi_data_numbers)
        plt.ylabel('How many')
        plt.xlabel('Current iteration')
        plt.title("Taxi log data number of measures")
    elif app_name == 'Presidental Races Result':
        p_keys = {}
        for data in segregated_data['Presidental Races Result']:
            for key in data.keys():
                if key not in p_keys:
                    p_keys[key] = 1
                else:
                    p_keys[key] += 1
        plt.bar(p_keys.keys(), p_keys.values())
        plt.ylabel('How many')
        plt.xlabel('Year')
        plt.title("How many measuers of year")

    # save the diagram to a buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)

    # return the diagram as a response
    return send_file(buf, mimetype='image/png')


if __name__ == "__main__":
    scheduler = BackgroundScheduler()
    scheduler.add_job(id='26', func=collect_mqtt, trigger='interval', seconds=5)
    scheduler.start()

    app.run(port=5025)
