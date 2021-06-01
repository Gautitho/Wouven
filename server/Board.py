from functions import *
from Player import *
from Entity import *
from Database import db

class Board:

    def __init__(self):
        self._entities  = []
        self._players   = {}

    @property
    def entities(self):
        return list(self._entities)

    @property
    def players(self):
        return dict(self._players)

    def appendPlayer(self, playerId, deck, team, pseudo):
        if (team == "blue"):
            x = 6
            y = 0
        elif (team == "red"):
            x = 0
            y = 6
        self._players[playerId] = Player(deck, team, pseudo, self.appendEntity(Entity(db.heroes[deck["heroDescId"]]["entityDescId"], team, x, y)))

    # Return the entityId
    def appendEntity(self, entity):
        if (self.entityIdOnTile(entity.x, entity.y) == -1):
            self._entities.append(entity)
            return len(self._entities) - 1

    def removeEntity(self, entityIdx):
        del self._boardEntites[entityIdx]

    def entityIdOnTile(self, x, y):
        for entityId in range(0, len(self._entities)):
            if ((self._entities[entityId].x == x) and (self._entities[entityId].y == y)):
                return entityId
        return -1

    def modifyPv(self, entityIdx, value):
        self._entities[entityIdx].modifyPv(value)
        if (self._entities[entityIdx].pv <= 0):
            removeEntity(entityIdx)