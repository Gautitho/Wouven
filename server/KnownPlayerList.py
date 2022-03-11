from GameException import *

class KnownPlayerList :
    def __init__(self):
        self._knownPlayerList           = []

    @property
    def knownPlayerList(self):
        return self._knownPlayerList

    def isKnownPlayer(self, playerId):
        for player in self._knownPlayerList:
            if player["playerId"] == playerId:
                return True
        return False

    def getClientId(self, playerId):
        for player in self._knownPlayerList:
            if (player["playerId"] == playerId):
                return player["clientId"] 
        return None

    def getPlayerId(self, clientId):
        for player in self._knownPlayerList:
            if (player["clientId"] == clientId):
                return player["playerId"] 
        return None

    def getGameId(self, clientId):
        for player in self._knownPlayerList:
            if (player["clientId"] == clientId):
                return player["gameId"] 
        return None

    # Append if playerId doesn't exist, update if he already exist
    def appendKnownPlayer(self, playerId, clientId):
        for playerIdx in range(len(self._knownPlayerList)):
            if (self._knownPlayerList[playerIdx]["playerId"] == playerId):
                self._knownPlayerList[playerIdx]["clientId"] = clientId
                return
        self._knownPlayerList.append({"playerId" : playerId, "clientId" : clientId, "gameId" : None})

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

    def setGameId(self, playerId, gameId):
        for playerIdx in range(len(self._knownPlayerList)):
            if (self._knownPlayerList[playerIdx]["playerId"] == playerId):
                self._knownPlayerList[playerIdx]["gameId"] = gameId
                return
        raise GameException(f"Player {playerId} does not exist !")

    def clientDisconnect(self, clientId):
        for playerIdx in range(len(self._knownPlayerList)):
            if (self._knownPlayerList[playerIdx]["clientId"] == clientId):
                self._knownPlayerList[playerIdx]["clientId"] = None
                return self._knownPlayerList[playerIdx]["playerId"]
        raise GameException(f"Client {clientId} does not exist !")