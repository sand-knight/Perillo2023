import asyncio
import paho.mqtt.client as mqtt

async def main(close_event : asyncio.Event):
    client = mqtt.Client()
    task = asyncio.create_task(send_configuration(client))

    client.connect("localhost")

    client.loop_start()
    print("MQTT client started")
    await close_event.wait()
    client.loop_stop()
    task.cancel()
    await task

async def send_configuration(client):
    
    try:
        while True:
            await asyncio.sleep(10)
            file = open("deeper_fcn_module/components/deeper_fcn9/model.json", mode = "rb")
            msg = file.read()
            file.close()
            client.publish(topic="configurazione/deeper_fcn_module/model", payload=msg)
            file = open("deeper_fcn_module/components/deeper_fcn9/weights.data-00000-of-00001", mode = "rb")
            msg = file.read()
            file.close()
            client.publish(topic="configurazione/deeper_fcn_module/weights", payload=msg)
    except asyncio.CancelledError:
        if file:
            file.close()
    