import copy
import json
import traceback
import os
import sys
from Database import *
from Game import *
from GameException import *
from KnownPlayerList import *

class GameManager :

    def __init__(self):
        self._serverCmdList             = []
        self._currGameDict              = {}
        self._nextGameId                = 0
        self._knownPlayerList           = KnownPlayerList()
        self._gameId                   = None
        self._waitingPlayer             = {} # {playerId / deck}
        self._waitingCreatedGameList    = [] # [{gameName / clientId / playerId / deck}]

    def checkCmdArgs(self, cmdDict, keyList):
        for key in keyList:
            if not(key in cmdDict):
                raise GameException(f"No {key} field in command")

    def clientDisconnect(self, clientId):
        disconnectedPlayerId = self._knownPlayerList.clientDisconnect(clientId)
        
        for gameId in list(self._currGameDict.keys()):
            for playerId in self._currGameDict[gameId].playerIdList:
                if (playerId == disconnectedPlayerId):
                    nextGame = copy.deepcopy(self._currGameDict[gameId])
                    nextGame.clientDisconnect()
                    self._currGameDict[gameId] = copy.deepcopy(nextGame)

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
            elif (clientCmd == "GET_INIT"):
                self.checkCmdArgs(cmdDict, [])
                self.GetInit(clientId, playerId)
            elif (clientCmd == "FIND_GAME"):
                self.checkCmdArgs(cmdDict, ["deck"])
                self.FindGame(clientId, playerId, cmdDict["deck"])
            elif (clientCmd == "CANCEL_FIND_GAME"):
                self.checkCmdArgs(cmdDict, [])
                self.CancelFindGame(clientId, playerId)

            self._gameId = self._knownPlayerList.getGameId(clientId)

            if (self._gameId != None):
                nextGame = copy.deepcopy(self._currGameDict[self._gameId])
                gameCmdList = nextGame.run(cmdDict)
                self._currGameDict[self._gameId] = copy.deepcopy(nextGame)
                for gameCmd in gameCmdList:
                    self._serverCmdList.append({"clientId" : self._knownPlayerList.getClientId(gameCmd["playerId"]), "content" : gameCmd["content"]})

        except GameException as ge:
            serverCmd = {"cmd" : "ERROR", "msg" : ge.errorMsg}
            self._serverCmdList.append({"clientId" : clientId, "content" : json.dumps(serverCmd)})

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

        # Logs
        s = ""
        for gameId in list(self._currGameDict.keys()):
            s += self._currGameDict[gameId].generalLog() + "\n"
        s = s[:-1]
        printLog(s, filePath="gameList.log", writeMode="w")

        for gameId in list(self._currGameDict.keys()):
            printLog(self._currGameDict[gameId].entityListLog() + "\n", filePath="game_" + self._currGameDict[gameId].name + "/entityList.log", writeMode="w")
            printLog(self._currGameDict[gameId].playerListLog() + "\n", filePath="game_" + self._currGameDict[gameId].name + "/playerList.log", writeMode="w")
            if (self._gameId != None and self._currGameDict[gameId].name == self._currGameDict[self._gameId].name):
                printLog(cmdDict, filePath="game_" + self._currGameDict[gameId].name + "/client.log", writeMode="a")
                printLog(gameCmdList, filePath="game_" + self._currGameDict[gameId].name + "/server.log", writeMode="a")

        s = ""
        for player in self._knownPlayerList.knownPlayerList:
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
        for gameId in list(self._currGameDict.keys()):
            if self._currGameDict[gameId].checkInactiveGameErase():
                gameToEraseIdList.append(gameId)
        gameToEraseIdList.reverse()
        for gameId in gameToEraseIdList:
            self._knownPlayerList.removeKnownPlayerInGame(gameId)
            del self._currGameDict[gameId]

    def create(self, gameName):
        nextGame = Game(gameName)
        self._currGameDict[self._nextGameId] = copy.deepcopy(nextGame)
        self._nextGameId += 1

    def join(self, clientId, gameName, playerId, deck):
        self._gameId = None
        for gameId in list(self._currGameDict.keys()):
            if (self._currGameDict[gameId].name == gameName):
                self._gameId = gameId
        if (self._gameId == None):
            raise GameException(f"Game {gameName} does not exist")

        nextGame = copy.deepcopy(self._currGameDict[self._gameId])
        nextGame.appendPlayer(playerId, deck)
        nextGame.clientConnect()
        self._knownPlayerList.setGameId(playerId, self._gameId)
        self._currGameDict[self._gameId] = copy.deepcopy(nextGame)
        serverCmd = {"cmd" : "WAIT_GAME_START"}
        self._serverCmdList.append({"clientId" : clientId, "content" : json.dumps(serverCmd)})

    def CreateGame(self, clientId, gameName, playerId, deck):
        if self._knownPlayerList.isKnownPlayer(playerId):
            raise GameException(f"Player {playerId} is already in a game")
        checkDeck(deck)
        for game in self._waitingCreatedGameList:
            if (gameName == game["gameName"]):
                raise GameException(f"Game {gameName} already exists")
            if (playerId == game["playerId"]):
                raise GameException(f"Player {playerId} is already waiting for a game")
        for gameId in list(self._currGameDict.keys()):
            if (gameName == self._currGameDict[gameId].name):
                raise GameException(f"Game {gameName} already exists")

        self._knownPlayerList.appendKnownPlayer(playerId, clientId)
        self._waitingCreatedGameList.append({"gameName" : gameName, "clientId" : clientId, "playerId" : playerId, "deck" : deck})
        serverCmd = {"cmd" : "WAIT_GAME_START"}
        self._serverCmdList.append({"clientId" : clientId, "content" : json.dumps(serverCmd)})

    def CancelCreateGame(self, clientId, playerId):
        self._knownPlayerList.removeKnownPlayer(playerId) 
        for gameId in range(len(self._waitingCreatedGameList)):
            if (playerId == self._waitingCreatedGameList[gameId]["playerId"]):
                del self._waitingCreatedGameList[gameId]
                serverCmd = {"cmd" : "CANCEL_GAME_START"}
                self._serverCmdList.append({"clientId" : clientId, "content" : json.dumps(serverCmd)})
                return
        raise GameException(f"No game created")

    def JoinGame(self, clientId, gameName, playerId, deck):
        if self._knownPlayerList.isKnownPlayer(playerId):
            raise GameException(f"Player {playerId} is already in a game")
        checkDeck(deck)

        self._knownPlayerList.appendKnownPlayer(playerId, clientId)
        for gameId in range(len(self._waitingCreatedGameList)):
            if (gameName == self._waitingCreatedGameList[gameId]["gameName"]):
                self.create(gameName)
                self.join(self._waitingCreatedGameList[gameId]["clientId"], self._waitingCreatedGameList[gameId]["gameName"], self._waitingCreatedGameList[gameId]["playerId"], self._waitingCreatedGameList[gameId]["deck"])
                self.join(clientId, gameName, playerId, deck)
                del self._waitingCreatedGameList[gameId]
                return
        raise GameException(f"Game {gameName} doesn't exist")

    def GetInit(self, clientId, playerId):
        if not(self._knownPlayerList.isKnownPlayer(playerId)):
            raise GameException(f"Player {playerId} is not in a game")
    
        self._knownPlayerList.appendKnownPlayer(playerId, clientId) # Update clientId
        self._gameId = self._knownPlayerList.getGameId(clientId)

        if (self._gameId == None):
            raise GameException(f"This game could not be initiated !")
        
        nextGame = copy.deepcopy(self._currGameDict[self._gameId])
        nextGame.clientConnect()
        self._currGameDict[self._gameId] = copy.deepcopy(nextGame)

    def Reconnect(self, clientId, playerId):
        if not(self._knownPlayerList.isKnownPlayer(playerId)):
            raise GameException(f"Player {playerId} is not in a game")
        if (self._knownPlayerList.getClientId(playerId) != None):
            raise GameException(f"Player {playerId} is already connected to his game")
        
        self._knownPlayerList.appendKnownPlayer(playerId, clientId) # Update clientId
        serverCmd           = {}
        serverCmd["cmd"]    = "GAME_RECONNECT"
        serverCmd["name"]   = self._knownPlayerList.getGameId(clientId)
        self._serverCmdList.append({"clientId" : clientId, "content" : json.dumps(serverCmd)})

    def FindGame(self, clientId, playerId, deck):
        if self._knownPlayerList.isKnownPlayer(playerId):
            raise GameException(f"Player {playerId} is already in a game")
        checkDeck(deck)

        self._knownPlayerList.appendKnownPlayer(playerId, clientId)
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
        self._knownPlayerList.removeKnownPlayer(playerId) 
        self._waitingPlayer = {}
        serverCmd = {"cmd" : "CANCEL_GAME_START"}
        self._serverCmdList.append({"clientId" : clientId, "content" : json.dumps(serverCmd)})