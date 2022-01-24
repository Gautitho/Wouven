import argparse
import functions
import asyncio
import websockets
import os
import logging
from GameManager import *

async def handler(websocket):
    while True:
        #try:
            #testFile = open("log", "w") # This line reset socket connection
            #testFile.write('anything')
            #testFile.close()
            os.system("echo 'Ploot'")
            message = await websocket.recv()
            await websocket.send('{"cmd" : "ERROR", "msg" : "This is a test"}')
        #except websockets.ConnectionClosedOK:
        #    break

async def main():
    async with websockets.serve(handler, "", 50000):
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    #allLogger = createLogger("all", "logs/all.log", "a", "FULL")
    #testFile = open("log", "w") # This line reset socket connection
    #testFile.write('anything')
    #testFile.close()
    #clientLogger = createLogger("client", "logs/client.log", "w+")
    asyncio.run(main())