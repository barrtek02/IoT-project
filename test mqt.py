import ast

import paho.mqtt.client as mqtt


def collect_mqtt():
    def on_message(client, userdata, message):
        message = str(message.payload.decode("utf-8"))
        message = ast.literal_eval(message)
        print(message)

    client = mqtt.Client('TEST_reader_2')
    client.on_message = on_message
    client.connect('test.mosquitto.org')
    # client.loop_start()
    client.subscribe('app/test23/')
    client.loop_forever()
    # time.sleep(120)
    client.loop_stop()


collect_mqtt()
