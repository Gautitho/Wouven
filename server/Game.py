import json
import random
import copy
import time
from functions import *
from Board import *
from GameException import *

deck1       = {"heroDescId" : "he4", "spellDescIdList" : ["she2", "se40", "se5", "se26", "se4", "se23", "se21", "sc10", "ss49"], "companionDescIdList" : ["ca5", "cw8", "cm0", "cm4"]}
deck2       = {"heroDescId" : "hs3", "spellDescIdList" : ["shs3", "ss42", "ss43", "ss24", "ss35", "si1", "si1", "sc10", "ss44"], "companionDescIdList" : ["cf13", "cw11", "ce14", "cm4"]}

class Game:

    def __init__(self, name):
        self._name              = name
        # List of game states : MATCHMAKING, RUNNING, DONE
        self._gameState         = "MATCHMAKING"
        self._board             = Board()
        self._serverCmdList     = []
        self._actionList        = []
        self._connectedPlayers  = 0
        self._inactiveStartTime = 0

    @property
    def name(self):
        return self._name

    @property
    def gameState(self):
        return self._gameState

    @property
    def turn(self):
        return self._board.turn

    @property
    def board(self):
        return copy.deepcopy(self._board)

    @property
    def playerIdList(self):
        return list(self._board.playersDict.keys())

    @property
    def serverCmdList(self):
        return list(self._serverCmdList)

    @property
    def actionList(self):
        return list(self._actionList)

    @property
    def connectedPlayers(self):
        return self._connectedPlayers

    @property
    def inactiveStartTime(self):
        return self._inactiveStartTime

    def checkInactiveGameErase(self):
        if (self._inactiveStartTime == 0 and self._connectedPlayers < 2):
            self._inactiveStartTime = time.time()
        elif (self._connectedPlayers == 2):
            self._inactiveStartTime = 0

        if (self._inactiveStartTime > 0 and time.time() - self._inactiveStartTime > INACTIVE_GAME_ERASE_TIME):
            return True
        elif (self._gameState != "RUNNING"):
            return True
        else:
            return False

    def checkCmdArgs(self, cmdDict, keyList):
        for key in keyList:
            if not(key in cmdDict):
                raise GameException(f"No {key} field in command")

    def clientConnect(self):
        self._connectedPlayers += 1

    def clientDisconnect(self):
        self._connectedPlayers -= 1

    def run(self, cmdDict):
        cmd         = cmdDict["cmd"]
        playerId    = cmdDict["playerId"]
        self._serverCmdList = []

        if (self._gameState == "MATCHMAKING"):
            if (len(self._board.playersDict) == 2):
                self.launchGame()

        else:
            if (cmd == "GET_INIT"):
                self.initGame(playerId)
                self.sendStatus()

            elif (cmd == "SURREND"):
                self.Surrend(playerId)

            elif (cmd in ["ENDTURN", "MOVE", "SPELL", "SUMMON", "USE_RESERVE"]):
                self.checkTurn(playerId)
                if (cmd == "ENDTURN"):
                    self.EndTurn(playerId)

                elif (cmd == "MOVE"):
                    self.checkCmdArgs(cmdDict, ["entityId", "path"])
                    self.addActionToList("move", self._board.playersDict[playerId].team, self._board.entitiesDict[int(cmdDict["entityId"])].descId, [cmdDict["path"][-1]])
                    self.Move(playerId, int(cmdDict["entityId"]), cmdDict["path"])

                elif (cmd == "SPELL"):
                    self.checkCmdArgs(cmdDict, ["spellIdx", "targetPositionList"])
                    self.addActionToList("spellCast", self._board.playersDict[playerId].team, self._board.playersDict[playerId].handSpellDict[list(self._board.playersDict[playerId].handSpellDict.keys())[int(cmdDict["spellIdx"])]].descId, cmdDict["targetPositionList"])
                    self.SpellCast(playerId, int(cmdDict["spellIdx"]), cmdDict["targetPositionList"])

                elif (cmd == "SUMMON"):
                    self.checkCmdArgs(cmdDict, ["companionId", "summonPositionList"])
                    self.addActionToList("summon", self._board.playersDict[playerId].team, db.companions[self._board.playersDict[playerId].companionList[int(cmdDict["companionId"])]["descId"]]["entityDescId"], cmdDict["summonPositionList"])
                    self.Summon(playerId, int(cmdDict["companionId"]), cmdDict["summonPositionList"])

                elif (cmd == "USE_RESERVE"):
                    self.addActionToList("useReserve", self._board.playersDict[playerId].team, None, [])
                    self.UseReserve(playerId)


                self._board.always()
                self.sendStatus()
                self.sendActionList()

        return self._serverCmdList

    def launchGame(self):
        self._gameState     = "RUNNING"
        serverCmd           = {}
        serverCmd["cmd"]    = "GAME_START"
        serverCmd["name"]   = self._name
        
        firstPlayerId       = None
        firstPlayerWeight   = 1000
        for playerId in list(self._board.playersDict.keys()): # TODO : If egal it is not random
            if (self._board.playersDict[playerId].deckWeight < firstPlayerWeight):
                firstPlayerId       = playerId
                firstPlayerWeight   = self._board.playersDict[playerId].deckWeight

        for playerId in list(self._board.playersDict.keys()):
            if (playerId == firstPlayerId):
                self._board.playersDict[playerId].draw(5)
                self._board.startTurn(playerId)
            else:
                self._board.playersDict[playerId].modifyPaStock(1)
                self._board.playersDict[playerId].draw(6)
            self._serverCmdList.append({"playerId" : playerId, "content" : json.dumps(serverCmd)})

    def initGame(self, playerId):
        serverCmd           = {}
        serverCmd["cmd"]    = "INIT"
        serverCmd["team"]   = self._board.playersDict[playerId].team
        self._serverCmdList.append({"playerId" : playerId, "content" : json.dumps(serverCmd)})

    def sendStatus(self):
        for playerId in list(self._board.playersDict.keys()):
            serverCmd = {}
            serverCmd["cmd"]    = "STATUS"
            serverCmd["turn"]   = self._board.turn
            for playerIdA in list(self._board.playersDict.keys()):
                if playerId == playerIdA:
                    serverCmd["myPlayer"]   = self._board.playersDict[playerIdA].getMyStatusDict()
                else:
                    serverCmd["opPlayer"]   = self._board.playersDict[playerIdA].getOpStatusDict()
            entitiesDict    = {}
            for entityId in list(self._board.entitiesDict.keys()):
                entitiesDict[entityId] = self._board.entitiesDict[entityId].getStatusDict()
            serverCmd["entitiesDict"] = entitiesDict
            self._serverCmdList.append({"playerId" : playerId, "content" : json.dumps(serverCmd)})

        # Check for end of the game
        deadPlayerIdList = []
        for playerId in list(self._board.playersDict.keys()):
            if not(self._board.playersDict[playerId].heroEntityId in self._board.entitiesDict):
               deadPlayerIdList.append(playerId)
        if deadPlayerIdList:
            self._gameState     = "DONE"
            for playerId in list(self._board.playersDict.keys()):
                serverCmd = {}
                serverCmd["cmd"]    = "END_GAME"
                if (len(deadPlayerIdList) == 1):
                    if (playerId == deadPlayerIdList[0]):
                        serverCmd["result"] = "LOSS"
                    else:
                        serverCmd["result"] = "WIN"
                else:
                    serverCmd["result"] = "DRAW"
                self._serverCmdList.append({"playerId" : playerId, "content" : json.dumps(serverCmd)})

    def addActionToList(self, actionType, sourceTeam, sourceDescId, targetPositionList):
        action              = {}
        action["type"]      = actionType
        if (actionType == "move"):            
            action["source"]    = {"spritePath" : db.entities[sourceDescId]["spritePath"], "descSpritePath" : db.entities[sourceDescId]["descSpritePath"], "team" : sourceTeam}
        elif (actionType == "spellCast"):
            action["source"]    = {"spritePath" : db.spells[sourceDescId]["spritePath"], "descSpritePath" : db.spells[sourceDescId]["descSpritePath"], "team" : sourceTeam}
        elif (actionType == "summon"):
            action["source"]    = {"spritePath" : db.entities[sourceDescId]["spritePath"], "descSpritePath" : db.entities[sourceDescId]["descSpritePath"], "team" : sourceTeam}
        else:
            action["source"]    = {"spritePath" : "", "team" : sourceTeam}
        targetList          = []
        if targetPositionList:
            for position in targetPositionList:
                entityId = self._board.entityIdOnTile(position["x"], position["y"])
                if (entityId != None):
                    targetList.append({"spritePath" : db.entities[self._board.entitiesDict[entityId].descId]["spritePath"], "descSpritePath" : db.entities[self._board.entitiesDict[entityId].descId]["descSpritePath"],"team" : self._board.entitiesDict[entityId].team})
        action["targetList"] = copy.deepcopy(targetList)

        self._actionList.insert(0, dict(action))
        if (len(self._actionList) == ACTION_LIST_LEN + 1):
            self._actionList.pop(-1)

    def sendActionList(self):
        for playerId in list(self._board.playersDict.keys()):
            serverCmd = {}
            serverCmd["cmd"]        = "HISTORIC"
            serverCmd["actionList"] = self._actionList
            self._serverCmdList.append({"playerId" : playerId, "content" : json.dumps(serverCmd)})

    def checkTurn(self, playerId):
        if not(playerId in list(self._board.playersDict.keys())):
            raise GameException(f"PlayerId ({playerId}) not recognized !")
        elif (self._board.playersDict[playerId].team != self._board.turn):
            raise GameException("Not your turn !")

    def getOpPlayerId(self, playerId):
        for pId in list(self._board.playersDict.keys()):
            if (pId != playerId):
                return pId

    def appendPlayer(self, playerId, deck):
        if (len(self._board.playersDict) == 0):
            if TEST_ENABLE:
                self._board.appendPlayer(playerId, deck1, "blue", playerId)
            else:
                self._board.appendPlayer(playerId, deck, "blue", playerId)
        elif (len(self._board.playersDict) == 1):
            if TEST_ENABLE:
                self._board.appendPlayer(playerId, deck2, "red", playerId)
            else:
                self._board.appendPlayer(playerId, deck, "red", playerId)
        else:
            raise GameException(f"2 players already in the game {self._name} !")

    def EndTurn(self, playerId):
        self._board.endTurn(playerId)
        self._board.startTurn(self.getOpPlayerId(playerId))

    def Move(self, playerId, entityId, path):
        self._board.moveEntity(playerId, entityId, path)

    def SpellCast(self, playerId, spellIdx, targetPositionList):
        self._board.spellCast(playerId, spellIdx, targetPositionList)

    def Summon(self, playerId, companionId, summonPositionList):
        self._board.summon(playerId, companionId, summonPositionList)
    
    def UseReserve(self, playerId):
        self._board.useReserve(playerId)

    def Surrend(self, playerId):
        self._gameState     = "DONE"
        for playerIdIt in list(self._board.playersDict.keys()):
            serverCmd = {}
            serverCmd["cmd"]    = "END_GAME"
            if (playerIdIt == playerId):
                serverCmd["result"] = "LOSS_SURRENDER"
            else:
                serverCmd["result"] = "WIN_SURRENDER"
            self._serverCmdList.append({"playerId" : playerIdIt, "content" : json.dumps(serverCmd)})       

    def generalLog(self):
        s = ""
        s += self._name + " : "
        s += "Game state = " + self._gameState + " / "
        s += "Connected players = " + str(self._connectedPlayers) + " / "
        s += "Turn = " + self._board.turn + " / "
        s += "Player Ids : "
        for playerId in list(self._board.playersDict.keys()):
            s += playerId + " | "
        s = s[:-3] + " / Inactive time start = " + time.strftime('%Y_%m_%d_%H_%M_%S', time.localtime(self._inactiveStartTime))
        return s

    def entityListLog(self):
        s = ""
        for entityId in list(self._board.entitiesDict.keys()):
            s += str(entityId) + " :\n"
            s += self._board.entitiesDict[entityId].toString() + "\n"
        s = s[:-1]
        return s

    def playerListLog(self):
        s = ""
        for playerId in list(self._board.playersDict.keys()):
            s += str(playerId) + " :\n"
            s += self._board.playersDict[playerId].toString() + "\n"
        s = s[:-1]
        return s