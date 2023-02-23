import atexit
import json
import random

import paho.mqtt.client as mqtt
import requests
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, request

from sending_config import *

info = 'Negro Leagues Player raiting'
print(info)
players = []
r2 = requests.get(source5)
for i in range(1, len(r2.text.splitlines())):
    players.append([r2.text.splitlines()[i].rsplit(',')[0], r2.text.splitlines()[i].rsplit(',')[1]])


def random_players(number):
    players_dict = {}
    for i in range(number):
        player = random.choice(players)
        players_dict[player[1]] = player[0]
    return players_dict


def send_data(method):
    if method == 'HTTP':
        requests.post(URL_server, json={'Apk_name': config.get('Apk_name'), 'Data': random_players(3)})
        print('message sent http')
    if method == 'MQTT':
        client = mqtt.Client('Election-Results')
        client.connect(broker_URL)
        client.loop_start()
        client.publish(broker_topic, json.dumps({'Apk_name': config.get('Apk_name'), 'Data': random_players(3)}))
        print('message sent mqtt')
        client.loop_stop()


app = Flask(__name__)
app.secret_key = "super secret key"
config = {'Sending Method': sending_method,
          'Sleep Time': str(sleep_time),
          'URL_server': URL_server,
          'broker_URL': broker_URL,
          'broker_topic': broker_topic,
          'Apk_URL': 'http://127.0.0.1:5005',
          'state': state,
          'Apk_name': 'Negro Players'}


@app.route('/', methods=['POST'])
def modify():
    scheduler.reschedule_job(trigger='interval',
                             seconds=request.json['Sleep Time'], job_id='5')
    scheduler.modify_job(job_id='5', args=[request.json['Sending Method']])

    return 'Modified', 201


if __name__ == "__main__":
    scheduler = BackgroundScheduler()
    scheduler.add_job(id='5', func=send_data, args=[sending_method], trigger='interval', seconds=sleep_time)
    scheduler.start()
    scheduler.pause_job(job_id='5')
    requests.post(URL_Manager + 'register', json=config)
    app.run(port=5005)


def exit_handler():
    requests.post(URL_Manager + 'end', json=config)


atexit.register(exit_handler)
