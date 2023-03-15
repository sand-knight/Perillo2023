import asyncio
import signal, os, importlib, sys

async def main():
    tasks = dict()
    closing_event = asyncio.Event() #modules will wait for this event to exit
    def handler():
        print("Interruption treated")
        closing_event.set()
    asyncio.get_event_loop().add_signal_handler(signal.SIGINT,handler )

    diriterator = os.scandir(".")
    for obj in diriterator:
        if obj.is_dir():
            if os.path.isfile(obj.path+"/module.py"): # find modules
                sys.path.append(obj.path)
                name=obj.path.split("/")[-1]          # folder name is module name
                module = importlib.import_module(name+".module") #import the module
                tasks[name] = asyncio.create_task(module.main(closing_event)) #call te module's main
                
    if len(tasks) > 0: ## await for close event and for each module
        await closing_event.wait()
        for task in tasks.values():
            await task

asyncio.run(main())