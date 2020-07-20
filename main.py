import machine
from machine import Pin
import math
import network
import os
import time
import utime
import gc
from machine import RTC
from machine import SD
from L76GNSS import L76GNSS
from pytrack import Pytrack
from mqtt import MQTTClient

time.sleep(2)
gc.enable()


def sub_cb(topic, msg):
    print(msg)


client = MQTTClient("b682b74962024ff1b2961b094b8ea9c5", "cncg.cloud", port=30001)

client.set_callback(sub_cb)
client.connect()
client.subscribe(topic="/pycom/test")

# setup rtc
rtc = machine.RTC()
rtc.ntp_sync("pool.ntp.org")
utime.sleep_ms(750)
print('\nRTC Set from NTP to UTC:', rtc.now())
utime.timezone(7200)
print('Adjusted from UTC to EST timezone', utime.localtime(), '\n')

py = Pytrack()
l76 = L76GNSS(py, timeout=30)

# sd = SD()
# os.mount(sd, '/sd')
# f = open('/sd/gps-record.txt', 'w')

def pin_handler(arg):
    coord = l76.coordinates()
    print("got an interrupt in pin %s" % (arg.id()))
    client.publish(topic="/pycom/test", msg="{} - {} - {}".format(coord, rtc.now(), gc.mem_free()))
    # f.write("{} - {}\n".format(coord, rtc.now()))
    # print("{} - {} - {}".format(coord, rtc.now(), gc.mem_free()))

p_in = Pin('P14', mode=Pin.IN, pull=Pin.PULL_UP)
p_in.callback(Pin.IRQ_FALLING, pin_handler)