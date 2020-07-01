from flask import Flask
import requests
import threading
import signal
import logging
import time
from flask import request
import json

app = Flask(__name__)

access_token = ""
logger = logging.getLogger(__name__)

channels = {}
broadcasters = {}

CLIENT_ID = "ao93ev500wqpaczsn55vca74kli26z"
CLIENT_SECRETE = "wdcac9rjzje6lwxczkffwz1woj5iw9"


@app.before_first_request
def activate_job():
    def run_job():
        while True:
            get_access_token()
            time.sleep(60)

    thread = threading.Thread(target=run_job)
    thread.start()


def get_access_token():
    global access_token
    global CLIENT_ID
    global CLIENT_SECRETE
    params = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRETE,
        "grant_type": "client_credentials",
    }
    results = requests.post("https://id.twitch.tv/oauth2/token", params=params)
    json_results = results.json()
    access_token = json_results["access_token"]


@app.route("/token/refresh")
def token_refresh():
    global access_token
    get_access_token()
    return access_token


@app.route("/token")
def token():
    global access_token
    return access_token


@app.route("/channel/<channel>", methods=["GET"])
def channel(channel):
    global access_token
    global channels

    headers = {
        "Authorization": "Bearer " + access_token,
        "client-id": "ao93ev500wqpaczsn55vca74kli26z",
    }

    results = requests.get(
        f"https://api.twitch.tv/helix/search/channels?query={channel}&first=1",
        headers=headers,
    )
    json_results = results.json()
    # channels[json_results["id"]] = json_results

    id = json_results["data"][0]["id"]
    channels[id] = json_results
    return channels


@app.route("/broadcaster/<broadcaster_id>", methods=["GET"])
def broadcaster(broadcaster_id):
    global access_token
    global broadcasters
    global CLIENT_ID

    headers = {
        "Authorization": "Bearer " + access_token,
        "client-id": CLIENT_ID,
    }

    results = requests.get(
        f"https://api.twitch.tv/helix/channels?broadcaster_id={broadcaster_id}",
        headers=headers,
    )
    json_results = results.json()
    # channels[json_results["id"]] = json_results

    broadcasters[broadcaster_id] = json_results
    return channels


def set_interval(callback, time, once=False):
    event = threading.Event()
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    if once:
        callback()  # call once

    while not event.wait(time):
        callback()


@app.route("/")
def index():
    return "<h1>Welcome to our server !!</h1>"
