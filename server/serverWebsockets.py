import argparse
import functions
import asyncio
import websockets
from GameManager import *

clientList      = []
clientIdList    = []
gameManager     = GameManager()

async def handler(websocket):
    while True:
        clientMsg = await websocket.recv()
        if not(websocket.id.hex in clientIdList):
            clientList.append(websocket)
            clientIdList.append(websocket.id.hex)
        printLog(clientMsg, type="INFOB", filePath="logs/all.log")
        cmdDict = json.loads(clientMsg)
        serverMsgList = gameManager.run(cmdDict, websocket.id.hex)
        print(clientIdList)
        for msg in serverMsgList:
            printLog(msg, type="INFOG", filePath="logs/all.log")
            for i in range(len(clientIdList)):
                if (msg["clientId"] == clientIdList[i]):
                    await clientList[i].send(msg["content"])

async def main(socketAddr, port):
    async with websockets.serve(handler, socketAddr, port):
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--testMode",       choices=["MANUAL", "REPLAY", "NONE"], default="NONE")
    parser.add_argument("--socketAddr",     default="127.0.0.1")
    parser.add_argument("--port",           default="50000")
    args = parser.parse_args()

    if args.testMode == "MANUAL":
        while 1:
            clientMsg = input()
            cmdDict = json.loads(clientMsg)
            msgList = gameManager.run(cmdDict, ('0', 0))
            for msg in msgList:
                printLog(msg, "INFOG")

    elif args.testMode == "REPLAY":
        logFile = open("logs/client.log", "r")
        for line in logFile:
            cmdDict = json.loads(line)
            printLog(line, "INFOB")
            msgList = gameManager.run(cmdDict, ('0', 0))
            for msg in msgList:
                printLog(msg, "INFOG")
        logFile.close()

    else:
        asyncio.run(main(args.socketAddr, args.port))