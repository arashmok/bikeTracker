import machine
from machine import Pin
import math
import network
import os
import time
import utime
import gc
import pycom
from machine import RTC
from machine import SD
from L76GNSS import L76GNSS
from pytrack import Pytrack
from mqtt import MQTTClient

# mqtt parameters
MQTTHOST = "cncg.cloud"
MQTTPORT = 30001
client_id = "dd04441ec6b04802a460a4d799c61cfa"
Topic = "/fipy/#"
# Instantiating the interface object of MQTT client
client = MQTTClient(client_id, MQTTHOST, port=MQTTPORT)

time.sleep(2)
gc.enable()

py = Pytrack()
l76 = L76GNSS(py, timeout=30)


# setup rtc
rtc = machine.RTC()
rtc.ntp_sync("pool.ntp.org")
utime.sleep_ms(750)
print('\nRTC Set from NTP to UTC:', rtc.now())
utime.timezone(7200)
print('Adjusted from UTC to EST timezone', utime.localtime(), '\n')

def sig_led(color):
    pycom.heartbeat(False)
    pycom.rgbled(color)
    time.sleep(0.1)
    pycom.heartbeat(True)

def pin_handler(arg):
    coord = l76.coordinates()
    print("got an interrupt in pin %s" % (arg.id()))
    client.publish(topic="/fipy/loc", msg="{} - {}".format(coord, utime.localtime()))
    sig_led(0xff00)
    print("Time - Coordinates = {} - {}".format(utime.localtime() ,coord))
    # f.write("{} - {}\n".format(coord, rtc.now()))
    # print("{} - {} - {}".format(coord, rtc.now(), gc.mem_free()))


def sub_cb(topic, msg):
    #print("Received {} on the following topic: {}".format(msg,topic))
    # if the received message contains 'req' keyword
    # then publish current coordination on the /fipy/loc topic
    if msg == b'req':
        coord = l76.coordinates()
        client.publish(topic="/fipy/loc", msg="{} - {}".format(coord, utime.localtime()))
        sig_led(0xff00)
        print("Time - Coordinates = {} - {}".format(utime.localtime() ,coord))


client.set_callback(sub_cb)
client.connect()
client.subscribe(Topic)

# sd = SD()
# os.mount(sd, '/sd')
# f = open('/sd/gps-record.txt', 'w')

p_in = Pin('P14', mode=Pin.IN, pull=Pin.PULL_UP)
p_in.callback(Pin.IRQ_FALLING, pin_handler)

# Check for the new messages that are published.
while True:
    client.check_msg()
    time.sleep(1)
client.disconnect()
