#!/usr/bin/env python3

import sys, getopt
from flask import Flask
from flask import request
from flask import Response
from flask import abort
import base64
import pprint
import json
import binascii
from bson.json_util import dumps as bjdumps

import socket
import select
import time

from pymongo import MongoClient

app = Flask(__name__)

app.debug = True

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
inputs = [sock]
outputs = []

defPort = 8080

@app.route('/Distance', methods=['GET'])
def QueryMongo():
    print ("Requete")

    device = request.args.get('device')
    print("device ", device)

    if device == None:
        abort(Response("device not specified"))


    found_item = measures.find_one ({"Name" : device })
    if found_item == None:
        abort(Response('Device {} not found'.format(device)))

    sensor_id = found_item["_id"]

    res = measures.find({"SensorCharacteristics": sensor_id},
    {"Date":1, "Distance":1, "_id":0})

    print(res)
    resp = Response(bjdumps(res))
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp


if __name__ == '__main__':

    client = MongoClient()
    db= client["Projet"]
    measures = db.Distance
    

    app.run(host="0.0.0.0", port=defPort)
