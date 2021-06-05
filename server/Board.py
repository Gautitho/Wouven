from functions import *
from Player import *
from Entity import *
from Database import *

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
            x = BOARD_COLS - 1
            y = 0
        elif (team == "red"):
            x = 0
            y = BOARD_ROWS - 1
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

    def moveEntity(self, entityId, path):
        errorMsg        = ""
        x               = self._entities[entityId].x
        y               = self._entities[entityId].y
        pm              = self._entities[entityId].pm
        attackedEntity  = -1
        if (self._entities[entityId].canMove):
            if (int(path[0]["x"]) == x and int(path[0]["y"]) == y): # The path is given with the inital position of the entity
                path.pop(0)
                for tile in path:
                    nextX = int(tile["x"])
                    nextY = int(tile["y"])
                    if (0 <= nextX < BOARD_COLS and 0 <= nextY < BOARD_ROWS):
                        if (abs(x - nextX) + abs(y - nextY) == 1):
                            if (pm == 0):
                                if (self._entities[entityId].canAttack and self.entityIdOnTile(nextX, nextY) != -1): # Attack after full pm move
                                    attackedEntity  = self.entityIdOnTile(nextX, nextY)
                                    pm              = -1                           
                                else:
                                    errorMsg = "Path length is higher than your pm !"
                                    break
                            else:
                                if (self.entityIdOnTile(nextX, nextY) == -1): # The next tile is empty
                                    x             = nextX
                                    y             = nextY
                                    pm            -= 1
                                else: # There is an entity on next tile
                                    if (self._entities[entityId].canAttack):
                                        attackedEntity  = self.entityIdOnTile(nextX, nextY)
                                        pm              = -1
                                    else:
                                        errorMsg = "You can't attack this turn !"
                                        break
                        else:
                            errorMsg = "Successive tiles must be contiguous in path or an entity is on your path !"
                            break
                    else:
                        errorMsg = "Tile out of the board !"
            else:
                errorMsg = "You can't move anymore this turn !"
        else:
            errorMsg = "First tile of the path must be the current entity position !"

        if (errorMsg == ""):                
            self._entities[entityId].move(x, y)
            if (attackedEntity != -1):
                self.modifyPv(attackedEntity, -self._entities[entityId].atk)

        return errorMsg

    def modifyPv(self, entityIdx, value):
        self._entities[entityIdx].modifyPv(value)
        if (self._entities[entityIdx].pv <= 0):
            removeEntity(entityIdx)