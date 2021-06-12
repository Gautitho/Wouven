from simple_websocket_server import WebSocketServer, WebSocket
from Game import *

TEST_MODE   = False

clients     = []
game        = Game()

class SimpleChat(WebSocket):

    def handle(self):
        global game
        print(self.data)
        cmdDict = json.loads(self.data)
        try:
            msgList = game.run(cmdDict)
            for msg in msgList:
                clients[msg["clientId"]].send_message(msg["content"])

        except GameException as ge:
            if ("playerId" in cmdDict):
                if (cmdDict["playerId"] in game.clientIds):
                    clients[game.clientIds[cmdDict["playerId"]]].send_message('{"cmd" : "ERROR", "msg" : "' + ge.errorMsg + '"}')
                else:
                    for client in clients:
                        client.send_message('{"cmd" : "ERROR", "msg" : "Wrong playerId !"}')
            else:
                for client in clients:
                    client.send_message('{"cmd" : "ERROR", "msg" : "No playerId in cmd !"}')

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

if TEST_MODE:
    gameTest = Game()
    while 1:
        clientMsg = input()
        cmdDict = json.loads(clientMsg)
        msgList = gameTest.run(cmdDict)
        for msg in msgList:
            printInfo(msg, "DEBUG")
else:
    server = WebSocketServer('127.0.0.1', 8000, SimpleChat)
    server.serve_forever()