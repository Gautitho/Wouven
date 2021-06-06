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

    def newTurn(self, playerId):
        self._players[playerId].newTurn()
        for entityId in self._players[playerId].boardEntityIds:
            self._entities[entityId].newTurn()

    def moveEntity(self, entityId, path):
        errorMsg        = ""
        x               = self._entities[entityId].x
        y               = self._entities[entityId].y
        pm              = self._entities[entityId].pm
        attackedEntity  = -1
        if (self._entities[entityId].canMove):
            if (path[0]["x"] == x and path[0]["y"] == y): # The path is given with the inital position of the entity
                path.pop(0)
                for tile in path:
                    nextX = tile["x"]
                    nextY = tile["y"]
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

    # TODO : A évaluer, faire une fonction de réalisation d'abilities séparée
    def spellCast(self, playerId, spellId, targetPositionList):
        errorMsg = ""
        if (spellId < len(self._players[playerId].handSpellDescIds)):
            spell = db.spells[self._players[playerId].handSpellDescIds[spellId]]
            if (spell["cost"] <= self._players[playerId].pa):
                if (len(spell["allowedTargetList"]) == len(targetPositionList)):
                    if (len(spell["allowedTargetList"]) == 1):
                        if (spell["allowedTargetList"][0] == "all"):
                            pass

                        elif (spell["allowedTargetList"][0] == "allEntities"):
                            targetEntity = self.entityIdOnTile(targetPositionList[0]["x"], targetPositionList[0]["y"])
                            if (targetEntity != -1):
                                self.executeAbilities(spell["abilites"], "spellCast", playerId, -1, targetEntity, {})
                            else:
                                errorMsg = "No entity on this tile !"

                        elif (spell["allowedTargetList"][0] == "emptyTile"):
                            pass

                        elif (spell["allowedTargetList"][0] == "myEntity"):
                            pass

                        elif (spell["allowedTargetList"][0] == "opEntity"):
                            pass

                        else:
                            errorMsg = "Wrong entity type !"
                    else:
                        errorMsg = "Spell with multi targets not supported !"
                else:
                    errorMsg = "Wrong number of target !"
            else:
                errorMsg = "Not enough pa to cast this spell !"
        else:
            errorMsg = "Spell not in your hand !"

        if (errorMsg == ""):
            self._players[playerId].playSpell(spellId, spell["cost"])

        return errorMsg

    def executeAbilities(self, abilityList, trigger, playerId, selfEntityId, targetEntityId, position):
        # Si nécessaire, mettre l'exécution de l'ability dans une string et l'eval plus tard
        errorMsg = ""
        for ability in abilityList:
            if (trigger == ability["trigger"]):
                if (ability["target"] == "target"):
                    if (ability["feature"] == "pv"):
                        self.modifyPv(targetEntity, ability["value"])

                    elif (ability["feature"] == "earth"):
                        pass

                    else:
                        errorMsg = "Wrong ability feature !"

                elif (ability["target"] == "self"):
                    pass

                elif (ability["target"] == "myPlayer"):
                    pass

                elif (ability["target"] == "opPlayer"):
                    pass

                else:
                    errorMsg = "Wrong ability target !"

        return errorMsg
