import argparse
from simple_websocket_server import WebSocketServer, WebSocket
from GameManager import *

LOG_ENABLE  = True

clientList      = []
clientIdList    = []
gameManager     = GameManager()

class SimpleChat(WebSocket):

    def handle(self):
        print(self.data)
        if LOG_ENABLE:
            logFile.write(self.data + "\n")

        cmdDict = json.loads(self.data)
        msgList = gameManager.run(cmdDict, self.address)
        for msg in msgList:
            for i in range(0, len(clientIdList)):
                if (msg["clientId"] == clientIdList[i]):
                    clientList[i].send_message(msg["content"])
       
    def connected(self):
        print(self.address, 'connected')
        clientList.append(self)
        clientIdList.append(self.address)

    def handle_close(self):
        clientList.remove(self)
        clientIdList.remove(self.address)
        gameManager.clientDisconnect(self.address)
        print(self.address, 'closed')

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
            printInfo(msg, "INFOB")

elif args.testMode == "REPLAY":
    logFile = open("cmd.log", "r")
    for line in logFile:
        cmdDict = json.loads(line)
        printInfo(line, "INFOG")
        msgList = gameManager.run(cmdDict, ('0', 0))
        for msg in msgList:
            printInfo(msg, "INFOB")

else:
    if LOG_ENABLE:
        logFile = open("cmd.log", "w")
    server = WebSocketServer(args.socketAddr, args.port, SimpleChat)
    server.serve_forever()
    if LOG_ENABLE:
        logFile.close()