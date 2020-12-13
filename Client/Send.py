import CBOR as cbor
import COAP as coap
from network import LoRa
import socket
import time
import binascii
import pycom
import BMEDis as bmeDis
from machine import I2C

i2c = I2C(0, I2C.MASTER, baudrate=400000)
print (i2c.scan())
# Object Lora
lora = LoRa(mode=LoRa.LORAWAN, region=LoRa.EU868)

print ("devEUI {}".format(binascii.hexlify(lora.mac())))
# appEUI Application identifier
app_eui = binascii.unhexlify('00 00 00 00 00 00 00 00'.replace(' ',''))
# appkey Key chiffrement
app_key = binascii.unhexlify('11 22 33 44 55 66 77 88 11 22 33 44 55 66 77 88'.replace(' ',''))
#method to join the network
lora.join(activation=LoRa.OTAA, auth=(app_eui, app_key),  timeout=0)

pycom.heartbeat(False)
pycom.rgbled(0x111111)


while not lora.has_joined():
    time.sleep(2.5)
    print('Not yet joined...')

pycom.rgbled(0x000000)
# Socket used to communicate with layer loraWAN
s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
#s.bind(5)
s.setsockopt(socket.SOL_LORA, socket.SO_DR, 0)
s.setsockopt(socket.SOL_LORA,  socket.SO_CONFIRMED,  False)

nbMsg = 1

while True:
    #method that mesure the distance
    dist = bmeDis.distance_measure()
    print(dist)
    #Code data cbor
    c = cbor.dumps([int(dist*100)])
    print (c)
    nbMsg += 1
    # send data using protocole CoAP
    post = coap.CoAP()
    post.new_header(Type=coap.CON, Code=coap.POST, Token = 0x1234)
    post.add_option_URI_path("DIS") #URI Distance
    post.add_option_content(coap.CONTENT_CBOR)
    post.end_option()
    post.add_value(c)


    s.setblocking(True)
    s.settimeout(10)

    data = None

    print ("Sending...")
    print (post)
    post.dump()
    try:
        s.send(post.to_coap())
    except:
        print ('timeout in sending')

    print ()
    try:
        data = s.recv(64)
        pycom.rgbled(0x001100)

    except:
        print ('timeout in receive')
        pycom.rgbled(0x000000)

    if data is not None:
        rep_coap = coap.CoAP(data)
        print ("Received...")
        print(rep_coap)
        rep_coap.dump()
    else:
        print ("No DW data")

    s.setblocking(False)

    time.sleep (5)
