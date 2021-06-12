import json
import random
from functions import *
from Board import *
from GameException import *

deck1       = {"heroDescId" : "h1", "spells" : ["s1", "s2", "s3", "s4", "s5", "s6", "s7", "s7", "s4"], "companions" : ["c1", "c2", "c3", "c4"]}
deck2       = {"heroDescId" : "h2", "spells" : ["s1", "s2", "s3", "s4", "s5", "s6", "s7", "s7", "s4"], "companions" : ["c1", "c2", "c3", "c4"]}

class Game:

    def __init__(self):
        # List of game states : MATCHMAKING, RUNNING
        self._gameState = "MATCHMAKING"
        self._turn      = "blue"
        self._board     = Board()
        self._clientIds = {}
        self._msgList   = []

    @property
    def clientIds(self):
        return dict(self._clientIds)

    def run(self, cmdDict):
        if "cmd" in cmdDict:
            cmd = cmdDict["cmd"]
        else:
            raise GameException("No 'cmd' field in command")
        if "playerId" in cmdDict:
            playerId = cmdDict["playerId"]
        else:
            raise GameException("No 'playerId' field in command")

        self._msgList = []

        if (self._gameState == "MATCHMAKING"):

            if (cmd == "AUTH"):
                self.Auth(cmdDict["playerId"])

            if (len(self._board.players) == 2):
                self.launchGame()
                self.sendStatus()

        else:

            self.checkTurn(playerId)
            if (cmd == "ENDTURN"):
                self.EndTurn(playerId)

            elif (cmd == "MOVE"):
                self.checkCmdArgs(cmdDict, ["entityId", "path"])
                self.Move(cmdDict["entityId"], cmdDict["path"])

            elif (cmd == "SPELL"):
                self.checkCmdArgs(cmdDict, ["spellId", "targetPositionList"])
                self.SpellCast(playerId, cmdDict["spellId"], cmdDict["targetPositionList"])

            self.sendStatus()

        return self._msgList

    def launchGame(self):
        self._gameState = "RUNNING"
        initCmd         = {}
        initCmd["cmd"]  = "INIT"

        firstPlayerId = random.choice(list(self._board.players.keys()))

        for playerId in self._board.players:
            if (playerId == firstPlayerId):
                self._turn = self._board.players[playerId].team
                for i in range(0, 5):
                    self._board.players[playerId].draw()
            else:
                self._board.players[playerId].modifyPaStock(1)
                for i in range(0, 6):
                    self._board.players[playerId].draw()
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
        for key in keyList:
            if not(key in cmdDict):
                raise GameException("No cmd field in command")

    def checkTurn(self, playerId):
        if not(playerId in self._board.players):
            raise GameException(f"PlayerId ({playerId}) not recognized !")
        elif (self._board.players[playerId].team != self._turn):
            raise GameException("Not your turn !")

    def getOpPlayerId(self, playerId):
        for pId in list(self._clientIds.keys()):
            if (pId != playerId):
                return pId

    def Auth(self, playerId):
        if (len(self._board.players) == 0):
            self._board.appendPlayer(playerId, deck1, "blue", "1")
            self._clientIds[playerId]   = 0
        elif (len(self._board.players) == 1):
            self._board.appendPlayer(playerId, deck2, "red", "2")
            self._clientIds[playerId]   = 1
        else:
            raise GameException("2 players already in the game !")

    def EndTurn(self, playerId):
        self._turn = "blue" if self._turn == "red" else "red"
        self._board.endTurn(playerId)
        self._board.startTurn(self.getOpPlayerId(playerId))

    def Move(self, entityId, path):
        self._board.moveEntity(entityId, path)

    def SpellCast(self, playerId, spellId, targetPositionList):
        self._board.spellCast(playerId, spellId, targetPositionList)