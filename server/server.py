import copy
from simple_websocket_server import WebSocketServer, WebSocket
from Game import *

# Test modes available : NONE, MANUAL, LOG_FILE
TEST_MODE   = "LOG_FILE"
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

if TEST_MODE == "MANUAL":
    gameTest = Game()
    while 1:
        clientMsg = input()
        cmdDict = json.loads(clientMsg)
        msgList = gameTest.run(cmdDict)
        for msg in msgList:
            printInfo(msg, "DEBUG")
elif TEST_MODE == "LOG_FILE":
    gameTest = Game()
    logFile = open("cmd.log", "r")
    for line in logFile:
        clientMsg = line
        cmdDict = json.loads(clientMsg)
        msgList = gameTest.run(cmdDict)
        for msg in msgList:
            printInfo(msg, "DEBUG")
else:
    if LOG_ENABLE:
        logFile = open("cmd.log", "w")
    server = WebSocketServer('127.0.0.1', 8000, SimpleChat)
    server.serve_forever()
    if LOG_ENABLE:
        logFile.close()