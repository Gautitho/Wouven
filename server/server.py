import copy
import argparse
from simple_websocket_server import WebSocketServer, WebSocket
from Game import *

LOG_ENABLE  = True

clients     = []
nextGame    = Game()
currGame    = Game()

class SimpleChat(WebSocket):

    def handle(self):
        global nextGame
        global currGame
        print(self.data)
        if LOG_ENABLE:
            logFile.write(self.data + "\n")

        cmdDict = json.loads(self.data)
        try:
            msgList = nextGame.run(cmdDict)
            for msg in msgList:
                clients[msg["clientId"]].send_message(msg["content"])
            currGame = copy.deepcopy(nextGame)

        except GameException as ge:
            if ("playerId" in cmdDict):
                if (cmdDict["playerId"] in nextGame.clientIds):
                    clients[nextGame.clientIds[cmdDict["playerId"]]].send_message('{"cmd" : "ERROR", "msg" : "' + ge.errorMsg + '"}')
                else:
                    for client in clients:
                        client.send_message('{"cmd" : "ERROR", "msg" : "Wrong playerId !"}')
            else:
                for client in clients:
                    client.send_message('{"cmd" : "ERROR", "msg" : "No playerId in cmd !"}')
            nextGame = copy.deepcopy(currGame) # Restore a stable game

        except Exception as e:
            print("Exception : " + str(e))
       
    def connected(self):
        print(self.address, 'connected')
        clients.append(self)
        for client in clients:
            client.send_message('{"cmd" : "AUTH", "msg" : "' + self.address[0] + ' - connected"}')

    def handle_close(self):
        clients.remove(self)
        print(self.address, 'closed')
        for client in clients:
            client.send_message('{"cmd" : "AUTH", "msg" : "' + self.address[0] + ' - disconnected"}')

parser = argparse.ArgumentParser()
parser.add_argument("--testMode",       choices=["MANUAL", "REPLAY", "NONE"], default="NONE")
parser.add_argument("--socketAddr",     default="127.0.0.1")
args = parser.parse_args()

if args.testMode == "MANUAL":
    gameTest = Game()
    while 1:
        clientMsg = input()
        cmdDict = json.loads(clientMsg)
        msgList = gameTest.run(cmdDict)
        for msg in msgList:
            printInfo(msg, "DEBUG")

elif args.testMode == "REPLAY":
    logFile = open("cmd.log", "r")
    for line in logFile:
        cmdDict = json.loads(line)
        printInfo(line, "INFOG")
        try:
            msgList = nextGame.run(cmdDict)
            currGame = copy.deepcopy(nextGame)
        except GameException as ge:
            if ("playerId" in cmdDict):
                if (cmdDict["playerId"] in nextGame.clientIds):
                    msgList.append('{"cmd" : "ERROR", "msg" : "' + ge.errorMsg + '"}')
                else:
                    msgList.append('{"cmd" : "ERROR", "msg" : "Wrong playerId !"}')
            else:
                msgList.append('{"cmd" : "ERROR", "msg" : "No playerId in cmd !"}')
            nextGame = copy.deepcopy(currGame) # Restore a stable game
        finally:
            for msg in msgList:
                printInfo(msg, "INFOB")

else:
    if LOG_ENABLE:
        logFile = open("cmd.log", "w")
    server = WebSocketServer(args.socketAddr, 50000, SimpleChat)
    server.serve_forever()
    if LOG_ENABLE:
        logFile.close()