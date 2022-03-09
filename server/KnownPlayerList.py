import os
import sys

class KnownPlayerList :
    def __init__(self):
        self._knownPlayerList           = []

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

    def getPlayerId(self, clientId):
        for player in self._knownPlayerList:
            if (player["clientId"] == clientId):
                return player["playerId"] 
        return None

    @property
    def knownPlayerList(self):
        return self._knownPlayerList