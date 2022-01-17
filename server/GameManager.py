import copy
import json
import traceback
from Game import *
from GameException import *

class GameManager :

    def __init__(self):
        self._serverCmdList     = []
        self._currGameList      = []
        self._nextGameList      = []
        self._nextGameId        = 0
        self._gameIdList        = []
        self._knownPlayerIdDict = {} # {playerId : clientId}
        self._gameIdx           = None
        self._waitingPlayer     = {} # {playerId / deck}

    def checkCmdArgs(self, cmdDict, keyList):
        for key in keyList:
            if not(key in cmdDict):
                raise GameException(f"No {key} field in command")

    def getClientGame(self, clientId):
        playerId = None
        for playerIdA in list(self._knownPlayerIdDict.keys()):
            if (self._knownPlayerIdDict[playerIdA] == clientId):
                playerId = playerIdA
                break
        if (playerId == None):
            return None
        for i in range(0, len(self._currGameList)):
            for playerIdB in self._currGameList[i].playerIdList:
                if (playerId == playerIdB):
                    return i
        return None

    def clientDisconnect(self, clientId):
        for playerId in list(self._knownPlayerIdDict.keys()):
            if (self._knownPlayerIdDict[playerId] == clientId):
                playerDisconnected = playerId
                self._knownPlayerIdDict[playerId] == None
                break
        
        for game in self._currGameList:
            for playerId in game.playerIdList:
                if (playerId == playerDisconnected):
                    game.clientDisconnect()

    def run(self, cmdDict, clientId):
        self._serverCmdList = []
        try:
            self.garbageCollector()
            self.checkCmdArgs(cmdDict, ["cmd", "playerId"])
            clientCmd   = cmdDict["cmd"]
            playerId    = cmdDict["playerId"]

            if (clientCmd == "CREATE_GAME"):
                self.checkCmdArgs(cmdDict, ["gameName", "deck"])
                self.CreateGame(clientId, cmdDict["gameName"], playerId, cmdDict["deck"])
            elif (clientCmd == "JOIN_GAME"):
                self.checkCmdArgs(cmdDict, ["gameName", "deck"])
                self.JoinGame(clientId, cmdDict["gameName"], playerId, cmdDict["deck"])
            elif (clientCmd == "RECONNECT"):
                self.checkCmdArgs(cmdDict, ["gameName"])
                self.Reconnect(clientId, cmdDict["gameName"], playerId)
            elif (clientCmd == "FIND_GAME"):
                self.checkCmdArgs(cmdDict, ["deck"])
                self.FindGame(clientId, playerId, cmdDict["deck"])
            elif (clientCmd == "CANCEL_FIND_GAME"):
                self.checkCmdArgs(cmdDict, [])
                self.CancelFindGame(clientId, playerId)

            self._gameIdx = self.getClientGame(clientId)

            if (self._gameIdx != None):
                gameCmdList = self._nextGameList[self._gameIdx].run(cmdDict)
                for gameCmd in gameCmdList:
                    self._serverCmdList.append({"clientId" : self._knownPlayerIdDict[gameCmd["playerId"]], "content" : gameCmd["content"]})
                self._currGameList[self._gameIdx] = copy.deepcopy(self._nextGameList[self._gameIdx])

        except GameException as ge:
            serverCmd = {"cmd" : "ERROR", "msg" : ge.errorMsg}
            self._serverCmdList.append({"clientId" : clientId, "content" : json.dumps(serverCmd)})
            if (self._currGameList and self._currGameList[self._gameIdx]):
                self._nextGameList[self._gameIdx] = copy.deepcopy(self._currGameList[self._gameIdx]) # Restore a stable game

        except Exception as e:
            print(traceback.format_exc())
            print("Exception : " + str(e))

        return self._serverCmdList

    def garbageCollector(self):
        gameToEraseIdList = []
        for gameIdx in range(0, len(self._currGameList)):
            if self._currGameList[gameIdx].checkInactiveGameErase():
                gameToEraseIdList.append(gameIdx)
        gameToEraseIdList.reverse()
        for gameIdx in gameToEraseIdList:
            del self._currGameList[gameIdx]
            del self._nextGameList[gameIdx]

    def CreateGame(self, clientId, gameName, playerId, deck):
        if (playerId in list(self._knownPlayerIdDict.keys())):
            raise GameException(f"Player {playerId} is already in a game")

        self._nextGameList.append(Game(gameName))
        self._gameIdList.append(self._nextGameId)
        self._gameIdx = self._nextGameId
        self._nextGameList[self._gameIdx].appendPlayer(playerId, deck)
        self._nextGameList[self._gameIdx].clientConnect()
        self._nextGameId += 1
        self._currGameList.append(copy.deepcopy(self._nextGameList[self._gameIdx]))
        self._knownPlayerIdDict[playerId] = clientId
        serverCmd = {"cmd" : "WAIT_GAME_START"}
        self._serverCmdList.append({"clientId" : clientId, "content" : json.dumps(serverCmd)})

    def JoinGame(self, clientId, gameName, playerId, deck):
        if (playerId in list(self._knownPlayerIdDict.keys())):
            raise GameException(f"Player {playerId} is already in a game")
        
        self._gameIdx = None
        for i in range(0, len(self._currGameList)):
            if (self._currGameList[i].name == gameName):
                self._gameIdx = i
        if (self._gameIdx == None):
            serverCmd = {"cmd" : "ERROR", "msg" : f"Game {gameName} does not exist"}
            self._serverCmdList.append({"clientId" : clientId, "content" : json.dumps(serverCmd)})
        else:
            self._nextGameList[self._gameIdx].appendPlayer(playerId, deck)
            self._nextGameList[self._gameIdx].clientConnect()
            self._currGameList[self._gameIdx] = copy.deepcopy(self._nextGameList[self._gameIdx])
            self._knownPlayerIdDict[playerId] = clientId
            serverCmd = {"cmd" : "WAIT_GAME_START"}
            self._serverCmdList.append({"clientId" : clientId, "content" : json.dumps(serverCmd)})

    def Reconnect(self, clientId, gameName, playerId):
        if not(playerId in list(self._knownPlayerIdDict.keys())):
            raise GameException(f"Player {playerId} is not in the game {gameName}")
        
        self._knownPlayerIdDict[playerId] = clientId

    def FindGame(self, clientId, playerId, deck):
        if (self._waitingPlayer == {}):
            self._waitingPlayer = {"clientId" : clientId, "playerId" : playerId, "deck" : deck}
            serverCmd = {"cmd" : "WAIT_GAME_START"}
            self._serverCmdList.append({"clientId" : clientId, "content" : json.dumps(serverCmd)})
        else:
            self.CreateGame(self._waitingPlayer["clientId"], "Game_" + self._waitingPlayer["playerId"] + "_" + playerId, self._waitingPlayer["playerId"], self._waitingPlayer["deck"])
            self.JoinGame(clientId, "Game_" + self._waitingPlayer["playerId"] + "_" + playerId, playerId, deck)
            self._waitingPlayer = {}

    def CancelFindGame(self, clientId, playerId):
        self._knownPlayerIdDict.pop(playerId)
        self._waitingPlayer = {}