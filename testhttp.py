from flask import Flask, request, jsonify

app = Flask(__name__)

RAM_usage = []


@app.route('/', methods=['POST'])
def uploadMessage():
    RAM_usage.append(request.json)

    return 'Uploaded', 202


@app.route('/', methods=['GET'])
def checkRAM():
    return jsonify(RAM_usage)


if __name__ == "__main__":
    app.run(debug=True, port=5020)
