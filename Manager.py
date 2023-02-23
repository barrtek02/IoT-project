import requests
from flask import Flask, render_template, request, url_for, flash, redirect

from sending_config import *

app = Flask(__name__)
app.secret_key = "super secret key"

messages = []
config = {}
apps_urls = {}
x = 'a'


@app.route('/')
def index():
    return render_template('index.html', messages=messages)


@app.route('/register/', methods=['POST'])
def register():
    if request.json['Apk_URL'] in apps_urls.values():
        return 'Already Exists', 400
    app_id = str(len(messages) + 1)
    apps_urls[app_id] = request.json['Apk_URL']
    config[app_id] = request.json
    messages.append({'title': f"ID: '{app_id}'   {config[app_id]['Apk_name']} - {config[app_id]['state']}",
                     'content': f"'Sending Method': {config[app_id]['Sending Method']}, 'Sleep Time': {config[app_id]['Sleep Time']}",
                     'Apk_name': request.json['Apk_name'],
                     'ID': app_id})
    return 'Registered', 201


@app.route('/create/<app_id>', methods=('GET', 'POST'))
def create(app_id):
    if request.method == 'POST':
        read_id = str(app_id)
        read_sending_method = request.form["inlineRadioOptions"]
        read_sleep_time = int(request.form["sleep_time"])
        if read_sleep_time > 9999:
            read_state = 'OFF'
        else:
            read_state = 'ON'
        if not sending_method:
            flash('Sending Method is required!')
        elif not sleep_time:
            flash('Sleep Time is required!')
        else:
            params = {'ID': read_id, 'Sending Method': read_sending_method, 'Sleep Time': read_sleep_time}
            requests.post(apps_urls[read_id], json=params)
            messages[int(read_id) - 1] = {
                'title': f"ID: '{read_id}'       {config[read_id]['Apk_name']} - {read_state}",
                'content': f"'Sending Method': {read_sending_method}, 'Sleep Time': {read_sleep_time}",
                'Apk_name': config[read_id]['Apk_name'],
                'ID': app_id}
            return redirect(url_for('index'))

    return render_template('edit.html')


@app.route('/create2/<app_id>', methods=('GET', 'POST'))
def create2(app_id):
    if request.method == 'POST':
        read_id = str(app_id)
        read_sending_method = request.form["inlineRadioOptions"]
        read_sleep_time = int(request.form["sleep_time"])

        read_collecting_method = request.form["inlineRadioOptions2"]
        if read_sending_method == 'MQTT':
            read_where_send = request.form["broker_topic"]
        else:
            read_where_send = str(request.form["send_URL"])

        if read_sleep_time > 9999:
            read_state = 'OFF'
        else:
            read_state = 'ON'
        if not sending_method:
            flash('Sending Method is required!')
        elif not sleep_time:
            flash('Sleep Time is required!')
        else:
            params = {'ID': read_id, 'Sending Method': read_sending_method, 'Sleep Time': read_sleep_time,
                      'Collecting Method': read_collecting_method, 'Where_send': read_where_send,
                      'Current Datasets': str(len(messages) - 1)}
            requests.post(apps_urls[read_id], json=params)
            messages[int(read_id) - 1] = {
                'title': f"ID: '{read_id}'       {config[read_id]['Apk_name']} - {read_state}",
                'content': f"'Sending Method': {read_sending_method}, 'Sleep Time': {read_sleep_time}",
                'Apk_name': config[read_id]['Apk_name'],
                'ID': app_id}
            return redirect(url_for('index'))

    return render_template('edit_aggregator.html')


@app.route('/create3/<app_id>', methods=('GET', 'POST'))
def create3(app_id):
    if request.method == 'POST':
        read_id = str(app_id)
        read_sending_method = request.form["inlineRadioOptions"]
        read_sleep_time = int(request.form["sleep_time"])

        ck1_v, ck2_v, ck3_v = 'False', 'False', 'False'
        if request.form.get("ck1"):
            ck1_v = 'True'
        if request.form.get("ck2"):
            ck2_v = 'True'
        if request.form.get("ck3"):
            ck3_v = 'True'

        read_collecting_method = request.form["inlineRadioOptions2"]
        if read_sending_method == 'MQTT':
            read_where_send = request.form["broker_topic"]
        else:
            read_where_send = str(request.form["send_URL"])

        if read_sleep_time > 9999:
            read_state = 'OFF'
        else:
            read_state = 'ON'
        if not sending_method:
            flash('Sending Method is required!')
        elif not sleep_time:
            flash('Sleep Time is required!')
        else:
            params = {'ID': read_id, 'Sending Method': read_sending_method, 'Sleep Time': read_sleep_time,
                      'Collecting Method': read_collecting_method, 'Where_send': read_where_send,
                      'Current Datasets': str(len(messages) - 1),
                      'filters': {'Names': ck1_v, 'Nicks': ck2_v, 'Geo locations': ck3_v}}
            requests.post(apps_urls[read_id], json=params)
            messages[int(read_id) - 1] = {
                'title': f"ID: '{read_id}'       {config[read_id]['Apk_name']} - {read_state}",
                'content': f"'Sending Method': {read_sending_method}, 'Sleep Time': {read_sleep_time}",
                'Apk_name': config[read_id]['Apk_name'],
                'ID': app_id}
            return redirect(url_for('index'))

    return render_template('edit_filter.html')


@app.route('/create4/<app_id>', methods=('GET', 'POST'))
def create4(app_id):
    if request.method == 'POST':
        # config['lower_limit'] = int(request.json['lower_limit'])
        # config['upper_limit'] = int(request.json['upper_limit'])
        # config['power'] = request.json['power']
        # config['broker_topic_send'] = request.json['Where_send']
        read_id = str(app_id)
        read_sleep_time = int(request.form["sleep_time"])
        read_lower_limit = int(request.form["lower_limit"])
        read_upper_limit = int(request.form["upper_limit"])
        read_where_send = request.form["Where_send"]

        if read_sleep_time > 9999:
            read_state = 'OFF'
        else:
            read_state = 'ON'

        if not sleep_time:
            flash('Sleep Time is required!')
        else:
            params = {'ID': read_id, 'Sleep Time': read_sleep_time, 'Where_send': read_where_send
                , 'lower_limit': read_lower_limit, 'upper_limit': read_upper_limit}
            requests.post(apps_urls[read_id], json=params)
            messages[int(read_id) - 1] = {
                'title': f"ID: '{read_id}'       {config[read_id]['Apk_name']} - {read_state}",
                'content': f"'Sending Method': MQTT, 'Sleep Time': {read_sleep_time}",
                'Apk_name': config[read_id]['Apk_name'],
                'ID': app_id}
            return redirect(url_for('index'))

    return render_template('edit_controller.html')


@app.route('/create5/<app_id>', methods=('GET', 'POST'))
def create5(app_id):
    if request.method == 'POST':
        read_id = str(app_id)
        read_sleep_time = int(request.form["sleep_time"])
        read_power = int(request.form["power"])

        if read_sleep_time > 9999:
            read_state = 'OFF'
        else:
            read_state = 'ON'
        if not sleep_time:
            flash('Sleep Time is required!')
        else:
            params = {'ID': read_id, 'Sending Method': 'MQTT', 'Sleep Time': read_sleep_time,
                      'power': read_power}
            requests.post(apps_urls[read_id], json=params)
            messages[int(read_id) - 1] = {
                'title': f"ID: '{read_id}'       {config[read_id]['Apk_name']} - {read_state}",
                'content': f"'Sending Method': 'MQTT', 'Sleep Time': {read_sleep_time}",
                'Apk_name': config[read_id]['Apk_name'],
                'ID': app_id}
            return redirect(url_for('index'))

    return render_template('edit_heater.html')


@app.route('/diagram/<app_name>', methods=('GET', 'POST'))
def diagram(app_name):
    response = requests.get('http://localhost:5025/diagram/' + app_name)
    if response.status_code == 200:
        # save the diagram to a file
        with open('static/diagram.png', 'wb') as f:
            f.write(response.content)
    return '''
        <html>
            <body>
                <img src="/static/diagram.png" alt="Diagram">
            </body>
        </html>
    '''


@app.route('/end/', methods=['POST'])
def unexpected_end():
    for id, url in apps_urls.items():
        if url == request.json['Apk_URL']:
            end_id = id
            messages[int(end_id) - 1] = {'title': f"ID: '{end_id}'       {config[end_id]['Apk_name']} - OFF",
                                         'content': f"Waiting for new connection / EDIT params",
                                         'Apk_name': config[end_id]['Apk_name'],
                                         'ID': end_id
                                         }
    return 'Ended'


if __name__ == "__main__":
    app.run(port=5010)
