import copy
import json
import traceback
import os
import sys
from Game import *
from GameException import *

class GameManager :

    def __init__(self):
        self._serverCmdList             = []
        self._currGameList              = []
        self._nextGameList              = []
        self._nextGameId                = 0
        self._gameIdList                = []
        self._knownPlayerList           = [] # [{clientId / playerId / gameId}]
        self._gameIdx                   = None
        self._waitingPlayer             = {} # {playerId / deck}
        self._waitingCreatedGameList    = [] # [{gameName / clientId / playerId / deck}]

    def checkCmdArgs(self, cmdDict, keyList):
        for key in keyList:
            if not(key in cmdDict):
                raise GameException(f"No {key} field in command")

    def getClientGame(self, clientId):
        playerId = None
        for player in self._knownPlayerList:
            if (player["clientId"] == clientId):
                playerId = player["playerId"]
                break
        if (playerId == None):
            return None
        for i in range(0, len(self._currGameList)):
            for playerIdB in self._currGameList[i].playerIdList:
                if (playerId == playerIdB):
                    return i
        return None

    def isKnownPlayer(self, playerId):
        for player in self._knownPlayerList:
            if player["playerId"] == playerId:
                return True
        return False

    def getKnownPlayer(self, playerId):
        for player in self._knownPlayerList:
            if player["playerId"] == playerId:
                return player
        raise GameException(f"Player {playerId} does not exist !")

    # Append if playerId doesn't exist, update if he already exist
    def appendKnownPlayer(self, playerId, clientId, gameId):
        for player in self._knownPlayerList:
            if player["playerId"] == playerId:
                player["clientId"]  = clientId
                player["gameId"]    = gameId
                return
        self._knownPlayerList.append({"playerId" : playerId, "clientId" : clientId, "gameId" : gameId})

    def removeKnownPlayer(self, playerId):
        idxToRemove = None
        for playerIdx in range(len(self._knownPlayerList)):
            if self._knownPlayerList[playerIdx]["playerId"] == playerId:
                idxToRemove = playerIdx
                break
        if (idxToRemove != None):
            del self._knownPlayerList[idxToRemove]
        else:
            raise GameException(f"Player {playerId} does not exist !")

    def removeKnownPlayerInGame(self, gameId):
        idxToRemoveList = []
        for playerIdx in range(len(self._knownPlayerList)):
            if self._knownPlayerList[playerIdx]["gameId"] == gameId:
                idxToRemoveList.append(playerIdx)
        idxToRemoveList.reverse()
        for idx in idxToRemoveList:
            del self._knownPlayerList[idx]

    def clientDisconnect(self, clientId):
        for player in self._knownPlayerList:
            if (player["clientId"] == clientId):
                playerDisconnected = player["playerId"]
                player["clientId"] == None
                break
        
        for game in self._currGameList:
            for playerId in game.playerIdList:
                if (playerId == playerDisconnected):
                    game.clientDisconnect()

    def run(self, cmdDict, clientId):
        self._serverCmdList = []
        gameCmdList = []
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
                self.checkCmdArgs(cmdDict, [])
                self.Reconnect(clientId, playerId)
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
                    self._serverCmdList.append({"clientId" : self.getKnownPlayer(gameCmd["playerId"])["clientId"], "content" : gameCmd["content"]})
                self._currGameList[self._gameIdx] = copy.deepcopy(self._nextGameList[self._gameIdx])

        except GameException as ge:
            serverCmd = {"cmd" : "ERROR", "msg" : ge.errorMsg}
            self._serverCmdList.append({"clientId" : clientId, "content" : json.dumps(serverCmd)})
            if (self._gameIdx != None and self._currGameList and self._currGameList[self._gameIdx]):
                self._nextGameList[self._gameIdx] = copy.deepcopy(self._currGameList[self._gameIdx]) # Restore a stable game

        except:
            if LOCAL_ENABLE:
                print(traceback.format_exc())
                print("Exception : " + str(sys.exc_info()[0]))
                sys.exit(1)
            else:
                printLog(str(traceback.format_exc()), filePath="error.log", writeMode="a")
                printLog(str(sys.exc_info()[0]), filePath="error.log", writeMode="a")
                serverCmd = {"cmd" : "ERROR", "msg" : "Fatal error : " + str(sys.exc_info()[0])}
                self._serverCmdList.append({"clientId" : clientId, "content" : json.dumps(serverCmd)})
                if (self._gameIdx != None and self._currGameList and self._currGameList[self._gameIdx]):
                    self._nextGameList[self._gameIdx] = copy.deepcopy(self._currGameList[self._gameIdx]) # Restore a stable game

        # Logs
        s = ""
        for game in self._currGameList:
            s += game.generalLog() + "\n"
        s = s[:-1]
        printLog(s, filePath="gameList.log", writeMode="w")

        for game in self._currGameList:
            if not(os.path.isdir(logDir + "/game_" + game.name)):
                os.mkdir(logDir + "/game_" + game.name)
            printLog(game.entityListLog() + "\n", filePath="game_" + game.name + "/entityList.log", writeMode="w")
            printLog(game.playerListLog() + "\n", filePath="game_" + game.name + "/playerList.log", writeMode="w")
            if (self._gameIdx != None and game.name == self._currGameList[self._gameIdx].name):
                printLog(cmdDict, filePath="game_" + game.name + "/client.log", writeMode="a")
                printLog(gameCmdList, filePath="game_" + game.name + "/server.log", writeMode="a")

        s = ""
        for player in self._knownPlayerList:
            s += "Player Id : " + str(player["playerId"]) + " / Client Id : " + str(player["clientId"]) + " / Game Id : " + str(player["gameId"]) + "\n"
        s = s[:-1]
        printLog(s, filePath="knownPlayerList.log", writeMode="w")

        if self._waitingPlayer:
            s = "Player Id : " + str(self._waitingPlayer["playerId"]) + " / Deck : " + toString(self._waitingPlayer["deck"], separator="\n")
        else:
            s= ""
        printLog(s, filePath="waitingPlayer.log", writeMode="w")

        s = ""
        for game in self._waitingCreatedGameList:
            s += toString(game, separator=" / ") + "\n"
        s = s[:-1]
        printLog(s, filePath="waitingCreatedGameList.log", writeMode="w")

        return self._serverCmdList

    def garbageCollector(self):
        gameToEraseIdList = []
        for gameIdx in range(0, len(self._currGameList)):
            if self._currGameList[gameIdx].checkInactiveGameErase():
                gameToEraseIdList.append(gameIdx)
        gameToEraseIdList.reverse()
        for gameIdx in gameToEraseIdList:
            self.removeKnownPlayerInGame(gameIdx)
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
        self.getKnownPlayer(playerId)["gameId"] = self._gameIdx
        self._currGameList[self._gameIdx] = copy.deepcopy(self._nextGameList[self._gameIdx])
        serverCmd = {"cmd" : "WAIT_GAME_START"}
        self._serverCmdList.append({"clientId" : clientId, "content" : json.dumps(serverCmd)})

    def CreateGame(self, clientId, gameName, playerId, deck):
        if self.isKnownPlayer(playerId):
            raise GameException(f"Player {playerId} is already in a game")
        self.appendKnownPlayer(playerId, clientId, None)
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
        self.removeKnownPlayer(playerId) 
        for gameIdx in range(len(self._waitingCreatedGameList)):
            if (playerId == self._waitingCreatedGameList[gameIdx]["playerId"]):
                del self._waitingCreatedGameList[gameIdx]
                serverCmd = {"cmd" : "CANCEL_GAME_START"}
                self._serverCmdList.append({"clientId" : clientId, "content" : json.dumps(serverCmd)})
                return
        raise GameException(f"No game created")

    def JoinGame(self, clientId, gameName, playerId, deck):
        if self.isKnownPlayer(playerId):
            raise GameException(f"Player {playerId} is already in a game")
        self.appendKnownPlayer(playerId, clientId, None)
        for gameIdx in range(len(self._waitingCreatedGameList)):
            if (gameName == self._waitingCreatedGameList[gameIdx]["gameName"]):
                self.create(gameName)
                self.join(self._waitingCreatedGameList[gameIdx]["clientId"], self._waitingCreatedGameList[gameIdx]["gameName"], self._waitingCreatedGameList[gameIdx]["playerId"], self._waitingCreatedGameList[gameIdx]["deck"])
                self.join(clientId, gameName, playerId, deck)
                del self._waitingCreatedGameList[gameIdx]
                return
        raise GameException(f"Game {gameName} doesn't exist")

    def Reconnect(self, clientId, playerId):
        if not(self.isKnownPlayer(playerId)):
            raise GameException(f"Player {playerId} is not in a game")
        
        self.appendKnownPlayer(playerId, clientId, None)

    def FindGame(self, clientId, playerId, deck):
        if self.isKnownPlayer(playerId):
            raise GameException(f"Player {playerId} is already in a game")
        self.appendKnownPlayer(playerId, clientId, None)
        if (self._waitingPlayer == {}):
            self._waitingPlayer = {"clientId" : clientId, "playerId" : playerId, "deck" : deck}
            serverCmd = {"cmd" : "WAIT_GAME_START"}
            self._serverCmdList.append({"clientId" : clientId, "content" : json.dumps(serverCmd)})
        else:
            gameName = "Game_" + str(self._nextGameId)
            self.create(gameName)
            self.join(self._waitingPlayer["clientId"], gameName, self._waitingPlayer["playerId"], self._waitingPlayer["deck"])
            self.join(clientId, gameName, playerId, deck)
            self._waitingPlayer = {}

    def CancelFindGame(self, clientId, playerId):
        self.removeKnownPlayer(playerId) 
        self._waitingPlayer = {}
        serverCmd = {"cmd" : "CANCEL_GAME_START"}
        self._serverCmdList.append({"clientId" : clientId, "content" : json.dumps(serverCmd)})