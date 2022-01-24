import copy
import json
import traceback
import os
from Game import *
from GameException import *

class GameManager :

    def __init__(self):
        self._serverCmdList             = []
        self._currGameList              = []
        self._nextGameList              = []
        self._nextGameId                = 0
        self._gameIdList                = []
        self._knownPlayerIdDict         = {} # {playerId : clientId}
        self._gameIdx                   = None
        self._waitingPlayer             = {} # {playerId / deck}
        self._waitingCreatedGameList    = [] # [{gameName / clientId / playerId / deck}]

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
            elif (clientCmd == "CANCEL_CREATE_GAME"):
                self.checkCmdArgs(cmdDict, [])
                self.CancelCreateGame(clientId, playerId)
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

        # Logs
        #s = ""
        #for game in self._currGameList:
        #    s += game.generalLog() + "\n"
        #printLog(s, filePath="logs/gameList.log", writeMode="w")

        #for game in self._currGameList:
        #    if not(os.path.isdir("logs/game_" + game.name)):
        #        os.mkdir("logs/game_" + game.name)
        #    printLog(game.entitiesLog() + "\n", filePath="logs/game_" + game.name + "/entityList.log", writeMode="w")
        #    if (game.name == self._nextGameList[self._gameIdx].name):
        #        printLog(cmdDict, filePath="logs/game_" + game.name + "/client.log", writeMode="a")
        #        printLog(gameCmdList, filePath="logs/game_" + game.name + "/server.log", writeMode="a")

        #s = ""
        #for playerId in list(self._knownPlayerIdDict.keys()):
        #    s += "Player Id : " + str(playerId) + " / Client Id : " + str(self._knownPlayerIdDict[playerId]) + "\n"
        #printLog(s, filePath="logs/knownPlayerList.log", writeMode="w")

        return self._serverCmdList

    def garbageCollector(self):
        gameToEraseIdList = []
        for gameIdx in range(0, len(self._currGameList)):
            if self._currGameList[gameIdx].checkInactiveGameErase():
                gameToEraseIdList.append(gameIdx)
        gameToEraseIdList.reverse()
        for gameIdx in gameToEraseIdList:
            for playerId in self._currGameList[gameIdx].playerIdList:
                del self._knownPlayerIdDict[playerId]
            del self._currGameList[gameIdx]
            del self._nextGameList[gameIdx]

    def create(self, gameName):
        self._nextGameList.append(Game(gameName))
        self._gameIdList.append(self._nextGameId)
        self._gameIdx = self._nextGameId
        self._nextGameId += 1
        self._currGameList.append(copy.deepcopy(self._nextGameList[self._gameIdx]))

    def join(self, clientId, gameName, playerId, deck):
        self._gameIdx = None
        for i in range(0, len(self._currGameList)):
            if (self._currGameList[i].name == gameName):
                self._gameIdx = i
        if (self._gameIdx == None):
            raise GameException(f"Game {gameName} does not exist")

        self._nextGameList[self._gameIdx].appendPlayer(playerId, deck)
        self._nextGameList[self._gameIdx].clientConnect()
        self._currGameList[self._gameIdx] = copy.deepcopy(self._nextGameList[self._gameIdx])
        serverCmd = {"cmd" : "WAIT_GAME_START"}
        self._serverCmdList.append({"clientId" : clientId, "content" : json.dumps(serverCmd)})

    def CreateGame(self, clientId, gameName, playerId, deck):
        if (playerId in list(self._knownPlayerIdDict.keys())):
            raise GameException(f"Player {playerId} is already in a game")
        self._knownPlayerIdDict[playerId] = clientId
        for game in self._waitingCreatedGameList:
            if (gameName == game["gameName"]):
                raise GameException(f"Game {gameName} already exists")
            if (playerId == game["playerId"]):
                raise GameException(f"Player {playerId} is already waiting for a game")
        for game in self._currGameList:
            if (gameName == game.name):
                raise GameException(f"Game {gameName} already exists")

        self._waitingCreatedGameList.append({"gameName" : gameName, "clientId" : clientId, "playerId" : playerId, "deck" : deck})
        serverCmd = {"cmd" : "WAIT_GAME_START"}
        self._serverCmdList.append({"clientId" : clientId, "content" : json.dumps(serverCmd)})

    def CancelCreateGame(self, clientId, playerId):
        del self._knownPlayerIdDict[playerId]
        for gameIdx in range(len(self._waitingCreatedGameList)):
            if (playerId == self._waitingCreatedGameList[gameIdx]["playerId"]):
                del self._waitingCreatedGameList[gameIdx]
                serverCmd = {"cmd" : "CANCEL_GAME_START"}
                self._serverCmdList.append({"clientId" : clientId, "content" : json.dumps(serverCmd)})
                return
        raise GameException(f"No game created")

    def JoinGame(self, clientId, gameName, playerId, deck):
        if (playerId in list(self._knownPlayerIdDict.keys())):
            raise GameException(f"Player {playerId} is already in a game")
        self._knownPlayerIdDict[playerId] = clientId
        for gameIdx in range(len(self._waitingCreatedGameList)):
            if (gameName == self._waitingCreatedGameList[gameIdx]["gameName"]):
                self.create(gameName)
                self.join(self._waitingCreatedGameList[gameIdx]["clientId"], self._waitingCreatedGameList[gameIdx]["gameName"], self._waitingCreatedGameList[gameIdx]["playerId"], self._waitingCreatedGameList[gameIdx]["deck"])
                self.join(clientId, gameName, playerId, deck)
                del self._waitingCreatedGameList[gameIdx]
                return
        raise GameException(f"Game {gameName} doesn't exist")

    def Reconnect(self, clientId, gameName, playerId):
        if not(playerId in list(self._knownPlayerIdDict.keys())):
            raise GameException(f"Player {playerId} is not in the game {gameName}")
        
        self._knownPlayerIdDict[playerId] = clientId

    def FindGame(self, clientId, playerId, deck):
        if (playerId in list(self._knownPlayerIdDict.keys())):
            raise GameException(f"Player {playerId} is already in a game")
        self._knownPlayerIdDict[playerId] = clientId
        if (self._waitingPlayer == {}):
            self._waitingPlayer = {"clientId" : clientId, "playerId" : playerId, "deck" : deck}
            serverCmd = {"cmd" : "WAIT_GAME_START"}
            self._serverCmdList.append({"clientId" : clientId, "content" : json.dumps(serverCmd)})
        else:
            self.create("Game_" + self._waitingPlayer["playerId"] + "_" + playerId)
            self.join(self._waitingPlayer["clientId"], "Game_" + self._waitingPlayer["playerId"] + "_" + playerId, self._waitingPlayer["playerId"], self._waitingPlayer["deck"])
            self.join(clientId, "Game_" + self._waitingPlayer["playerId"] + "_" + playerId, playerId, deck)
            self._waitingPlayer = {}

    def CancelFindGame(self, clientId, playerId):
        del self._knownPlayerIdDict[playerId]
        self._waitingPlayer = {}
        serverCmd = {"cmd" : "CANCEL_GAME_START"}
        self._serverCmdList.append({"clientId" : clientId, "content" : json.dumps(serverCmd)})