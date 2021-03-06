import argparse
import os
import shutil
import pathlib
from datetime import datetime
from simple_websocket_server import WebSocketServer, WebSocket
from GameManager import *
from functions import *

DEFAULT_REPLAY_FILE_PATH = "logs/client.log" if (LOCAL_ENABLE or len(os.listdir("logs")) < 1) else "logs/lastLogDir/client.log"

clientList      = []
clientIdList    = []
gameManager     = GameManager()

class SimpleChat(WebSocket):

    def handle(self):
        printLog(str(self.address) + " : " + toString(self.data), type="INFOG", filePath="all.log")
        printLog(self.data, filePath="client.log")
        if LOCAL_ENABLE:
            clientLog.write(self.data + "\n")
        printLog(toString(clientIdList, separator="\n"), filePath="clientList.log", writeMode="w")

        cmdDict = json.loads(self.data)
        msgList = gameManager.run(cmdDict, self.address)
        for msg in msgList:
            printLog(msg, type="INFOB", filePath="all.log")
            printLog(msg, filePath="server.log")
            for i in range(0, len(clientIdList)):
                if (msg["clientId"] == clientIdList[i]):
                    clientList[i].send_message(msg["content"])
       
    def connected(self):
        printLog(str(self.address) + ' connected', type="INFO", filePath="all.log")
        clientList.append(self)
        clientIdList.append(self.address)
        printLog(toString(clientIdList, separator="\n"), filePath="clientList.log", writeMode="w")

    def handle_close(self):
        clientList.remove(self)
        clientIdList.remove(self.address)
        gameManager.clientDisconnect(self.address)
        printLog(str(self.address) + ' closed', type="INFO", filePath="all.log")
        printLog(toString(clientIdList, separator="\n"), filePath="clientList.log", writeMode="w")

parser = argparse.ArgumentParser()
parser.add_argument("--testMode",       choices=["MANUAL", "REPLAY", "NONE"], default="NONE")
parser.add_argument("--socketAddr",     default="127.0.0.1")
parser.add_argument("--port",           default="50000")
parser.add_argument("--replayFilePath", default=DEFAULT_REPLAY_FILE_PATH)
args = parser.parse_args()

# Preparing logging repository
if not(os.path.isdir("logs")):
    os.mkdir("logs")
if not(LOCAL_ENABLE):
    if (args.testMode == "NONE"):
        logDir = "logs/lastLogDir" # Used in functions
        if os.path.isdir(logDir):
            if not(os.path.exists(logDir + "/info.log")): 
                printLog("File info.log not found in previous logDir, directory removed !", type="WARNING")
            else:
                infoFile = open(logDir + "/info.log", "r")
                date = infoFile.read()
                infoFile.close()
                os.rename(logDir, "logs/" + date)
        os.mkdir(logDir)
        infoFile = open(logDir + "/info.log", "w")
        infoFile.write(datetime.now().strftime('%Y_%m_%d_%H_%M_%S'))
        infoFile.close()
    else:
        logDir = "logs/debugLogDir" # Used in functions
        if os.path.exists(logDir):
            shutil.rmtree(logDir)
        os.mkdir(logDir)
    setLogDir(logDir)


if args.testMode == "MANUAL":
    while 1:
        clientMsg = input()
        cmdDict = json.loads(clientMsg)
        msgList = gameManager.run(cmdDict, ('0', 0))
        for msg in msgList:
            printLog(msg, type="INFOB", filePath="all.log")

elif args.testMode == "REPLAY":
    logFile = open(args.replayFilePath, "r")
    for line in logFile:
        cmdDict = json.loads(line)
        printLog(line, type="INFOG", filePath="all.log")
        msgList = gameManager.run(cmdDict, ('0', 0))
        for msg in msgList:
            printLog(msg, type="INFOB", filePath="all.log")

else:
    if LOCAL_ENABLE:
        clientLog = open("logs/client.log", "w")
    server = WebSocketServer(args.socketAddr, args.port, SimpleChat)
    server.serve_forever()
    if LOCAL_ENABLE:
        clientLog.close()