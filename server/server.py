from simple_websocket_server import WebSocketServer, WebSocket
from Game import *

TEST_MODE   = False

clients     = []
game        = Game()

class SimpleChat(WebSocket):

    def handle(self):
        global game
        print(self.data)
        try:
            msgList = game.run(self.data)
            for msg in msgList:
                clients[msg["clientId"]].send_message(msg["content"])

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
        msgList = gameTest.run(clientMsg)
        for msg in msgList:
            printInfo(msg, "DEBUG")
else:
    server = WebSocketServer('127.0.0.1', 8000, SimpleChat)
    server.serve_forever()