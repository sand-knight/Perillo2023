from HappySleep_Device import *
import asyncio
import time, datetime

verbose=False

if verbose:
    def verboseprint(*args):
        # Print each argument separately so caller doesn't need to
        # stuff everything to be printed into a single string
        
           print(", ".join(str(arg) for arg in args))
        
else:   
    verboseprint = lambda *a: None

class ValueType(Enum):
    NOTIFICATION = 0
    REQUESTRESPONSE = 1
    STATIC = 3
    
class HappySleep_plugin():
    is_plugin_active=False
    __registereds=dict()
    __heartbreath_reference_count = 0
    __humitemp_reference_count = 0
    __bcg_reference_count = 0
    __battery_service = None

    def __fetch(what, dictionary):
            values = []
            for k in what:
                variable = dictionary.get(k)
                if variable is not None:
                    values.append(variable.get("value"))
                else:
                    raise Exception("variable not found mid-running")
            return values

    async def __register_bcg(self):
        if self.__bcg_reference_count == 0 or not self.device.is_realtime_raw_bcg_on:
            await self.device.turn_realtime_raw_bcg_on(HappySleep_plugin.__update_bcg, self.__dictionary)
        self.__bcg_reference_count += 1

    async def __unregister_bcg(self):
        self.__bcg_reference_count -= 1
        if self.__bcg_reference_count <= 0:
            await self.device.turn_realtime_raw_bcg_off()

    async def __update_bcg (val : int, dictionary):
        
        for callback in dictionary["bcg"]["on_update_callbacks"]:
            if asyncio.iscoroutinefunction(callback[0]):

                await callback[0](val, *callback[2])
            else:
                callback[0](val, *callback[2])
    
    async def __update_bcg (val : int, dictionary):
        dictionary["bcg"]["value"] = val
        for callback in dictionary["bcg"]["on_update_callbacks"]:
            values=[]
            for k in callback[1]:
                values.append(dictionary[k]["value"])
            if asyncio.iscoroutinefunction(callback[0]):    
                await callback[0](values, *callback[2])
            else:
                callback[0](values, *callback[2])

    async def __register_heartbreath(self):

        if self.__heartbreath_reference_count == 0 :#or not self.device.is_realtime_heartbreath_on:
            await self.device.turn_realtime_heartbreath_on(HappySleep_plugin.__update_heartbreath, self.__dictionary)
        self.__heartbreath_reference_count+=1
        
    async def __unregister_heartbreath(self):
        self.__heartbreath_reference_count-=1
        if self.__heartbreath_reference_count <= 0:
            await self.device.turn_realtime_heartbreath_off()

    

    async def __update_heartbreath(obj : Realtime_Heartbreath, dictionary,  ):
        #start executing every callback registered on update
        #finally await their exit


        tasks = []
        verboseprint("heartbreath received")
        if obj.heartrate>40 and obj.heartrate<124 :
            verboseprint("but is out of valid range")
            dictionary["heartrate"]["value"]=obj.heartrate
            dictionary["heartrate"]["timestamp"]=obj.last_updated
            for callback in dictionary["heartrate"]["on_update_callbacks"]:
                if asyncio.iscoroutinefunction(callback[0]):
                    tasks.append(
                        asyncio.create_task(
                            callback[0](
                                HappySleep_plugin.__fetch(callback[1], dictionary),
                                *callback[2]
                            )
                        )
                    )
                else:
                    callback[0](HappySleep_plugin.__fetch(callback[1], dictionary), *callback[2])

        if obj.breathrate>5 and obj.breathrate<40 :
            dictionary["breathrate"]["value"]=obj.breathrate
            dictionary["breathrate"]["timestamp"]=obj.last_updated
            for callback in dictionary["breathrate"]["on_update_callbacks"]:
                if asyncio.iscoroutinefunction(callback[0]):
                    tasks.append(
                        asyncio.create_task(
                            callback[0](
                                HappySleep_plugin.__fetch(callback[1], dictionary),
                                *callback[2]
                            )
                        )
                    )
                else:
                    callback[0](HappySleep_plugin.__fetch(callback[1], dictionary), *callback[2])
        
        old_val=dictionary["moving"]["value"]
        dictionary["moving"]["value"] = obj.moving
        dictionary["moving"]["timestamp"] = obj.last_updated
        if old_val != obj.moving:
            for callback in dictionary["moving"]["on_update_callbacks"]:
                if asyncio.iscoroutinefunction(callback[0]):
                    tasks.append(
                        asyncio.create_task(
                            callback[0](
                                HappySleep_plugin.__fetch(callback[1], dictionary),
                                *callback[2]
                            )
                        )
                    )
                else:
                    callback[0](HappySleep_plugin.__fetch(callback[1], dictionary), *callback[2])
        
        old_val=dictionary["moving"]["value"]
        dictionary["absent"]["value"] = obj.absent
        dictionary["absent"]["timestamp"] = obj.last_updated
        if old_val != obj.absent:
            for callback in dictionary["absent"]["on_update_callbacks"]:
                if asyncio.iscoroutinefunction(callback[0]):
                    tasks.append(
                        asyncio.create_task(
                            callback[0](
                                HappySleep_plugin.__fetch(callback[1], dictionary),
                                *callback[2]
                            )
                        )
                    )
                else:
                    callback[0](HappySleep.__fetch(callback[1], dictionary), *callback[2])

        for task in tasks:
            await task


    async def __register_humitemp(self):
        verboseprint("~~~~~~~~~~~ HUMIDITY REGISTERING ~~~~~~~~~~~~~~~~~~~~~~~")
        if self.__humitemp_reference_count == 0 or not self.device.is_realtime_temperature_humidity_on:
            await self.device.turn_realtime_temperature_humidity_on(HappySleep_plugin.__update_humitemp, self.__dictionary)
        self.__humitemp_reference_count+=1
        
    async def __unregister_humitemp(self):
        self.__humitemp_reference_count-=1
        if self.__humitemp_reference_count <= 0:
            await self.device.turn_realtime_temperature_humidity_off()

    async def __update_humitemp(obj : Realtime_Temperature_Humidity, dictionary):
        tasks = []
        #start executing every callback registered in the dictionary
        #put them in task
        #and finally await them all

        old_val = dictionary["temperature"]["value"]
        dictionary["temperature"]["value"] = obj.temperature
        dictionary["temperature"]["timestamp"] = obj.last_updated
        if old_val != obj.temperature:
            for callback in dictionary["temperature"]["on_update_callbacks"]:
                if asyncio.iscoroutinefunction(callback[0]):
                    tasks.append(
                        asyncio.create_task(
                            callback[0](
                                HappySleep_plugin.__fetch(callback[1], dictionary),
                                *callback[2]
                            )
                        )
                    )
                else:
                    callback[0](HappySleep_plugin.__fetch(callback[1], dictionary), *callback[2])

        old_val = dictionary["humidity"]["value"]
        dictionary["humidity"]["value"] = obj.humidity
        dictionary["humidity"]["timestamp"] = obj.last_updated
        if old_val != obj.humidity:
            for callback in dictionary["humidity"]["on_update_callbacks"]:
                if asyncio.iscoroutinefunction(callback[0]):
                    tasks.append(
                        asyncio.create_task(
                            callback[0](
                                HappySleep_plugin.__fetch(callback[1], dictionary),
                                *callback[2]
                            )
                        )
                    )
                else:
                    callback[0](HappySleep_plugin.__fetch(callback[1], dictionary), *callback[2])

        for task in tasks:
            await task

    async def __update_battery(val , dictionary):
            oldval = dictionary["battery"]["value"]

            if oldval != val :
                dictionary["battery"]["value"] = val
                for callback in dictionary["battery"]["on_update_callbacks"]:
                    if asyncio.iscoroutinefunction(callback[0]):
                        await callback[0](
                            HappySleep_plugin.__fetch(callback[1], dictionary),
                            *callback[2],
                            **callback[3]
                        )
                    else:
                        callback[0](HappySleep_plugin.__fetch(callback[1], dictionary), *callback[2])



    __dictionary={
        "heartrate" : {
                        "type" : ValueType.NOTIFICATION,
                        "on_update_callbacks" : None,
                        "value" : None,
                        "timestamp" : None,
                        "on_register" : __register_heartbreath,
                        "on_update" : __update_heartbreath,
                        "on_update_callbacks" : [],
                        "on_unregister" : __unregister_heartbreath
                        
                    },

        "heartrate_unit" : {
                        "type" : ValueType.STATIC,
                        "value" : "bpm"
                    },
        
        "breathrate" : {
                        "type" : ValueType.NOTIFICATION,
                        "value" : None,
                        "timestamp" : None,
                        "on_register" : __register_heartbreath,
                        "on_update" : __update_heartbreath,
                        "on_update_callbacks" : [],
                        "on_unregister" : __unregister_heartbreath

                    },
        "breathrate_unit" : {
                        "type" : ValueType.STATIC,
                        "value" : "bpm"
                    },
            
        "moving" : {

                        "type" : ValueType.NOTIFICATION,
                        "value" : None,
                        "timestamp" : None,
                        "on_register" : __register_heartbreath,
                        "on_update" : __update_heartbreath,
                        "on_update_callbacks" : [],
                        "on_unregister" : __register_heartbreath
                    },

        "absent" : {
                        "type" : ValueType.NOTIFICATION,
                        "value" : None,
                        "timestamp" : None,
                        "on_register" : __register_heartbreath,
                        "on_update" : __update_heartbreath,
                        "on_update_callbacks" : [],
                        "on_unregister" : __register_heartbreath
                    },
        "battery" : {
                        "type" : ValueType.NOTIFICATION,
                        "value" : None,
                        "timestamp" : None,
                        "on_register" : None,
                        "on_update" : __update_battery,
                        "on_update_callbacks" : [],
                        "on_unregister" : None
        },
        "battery_unit" : {
                        "type" : ValueType.STATIC,
                        "value" : "%"
        },
        "gender" : {
                        "type" : ValueType.STATIC,
                        "value" : "bpm"
        },
        "age" : {
                        "type" : ValueType.STATIC,
                        "value" : "bpm"
        },
        "height" : {
                        "type" : ValueType.STATIC,
                        "value" : "bpm"
        },
        "weight" : {
                        "type" : ValueType.STATIC,
                        "value" : "bpm"
        },
        "temperature" : {
                        "type" : ValueType.NOTIFICATION,
                        "value" : None,
                        "timestamp" : None,
                        "on_register" : __register_humitemp,
                        "on_update" : __update_humitemp,
                        "on_update_callbacks" : [],
                        "on_unregister" : __unregister_humitemp


        },
        "temperature_unit" : {
                        "type" : ValueType.STATIC,
                        "value" : "°C"
        },
        "humidity" : {
                        "type" : ValueType.NOTIFICATION,
                        "value" : None,
                        "timestamp" : None,
                        "on_register" : __register_humitemp,
                        "on_update" : __update_humitemp,
                        "on_update_callbacks" : [],
                        "on_unregister" : __unregister_humitemp
        },
        "humidity_unit" : {
                        "type" : ValueType.STATIC,
                        "value" : "%"
        },
        "bcg" : {
                        "type" : ValueType.NOTIFICATION,
                        "value" : None,
                        "timestamp" : None,
                        "on_register" : __register_bcg,
                        "on_update" : __update_bcg,
                        "on_update_callbacks" : [],
                        "on_unregister" : __unregister_bcg
        }
        
    }

    async def __treat_disconnect(self):
        await self.device.disconnect_event.wait()
        await self.stop()

    def __init__(self, ble_mac_address:str=None):
        self.device=HappySleep_belt(ble_mac_address)

    async def start(self):
        if not self.device.is_connected:
            await self.device.connect()

        ## update person information:
        info = await self.device.get_user_info()
        self.__dictionary["gender"]["value"] = info.gender
        self.__dictionary["age"]["value"] = info.age
        self.__dictionary["height"]["value"] = info.height
        self.__dictionary["weight"]["value"] = info.weight

        ##start battery service:

        async def battery_func(self):
            try:
                while(self.device.is_connected):
                    await asyncio.sleep(5)
                    val = await self.device.get_power()
                    await self.__dictionary["battery"]["on_update"](val, self.__dictionary)
            except asyncio.CancelledError as e:
                verboseprint("Exited from battery watchdog")
            except Exception:
                raise

        self.__battery_service = asyncio.create_task(battery_func(self))

        self.__disconnect_watchdog = asyncio.create_task(self.__treat_disconnect())

    
    async def register_data_stream(self, what:tuple, cadence : float, callback, *callback_args, **callback_kwargs):

        if cadence >0 and "bcg" in what:
            raise Exception("Unsupported operation on bcg")

        for k in what:
            if self.__dictionary[k]["type"] != ValueType.STATIC:
                if self.__dictionary[k]["on_register"] is not None:
                    await self.__dictionary[k]["on_register"](self)
            
        async def task_func(device, dictionary, what, cadence, callback, *callback_args, **callback_kwargs):
            try:
                while True:
                    valueslist = []

                    for k in what:

                        valueslist.append(dictionary[k]["value"])

                    if asyncio.iscoroutinefunction(callback):
                        await callback(valueslist, *callback_args, **callback_kwargs)
                    else:
                        callback(valueslist, *callback_args, **callback_kwargs)

                    await asyncio.sleep(cadence)
            except asyncio.CancelledError as e:
                print(e)
                
        

        if cadence>0:  
            task = asyncio.create_task(task_func(self.device, self.__dictionary, what, cadence, callback, *callback_args, **callback_kwargs))
            value = (task, what,)
            key = hash((callback, what, *callback_args, cadence))
            
        else:
            value = (callback, what, callback_args)
            for k in what:
                if self.__dictionary[k].get("on_update_callbacks") is not None:
                    self.__dictionary[k]["on_update_callbacks"].append(value)
            key = hash(value)
            #treatment = (callback, callback_args, callback_kwargs,)
            #value = (treatment, what)

        self.__registereds[key]=value
        return key

    async def unregister_data_stream(self, key):
        
        ob=self.__registereds.get(key)
        if ob is None:
            print("Key not found")
            return

        if callable(ob[0]):
            for k in ob[1]:
                if self.__dictionary[k]["type"] != ValueType.STATIC:
                    if self.__dictionary[k].get("on_update_callbacks") is not None:
                        self.__dictionary[k]["on_update_callbacks"].remove(ob)
                    
                    if self.__dictionary[k].get("on_unregister") is not None:
                        await self.__dictionary[k]["on_unregister"](self)

        elif isinstance(key, asyncio.Task):

            ob[0].cancel()
            await ob[0]
            for k in ob[1]:
                if self.dictionary[k]["type"] != ValueType.STATIC:
                    if self.__dictionary[k].get("on_unregister") is not None:
                        await self.__dictionary[k]["on_unregister"](self)

        self.__registereds.pop(key)


    async def stop(self):
        for obj in self.__registereds.values():
            if isinstance(obj[0] , asyncio.Task):
                obj[0].cancel()
                await obj[0]

        if self.__battery_service:
            self.__battery_service.cancel()
            await self.__battery_service

        if self.device.is_realtime_heartbreath_on:
            await self.device.turn_realtime_heartbreath_off()
        if self.device.is_realtime_temperature_humidity_on:
            await self.device.turn_realtime_temperature_humidity_off()
        if self.device.is_realtime_raw_bcg_on:
            await self.device.turn_realtime_raw_bcg_off()

        for value in self.__dictionary.values():
            if value.get("on_update_callbacks") is not None and len(value["on_update_callbacks"]) > 0:
                value["on_update_callbacks"].clear()

        self.__registereds.clear()


        await self.device.disconnect()



# def mqtt_publish(stringa:str, client:mqtt.Client, topic:str):
# client.publish(topic, payload=stringa)

# >>> print (a.__dict__)
# {'heartrate': 20, 'breathrate': 30, 'moving': 1, 'absent': 0, 'last_updated': 1676379054.1492388}
