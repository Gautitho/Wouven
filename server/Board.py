from functions import *
from Player import *
from Entity import *
from Database import *
from GameException import *

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
        self._players[playerId] = Player(deck, team, pseudo)
        self._players[playerId].setHeroEntityId(self.appendEntity(playerId, db.heroes[deck["heroDescId"]]["entityDescId"], team, x, y))

    # Return the entityId
    def appendEntity(self, playerId, entityDescId, team, x, y):
        if (self.entityIdOnTile(x, y) == -1):
            self._entities.append(Entity(entityDescId, team, x, y))
            self._players[playerId].addEntity(len(self._entities) - 1)
            return len(self._entities) - 1
        else:
            raise GameException("Tile is not empty !")

    def removeEntity(self, entityIdx):
        del self._boardEntites[entityIdx]
        found = False
        for playerId in list(self._players.keys()):
            if entityIdx in self._players[playerId]:
                self._players[playerId].removeEntity(entityIdx)
                found = True
                break
        if not(found):
            raise GameException("Entity to remove not found in players entities list !")

    def entityIdOnTile(self, x, y):
        for entityId in range(0, len(self._entities)):
            if ((self._entities[entityId].x == x) and (self._entities[entityId].y == y)):
                return entityId
        return -1

    def startTurn(self, playerId):
        self._players[playerId].startTurn()
        for entityId in self._players[playerId].boardEntityIds:
            self._entities[entityId].startTurn()

    def endTurn(self, playerId):
        self._players[playerId].endTurn()
        for entityId in self._players[playerId].boardEntityIds:
            self._entities[entityId].endTurn()

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
                                    raise GameException("Path length is higher than your pm !")
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
                                        raise GameException("You can't attack this turn !")
                        else:
                            raise GameException("Successive tiles must be contiguous in path or an entity is on your path !")
                    else:
                        raise GameException("Tile out of the board !")
            else:
                raise GameException("You can't move anymore this turn !")
        else:
            raise GameException("First tile of the path must be the current entity position !")

        self._entities[entityId].move(x, y)
        if (attackedEntity != -1):
            self.modifyPv(attackedEntity, -self._entities[entityId].atk)

    def modifyPv(self, entityIdx, value):
        self._entities[entityIdx].modifyPv(value)
        if (self._entities[entityIdx].pv <= 0):
            removeEntity(entityIdx)

    def spellCast(self, playerId, spellId, targetPositionList):
        if (0 <= spellId < len(self._players[playerId].handSpellDescIds)):
            spell = db.spells[self._players[playerId].handSpellDescIds[spellId]]
            if (spell["cost"] <= self._players[playerId].pa):
                self._players[playerId].playSpell(spellId, spell["cost"])
                if (len(spell["allowedTargetList"]) == len(targetPositionList)):
                    if (len(spell["allowedTargetList"]) == 1):
                        if (spell["allowedTargetList"][0] == "all"):
                            pass

                        elif (spell["allowedTargetList"][0] == "allEntities"):
                            targetEntityId = self.entityIdOnTile(targetPositionList[0]["x"], targetPositionList[0]["y"])
                            if (targetEntityId != -1):
                               self.executeAbilities(spell["abilities"], "spellCast", playerId, -1, targetEntityId, {})
                            else:
                               raise GameException("No entity on this tile !")

                        elif (spell["allowedTargetList"][0] == "emptyTile"):
                            pass

                        elif (spell["allowedTargetList"][0] == "myEntity"):
                            pass

                        elif (spell["allowedTargetList"][0] == "opEntity"):
                            pass

                        else:
                            raise GameException("Wrong target type !")
                    else:
                        raise GameException("Spell with multi targets not supported !")
                else:
                    raise GameException("Wrong number of target !")
            else:
                raise GameException("Not enough pa to cast this spell !")
        else:
            raise GameException("Spell not in your hand !")

    def executeAbilities(self, abilityList, trigger, playerId, selfEntityId, targetEntityId, position):
        # Si nécessaire, mettre l'exécution de l'ability dans une string et l'eval plus tard
        for ability in abilityList:
            if (trigger == ability["trigger"]):
                if (ability["target"] == "target"):

                    conditionValid = False
                    if (ability["condition"][0] == ""):
                        conditionValid = True 
                    elif (ability["condition"][0] == "elemState"):
                        if (ability["condition"][1] in ["oiled", "wet", "muddy", "windy"]):
                            conditionValid = (self._entities[targetEntityId].elemState == ability["condition"][1])
                            self._entities[targetEntityId].setElemState("")
                        else:
                            raise GameException("ElemState to consume is not supported !")
                    else:
                        raise GameException("Wrong ability condition !")

                    if conditionValid:
                        if (ability["feature"] == "pv"):
                            self.modifyPv(targetEntityId, ability["value"])
                        elif (ability["feature"] == "elemState"):
                            self._entities[targetEntityId].setElemState(ability["value"])
                        else:
                            raise GameException("Wrong ability feature !")

                elif (ability["target"] == "self"):
                    pass

                elif (ability["target"] == "myPlayer"):
                    
                    conditionValid = False
                    if (ability["condition"][0] == ""):
                        conditionValid = True 
                    else:
                        raise GameException("Wrong ability condition !")

                    if conditionValid:
                        if (ability["feature"] == "gauges"):
                            if isinstance(ability["value"], dict):
                                for gaugeType in list(ability["value"].keys()):
                                    self._players[playerId].modifyGauge(gaugeType, ability["value"][gaugeType])
                            else:
                                raise GameException("Ability value for gauges must be a dict !")

                elif (ability["target"] == "opPlayer"):
                    pass

                else:
                    raise GameException("Wrong ability target !")

    def summon(self, playerId, companionId, summonPositionList):
        if (len(summonPositionList) == 1):
            if (0 <= companionId < len(self._players[playerId].companions)):
                if (self._players[playerId].companions[companionId]["state"] == "available"):
                    companion = db.companions[self._players[playerId].companions[companionId]["descId"]]
                    for gaugeType in list(companion["cost"].keys()):
                        self._players[playerId].modifyGauge(gaugeType, -companion["cost"][gaugeType])
                    placementValid = False
                    for placement in companion["placementList"]:
                        if (placement["ref"] == "ally"):
                            for allyEntityId in self._players[playerId].boardEntityIds:
                                if (abs(summonPositionList[0]["x"] - self._entities[allyEntityId].x) + abs(summonPositionList[0]["y"] - self._entities[allyEntityId].y) <= placement["range"]):
                                    placementValid = True
                        elif (placement["ref"] == "myPlayer"):
                            if (abs(summonPositionList[0]["x"] - self._entities[self._players[playerId].heroEntityId].x) + abs(summonPositionList[0]["y"] - self._entities[self._players[playerId].heroEntityId].y) <= placement["range"]):
                                placementValid = True
                        else:
                            raise GameException("Summon reference not allowed !")

                    if placementValid:
                        self.appendEntity(playerId, companion["entityDescId"], self._players[playerId].team, summonPositionList[0]["x"], summonPositionList[0]["y"])
                        self._players[playerId].summonCompanion(companionId)
                    else:
                        raise GameException("Invalid companion placement !")
                else:
                    raise GameException("Companion not available !")
            else:
                raise GameException("Companion not in your deck !")
        else:
            raise GameException("Only one summon position is allowed !")