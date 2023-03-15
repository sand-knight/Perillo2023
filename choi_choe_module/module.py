import paho.mqtt.client as mqtt
import asyncio
from collections import deque
from perillo_funcs import *

async def main(close_event : asyncio.Event):
    samples = deque(maxlen=400)
    turn = 0

    def on_connect(client, userdata, flags, rc):
        print("mqtt connected")
        client.subscribe("paziente/segnali/bcg")

    def on_message(client:mqtt.Client, userdata, msg):
        nonlocal turn
        samples.append( int(msg.payload) )
        turn+=1
        if turn == 425:
            turn = 400
            copy = samples.copy()
            val = diff_mean_choi(copy)
            client.publish(topic="paziente/segnali/algoritmi/choi", payload=str(val))
            val = diff_mean_choe(copy)
            client.publish(topic="paziente/segnali/algoritmi/choe", payload=str(val))

    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect("localhost")

    client.loop_start()
    print("MQTT client started")
    await close_event.wait()
    client.loop_stop()
