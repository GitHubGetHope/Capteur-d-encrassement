#!/usr/bin/env python3

import sys, getopt
from flask import Flask
from flask import request
from flask import Response
import base64
import pprint
import json
import binascii

import socket
import select
import time

app = Flask(__name__)

app.debug = True

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
inputs = [sock]
outputs = []

defPort = 7000

@app.route('/lns', methods=['POST'])
def get_from_LNS():

    global defPort

    fromGW = request.get_json(force=True)
    print ("HTTP POST RECEIVED")
    pprint.pprint(fromGW)
    if "data" in fromGW:
        payload = base64.b64decode(fromGW["data"])
        #print (payload)

        IPlb = "127.0.{}.{}".format(defPort >> 8, defPort & 0xFF);
        print (IPlb)

        sock.sendto(payload, (IPlb, defPort+5683))

        readable, writable, exceptional = select.select(inputs, outputs, inputs, 0.1)


        if readable == []:
            print ("No rapid answer")
            resp = Response(status=200)
            print (resp)
            return resp

        for s in readable:
            replyStr = s.recv(1000)
            print (type(replyStr), binascii.hexlify(replyStr))

        answer = {
            "fPort" : fromGW["fPort"],
            "devEUI": fromGW["devEUI"],
            "data"  : base64.b64encode(replyStr).decode('utf-8')
        }

        print()
        print ("HTTP POST REPLY")
        pprint.pprint(answer)
        resp = Response(response=json.dumps(answer), status=200, mimetype="application/json")
        print (resp)
        return resp

    else:
        print ("No data")
        resp = Response(status=200)
        print (resp)
        return resp


if __name__ == '__main__':
    print (sys.argv)

#    global defPort = 7000

    try:
        opts, args = getopt.getopt(sys.argv[1:],"hp:",["port="])
    except getopt.GetoptError:
        print ("{0} -p <port> -h".format(sys.argv[0]))
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print ("{0} -p <port> -h".format(sys.argv[0]))
            sys.exit()
        elif opt in ("-p", "--port"):
            defPort = int(arg)


    app.run(host="0.0.0.0", port=defPort)
