from flask import Flask, request
import json
app = Flask(__name__)


@app.route('/')
def hello_world():
    headers = {}
    for header in request.headers:
        headers[header[0]] = header[1]
    return headers