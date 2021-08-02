import json
import random
import copy
from functions import *
from Board import *
from GameException import *

deck1       = {"heroDescId" : "kasai", "spells" : ["bloodySword", "blame", "burn", "fulgur", "explosiveCharge", "leap", "spinning", "massage", "inspiration"], "companions" : ["elely", "shutter", "championneSanglante", "seraphin"]}
deck2       = {"heroDescId" : "kasai", "spells" : ["bloodySword", "blame", "burn", "fulgur", "explosiveCharge", "leap", "spinning", "massage", "inspiration"], "companions" : ["elely", "shutter", "championneSanglante", "seraphin"]}

class Game:

    def __init__(self):
        # List of game states : MATCHMAKING, RUNNING
        self._gameState = "MATCHMAKING"
        self._turn      = "blue"
        self._board     = Board()
        self._clientIds = {}
        self._msgList   = []

    @property
    def gameState(self):
        return dict(self._gameState)

    @property
    def turn(self):
        return dict(self._turn)

    @property
    def board(self):
        return copy.copy(self._board)

    @property
    def clientIds(self):
        return dict(self._clientIds)

    @property
    def msgList(self):
        return list(self._msgList)

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
                self.Move(playerId, int(cmdDict["entityId"]), cmdDict["path"])

            elif (cmd == "SPELL"):
                self.checkCmdArgs(cmdDict, ["spellId", "targetPositionList"])
                self.SpellCast(playerId, int(cmdDict["spellId"]), cmdDict["targetPositionList"])

            elif (cmd == "SUMMON"):
                self.checkCmdArgs(cmdDict, ["companionId", "summonPositionList"])
                self.Summon(playerId, int(cmdDict["companionId"]), cmdDict["summonPositionList"])

            elif (cmd == "USE_RESERVE"):
                self.UseReserve(playerId)

            self._board.always()
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
            entitiesDict    = {}
            for entityId in list(self._board.entities.keys()):
                entitiesDict[entityId] = self._board.entities[entityId].getStatusDict()
            statusCmd["entitiesDict"] = entitiesDict
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

    def Move(self, playerId, entityId, path):
        self._board.moveEntity(playerId, entityId, path)

    def SpellCast(self, playerId, spellId, targetPositionList):
        self._board.spellCast(playerId, spellId, targetPositionList)

    def Summon(self, playerId, companionId, summonPositionList):
        self._board.summon(playerId, companionId, summonPositionList)
    
    def UseReserve(self, playerId):
        self._board.useReserve(playerId)