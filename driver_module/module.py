from datetime import datetime
from HappySleep_Driver import HappySleep_plugin
import paho.mqtt.client as mqtt
import asyncio, importlib

async def main(close_event: asyncio.Event):
    plugin = HappySleep_plugin()
    try:
        mqtt_client = mqtt.Client()
        mqtt_client.connect("localhost")
        
        def publish_callback(val, client, topic):
            client.publish(
                topic,
                payload=str(val[0])
            )


        await plugin.start()

        key1 = await plugin.register_data_stream(("bcg",), 0, publish_callback, mqtt_client, "paziente/segnali/bcg")
        key2 = await plugin.register_data_stream(("heartrate",), 0, publish_callback, mqtt_client, "paziente/segnali/aggregated/heartrate")
        key3 = await plugin.register_data_stream(("breathrate",), 0, publish_callback, mqtt_client, "paziente/segnali/aggregated/breathrate")
        key4 = await plugin.register_data_stream(("battery",), 0, publish_callback, mqtt_client, "paziente/sys/battery")

        await close_event.wait()

    except KeyboardInterrupt:
        pass
    except Exception as e:
        close_event.set()  # <--- posso rendere indipendenti gli script tra di loro togliendo questo da qua
        await plugin.stop()
        raise
    finally:
        print("Stopping HappySleep Driver")
        await plugin.stop()