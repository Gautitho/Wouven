import argparse
import functions
import asyncio
import websockets
from GameManager import *

clientList      = []
clientIdList    = []
gameManager     = GameManager()

#class SimpleChat(WebSocket):
#
#    def handleMessage(self):
#        print(self.data)
#        testFile = open("cmd.log", "w")
#        testFile.write("plop")
#        testFile.close()
#        #printInfo(self.data + "\n", "INFOB", clientLogFile)
#        #printInfo(self.data + "\n", "INFOB", allLogFile)
#
#        cmdDict = json.loads(self.data)
#        msgList = gameManager.run(cmdDict, self.address)
#        for msg in msgList:
#            #log = str(msg)
#            #printInfo(log + "\n", "INFOG", allLogFile)
#            #allLogFile.write("Poof")
#            for i in range(0, len(clientIdList)):
#                if (msg["clientId"] == clientIdList[i]):
#                    clientList[i].sendMessage(msg["content"])
#       
#    def handleConnected(self):
#        print(self.address, 'connected')
#        #printInfo(self.address + ' connected', "MISC", "logs/all.log")
#        clientList.append(self)
#        clientIdList.append(self.address)
#
#    def handleClose(self):
#        clientList.remove(self)
#        clientIdList.remove(self.address)
#        gameManager.clientDisconnect(self.address)
#        print(self.address, 'closed')
#        #printInfo(self.address + ' closed', "MISC", "logs/all.log")

async def handler(websocket):
    while True:
        try:
            testFile = open("log", "w")
            testFile.write('anything')
            testFile.close()
            message = await websocket.recv()
            await websocket.send('{"cmd" : "ERROR", "msg" : "This is a test"}')
        except websockets.ConnectionClosedOK:
            break

async def main():
    async with websockets.serve(handler, "", 50000):
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())

#parser = argparse.ArgumentParser()
#parser.add_argument("--testMode",       choices=["MANUAL", "REPLAY", "NONE"], default="NONE")
#parser.add_argument("--socketAddr",     default="127.0.0.1")
#parser.add_argument("--port",           default="50000")
#args = parser.parse_args()
#
#if args.testMode == "MANUAL":
#    while 1:
#        clientMsg = input()
#        cmdDict = json.loads(clientMsg)
#        msgList = gameManager.run(cmdDict, ('0', 0))
#        for msg in msgList:
#            printInfo(msg, "INFOG")
#
#elif args.testMode == "REPLAY":
#    logFile = open("logs/client.log", "r")
#    for line in logFile:
#        cmdDict = json.loads(line)
#        printInfo(line, "INFOB")
#        msgList = gameManager.run(cmdDict, ('0', 0))
#        for msg in msgList:
#            printInfo(msg, "INFOG")
#    logFile.close()
#
#else:
#    allLogFile = open("logs/all.log", "w")
#    clientLogFile = open("logs/client.log", "w")
#    server = SimpleWebSocketServer(args.socketAddr, args.port, SimpleChat)
#    server.serveforever()
#    allLogFile.close()
#    clientLogFile.close()