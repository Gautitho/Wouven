import json
from functions import *
from Board import *

deck1       = {"heroDescId" : "h1", "spells" : ["1", "2", "3", "4", "5", "6", "7", "7", "4"], "companions" : ["c1", "c2", "c3", "c4"]}
deck2       = {"heroDescId" : "h2", "spells" : ["1", "2", "3", "4", "5", "6", "7", "7", "4"], "companions" : ["c1", "c2", "c3", "c4"]}

class Game:

    def __init__(self):
        # List of game states : MATCHMAKING, RUNNING
        self._gameState = "MATCHMAKING"
        self._turn      = "blue"
        self._board     = Board()
        self._clientIds = {}
        self._msgList   = []

    def run(self, clientMsg):
        cmdDict = json.loads(clientMsg)
        if "cmd" in cmdDict:
            cmd = cmdDict["cmd"]
        else:
            for clientId in self._clientIds:
               self._msgList.append({"clientId" : self._clientIds[clientId], "content" : json.dumps({"cmd" : "ERROR", "msg" : "No cmd field in command"})})

        self._msgList = []

        if (self._gameState == "MATCHMAKING"):

            if (cmd == "AUTH"):
                if self.checkCmdArgs(cmdDict, ["playerId"]):
                    self.Auth(cmdDict["playerId"])

            if (len(self._board.players) == 2):
                self.launchGame()
                self.sendStatus()

        else:

            if (cmd == "ENDTURN"):
                if self.checkCmdArgs(cmdDict, ["playerId"]):
                    self.EndTurn(cmdDict["playerId"])

            elif (cmd == "MOVE"):
                if self.checkCmdArgs(cmdDict, ["playerId", "entityId", "path"]):
                    self.Move(cmdDict["playerId"], cmdDict["entityId"], cmdDict["path"])

            self.sendStatus()

        return self._msgList

    def launchGame(self):
        self._gameState = "RUNNING"
        initCmd = {}
        initCmd["cmd"]      = "INIT"
        
        for playerId in self._board.players:
            initCmd["team"]     = self._board.players[playerId].team
            self._msgList.append({"clientId" : self._clientIds[playerId], "content" : json.dumps(initCmd)})

    def sendStatus(self):
        for clientId in self._clientIds:
            statusCmd = {}
            statusCmd["cmd"]    = "STATUS"
            statusCmd["turn"]   = self._turn
            for playerId in self._board.players:
                if clientId == playerId:
                    statusCmd["myPlayer"]   = self._board.players[playerId].getMyStatusDict()
                else:
                    statusCmd["opPlayer"]   = self._board.players[playerId].getOpStatusDict()
            entitiesList    = []
            for entityIdx in range(0, len(self._board.entities)):
                entitiesList.append(self._board.entities[entityIdx].getStatusDict())
            statusCmd["entitiesList"] = entitiesList
            self._msgList.append({"clientId" : self._clientIds[clientId], "content" : json.dumps(statusCmd)})

    def checkCmdArgs(self, cmdDict, keyList):
        retVal = True
        for key in keyList:
            if not(key in cmdDict):
                retVal = False
                for clientId in self._clientIds:
                   self._msgList.append({"clientId" : self._clientIds[clientId], "content" : json.dumps({"cmd" : "ERROR", "msg" : f"Missing [{key}] in command arguments !"})})
        return retVal

    def checkTurn(self, playerId):
        if not(playerId in self._board.players):
            for clientId in self._clientIds:
                self._msgList.append({"clientId" : self._clientIds[clientId], "content" : json.dumps({"cmd" : "ERROR", "msg" : f"PlayerId ({playerId}) not recognized !"})})
            return False
        elif (self._board.players[playerId].team != self._turn):
            self._msgList.append({"clientId" : self._clientIds[playerId], "content" : json.dumps({"cmd" : "ERROR", "msg" : "Not your turn !"})})
            return False
        else:
            return True

    def Auth(self, playerId):
        if (len(self._board.players) == 0):
            self._board.appendPlayer(playerId, deck1, "blue", "1")
            self._clientIds[playerId]   = 0
        elif (len(self._board.players) == 1):
            self._board.appendPlayer(playerId, deck2, "red", "2")
            self._clientIds[playerId]   = 1
        else:
            self._msgList.append({"clientId" : 0, "content" : json.dumps({"cmd" : "ERROR", "msg" : "2 players already in the game !"})})
            self._msgList.append({"clientId" : 1, "content" : json.dumps({"cmd" : "ERROR", "msg" : "2 players already in the game !"})})

    def EndTurn(self, playerId):
        if (self.checkTurn(playerId)):
            self._turn = "blue" if self._turn == "red" else "red"
            for entityId in self._board.players[playerId].boardEntityIds:
                self._board.entities[entityId].newTurn()

    def Move(self, playerId, entityId, path):
        if (self.checkTurn(playerId)):
            errorMsg = self._board.entities[entityId].move(self._board, path)
            print(errorMsg)
