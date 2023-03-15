import paho.mqtt.client as mqtt
import asyncio, numpy
from collections import deque

import utils
import tensorflow._api.v2.compat.v1 as tf
import warnings

async def main(close_event : asyncio.Event):
    tf.logging.set_verbosity(tf.logging.ERROR)
    config = tf.ConfigProto()
    config.gpu_options.allow_growth = True
    tf.keras.backend.set_session(tf.Session(config=config))
    warnings.filterwarnings("ignore")
    
    samples = deque(maxlen=400)
    turn = 0

    def on_connect(client, userdata, flags, rc):
        print("mqtt connected")
        client.subscribe("paziente/segnali/bcg")
        client.subscribe("configurazione/deeper_fcn_module/#")

    def on_message(client:mqtt.Client, userdata, msg):
        nonlocal turn
        samples.append( int(msg.payload) )
        turn+=1
        if turn == 450:
            turn = 400
            copy = samples.copy()
            val = simple_deeper_fcn(samples)
            client.publish(topic="paziente/segnali/algoritmi/deeper_fcn", payload=str(val))

    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.message_callback_add("configurazione/deeper_fcn_module/model", update_model)
    client.message_callback_add("configurazione/deeper_fcn_module/weights", update_weights)
    client.connect("localhost")

    client.loop_start()
    print("MQTT client started")
    await close_event.wait()
    client.loop_stop()

def simple_deeper_fcn(samples):
    model = utils.get_model_from_json("deeper_fcn_module/components/deeper_fcn10")
    model.load_weights("deeper_fcn_module/components/deeper_fcn10/weights")
    array = numpy.expand_dims(samples, axis=0)
    array = numpy.expand_dims(array, axis=2)
    result = model.predict(array)
    return result[0,0]

def update_model(client, userdata, message):
    file = open("deeper_fcn_module/components/deeper_fcn10/model.json", mode = "wb")
    print("got new model configuration file")
    file.write(message.payload)
    file.close()

def update_weights(client, userdata, message):
    file = open("deeper_fcn_module/components/deeper_fcn10/weights.data-00000-of-00001", mode = "wb")
    print("got new weights configuration file")
    file.write(message.payload)
    file.close()