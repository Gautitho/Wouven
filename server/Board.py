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
        if (self.entityIdOnTile(x, y) == None):
            self._entities.append(Entity(entityDescId, team, x, y))
            self._players[playerId].addEntity(len(self._entities) - 1)
            return len(self._entities) - 1
        else:
            raise GameException("Tile is not empty !")

    def removeEntity(self, entityIdx):
        found = False
        for playerId in list(self._players.keys()):
            if entityIdx in self._players[playerId].boardEntityIds:
                self._players[playerId].removeEntity(entityIdx)
                found = True
                break
        del self._entities[entityIdx]
        if not(found):
            raise GameException("Entity to remove not found in players entities list !")

    def garbageCollector(self):
        entityId = 0
        while (entityId < len(self._entities)):
            if (self._entities[entityId].pv <= 0):
                self.removeEntity(entityId)
                entityId = 0
            else:
                entityId += 1

    def getOpPlayerId(self, playerId):
        for pId in list(self._players.keys()):
            if (pId != playerId):
                return pId

    def getOpTeam(self, playerId):
        if (self._players[playerId].team == "blue"):
            return "red"
        elif (self._players[playerId].team == "red"):
            return "blue"
        else:
            raise GameException(f"Team ({self._players[playerId].team}) does not exist !")

    def entityIdOnTile(self, x, y):
        for entityId in range(0, len(self._entities)):
            if ((self._entities[entityId].x == x) and (self._entities[entityId].y == y)):
                return entityId
        return None

    def entityIdAroundTile(self, x, y, team):
        entityIdList = []
        for xa in range(max(x-1, 0), min(x+2, BOARD_COLS)):
            for ya in range(max(y-1, 0), min(y+2, BOARD_ROWS)):
                if (xa != x or ya != y):
                    matchId = self.entityIdOnTile(xa, ya)
                    if (matchId != None):
                        if (team == "all" or team == self._entities[matchId].team):
                            entityIdList.append(matchId)
        return entityIdList

    def entityIdNextToTile(self, x, y, team):
        entityIdList = []
        matchId = self.entityIdOnTile(max(x-1, 0), y)
        if (matchId != None):
            if (team == "all" or team == self._entities[matchId].team):
                entityIdList.append(matchId)
        matchId = self.entityIdOnTile(min(x+1, BOARD_COLS), y)
        if (matchId != None):
            if (team == "all" or team == self._entities[matchId].team):
                entityIdList.append(matchId)
        matchId = self.entityIdOnTile(x, max(y-1, 0))
        if (matchId != None):
            if (team == "all" or team == self._entities[matchId].team):
                entityIdList.append(matchId)
        matchId = self.entityIdOnTile(x, min(y+1, BOARD_ROWS))
        if (matchId != None):
            if (team == "all" or team == self._entities[matchId].team):
                entityIdList.append(matchId)
        return entityIdList

    def entityIdAlignedToTile(self, x, y, team):
        entityIdList = []
        for xa in range(0, BOARD_COLS):
            if (xa != x):
                matchId = self.entityIdOnTile(xa, y)
                if (matchId != None):
                    if (team == "all" or team == self._entities[matchId].team):
                        entityIdList.append(matchId)
        for ya in range(0, BOARD_ROWS):
            if (ya != y):
                matchId = self.entityIdOnTile(x, ya)
                if (matchId != None):
                    if (team == "all" or team == self._entities[matchId].team):
                        entityIdList.append(matchId)
        return entityIdList

    def firstEntityIdAlignedToTile(self, x, y, team):
        entityIdList = []
        for xa in range(x-1, -1, -1):
            matchId = self.entityIdOnTile(xa, y)
            if (matchId != None):
                if (team == "all" or team == self._entities[matchId].team):
                    entityIdList.append(matchId)
                    break
        for xa in range(x+1, BOARD_COLS):
            matchId = self.entityIdOnTile(xa, y)
            if (matchId != None):
                if (team == "all" or team == self._entities[matchId].team):
                    entityIdList.append(matchId)
                    break
        for ya in range(y-1, -1, -1):
            matchId = self.entityIdOnTile(x, ya)
            if (matchId != None):
                if (team == "all" or team == self._entities[matchId].team):
                    entityIdList.append(matchId)
                    break
        for ya in range(y+1, BOARD_ROWS):
            matchId = self.entityIdOnTile(x, ya)
            if (matchId != None):
                if (team == "all" or team == self._entities[matchId].team):
                    entityIdList.append(matchId)
                    break
        return entityIdList

    def startTurn(self, playerId):
        self._players[playerId].startTurn()
        for entityId in self._players[playerId].boardEntityIds:
            self._entities[entityId].startTurn()

    def endTurn(self, playerId):
        self._players[playerId].endTurn()
        for entityId in self._players[playerId].boardEntityIds:
            self._entities[entityId].endTurn()

    def moveEntity(self, playerId, entityId, path):
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
                                if (self._entities[entityId].canAttack and self.entityIdOnTile(nextX, nextY) != None): # Attack after full pm move
                                    attackedEntityId  = self.entityIdOnTile(nextX, nextY)
                                    self._entities[attackedEntityId].modifyPv(-self._entities[entityId].atk)
                                    self.executeAbilities(self._entities[entityId].abilities, "attack", playerId, entityId, [attackedEntityId], [], None)
                                    self.executeAbilities(self._entities[attackedEntityId].abilities, "attacked", playerId, attackedEntityId, None, [], None)
                                    pm              = -1
                                else:
                                    raise GameException("Path length is higher than your pm !")
                            else:
                                if (self.entityIdOnTile(nextX, nextY) == None): # The next tile is empty
                                    x             = nextX
                                    y             = nextY
                                    pm            -= 1
                                else: # There is an entity on next tile
                                    if (self._entities[entityId].canAttack):
                                        attackedEntityId  = self.entityIdOnTile(nextX, nextY)
                                        self._entities[attackedEntityId].modifyPv(-self._entities[entityId].atk)
                                        self.executeAbilities(self._entities[entityId].abilities, "attack", playerId, entityId, [attackedEntityId], [], None)
                                        self.executeAbilities(self._entities[attackedEntityId].abilities, "attacked", playerId, attackedEntityId, None, [], None)
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

    def spellCast(self, playerId, spellId, targetPositionList):
        # Check if spell in hand
        if (0 <= spellId < len(self._players[playerId].handSpellDescIds)):
            spell = db.spells[self._players[playerId].handSpellDescIds[spellId]]

            # Check if there is enough PA to play the spell
            if (spell["cost"] <= self._players[playerId].pa):
                self._players[playerId].playSpell(spellId, spell["cost"])

                # Check allowed targets
                if (len(spell["allowedTargetList"]) == len(targetPositionList)):
                    positionList        = targetPositionList
                    targetEntityIdList  = []
                    selfEntityId        = None
                    for allowedTargetIdx in range(0, len(spell["allowedTargetList"])):
                        targetEntityIdList.append(None)
                        if (spell["allowedTargetList"][allowedTargetIdx] == "all"):
                            pass

                        elif (spell["allowedTargetList"][allowedTargetIdx] == "allEntity"):
                            targetEntityIdList[-1] = self.entityIdOnTile(targetPositionList[allowedTargetIdx]["x"], targetPositionList[allowedTargetIdx]["y"])
                            if (targetEntityIdList[-1] != None):
                               pass
                            else:
                               raise GameException("An entity must be targeted !")

                        elif (spell["allowedTargetList"][allowedTargetIdx] == "emptyTile"):
                            targetEntityIdList[-1] = self.entityIdOnTile(targetPositionList[allowedTargetIdx]["x"], targetPositionList[allowedTargetIdx]["y"])
                            if (targetEntityIdList[-1] == None):
                                pass
                            else:
                               raise GameException("Target tile must be empty !")

                        elif (spell["allowedTargetList"][allowedTargetIdx] == "myEntity"):
                            pass

                        elif (spell["allowedTargetList"][allowedTargetIdx] == "opEntity"):
                            pass

                        elif (spell["allowedTargetList"][allowedTargetIdx] == "myPlayer"):
                            targetEntityIdList[-1] = self.entityIdOnTile(targetPositionList[allowedTargetIdx]["x"], targetPositionList[allowedTargetIdx]["y"])
                            if (targetEntityIdList[-1] == self._players[playerId].heroEntityId):
                                selfEntityId = self._players[playerId].heroEntityId
                            else:
                                raise GameException("Target must be in your team !")

                        elif (spell["allowedTargetList"][allowedTargetIdx] == "firstAlignedEntity"):
                            targetEntityIdList[-1] = self.entityIdOnTile(targetPositionList[allowedTargetIdx]["x"], targetPositionList[allowedTargetIdx]["y"])
                            if (targetEntityIdList[-1] in self.firstEntityIdAlignedToTile(self._entities[self._players[playerId].heroEntityId].x, self._entities[self._players[playerId].heroEntityId].y, "all")):
                                selfEntityId = self._players[playerId].heroEntityId
                            else:
                                raise GameException("Target is not the first aligned entity !")
                        else:
                            raise GameException("Wrong target type !")
                else:
                    raise GameException("Wrong number of target !")

                # Check conditions (TODO : Réfléchir à rajouter un argument booléen "break" aux abilities pour passer les check de condition uniquement dans les abilities)
                for condition in spell["conditionList"]:
                    # Set targetIdx
                    if ("targetIdx" in condition):
                        targetIdx = condition["targetIdx"]
                    else:
                        targetIdx = 0

                    if (condition["feature"] == "range"):
                        if (calcDist(self._entities[self._players[playerId].heroEntityId].x, self._entities[self._players[playerId].heroEntityId].y, targetPositionList[targetIdx]["x"], targetPositionList[targetIdx]["y"]) <= condition["value"]):
                            pass
                        else:
                            raise GameException("Target too far !")

                    elif (condition["feature"] == "rangeFromFirstTarget"):
                        if (calcDist(targetPositionList[0]["x"], targetPositionList[0]["y"], targetPositionList[targetIdx]["x"], targetPositionList[targetIdx]["y"]) <= condition["value"]):
                            pass
                        else:
                            raise GameException("Target too far !")

                    elif (condition["feature"] == "elemState"):
                        if (condition["value"] in ["oiled", "wet", "muddy", "windy"]):
                            if (self._entities[targetEntityIdList[targetIdx]].elemState == condition["value"]):
                                self._entities[targetEntityIdList[targetIdx]].setElemState("")
                            else:
                                conditionsValid = False
                        else:
                            raise GameException("ElemState to consume does not exist !")

                    else:
                        raise GameException("Condition not supported !")

                # Execute spell
                self.executeAbilities(spell["abilities"], "spellCast", playerId, selfEntityId, targetEntityIdList, positionList, spell["elem"])
                for entityId in range(0, len(self._entities)):
                    self.executeAbilities(self._entities[entityId].abilities, "spellCast", playerId, entityId, None, positionList, spell["elem"])

            else:
                raise GameException("Not enough pa to cast this spell !")
        else:
            raise GameException("Spell not in your hand !")

    def summon(self, playerId, companionId, summonPositionList):
        if (len(summonPositionList) == 1):
            # Check if companion available
            if (0 <= companionId < len(self._players[playerId].companions)):
                if (self._players[playerId].companions[companionId]["state"] == "available"):
                    companion = db.companions[self._players[playerId].companions[companionId]["descId"]]

                    # Check if the player ha enough gauges to summon
                    for gaugeType in list(companion["cost"].keys()):
                        self._players[playerId].modifyGauge(gaugeType, -companion["cost"][gaugeType])

                    # Check placement
                    placementValid = False
                    for placement in companion["placementList"]:
                        if (placement["ref"] == "ally"):
                            for allyEntityId in self._players[playerId].boardEntityIds:
                                if (calcDist(self._entities[allyEntityId].x, self._entities[allyEntityId].y, summonPositionList[0]["x"], summonPositionList[0]["y"]) <= placement["range"]):
                                    placementValid = True
                        elif (placement["ref"] == "myPlayer"):
                            if (calcDist(self._entities[self._players[playerId].heroEntityId].x, self._entities[self._players[playerId].heroEntityId].y, summonPositionList[0]["x"], summonPositionList[0]["y"]) <= placement["range"]):
                                placementValid = True
                        else:
                            raise GameException("Summon reference not allowed !")

                    # Summon
                    if placementValid:
                        entityId = self.appendEntity(playerId, companion["entityDescId"], self._players[playerId].team, summonPositionList[0]["x"], summonPositionList[0]["y"])
                        self._players[playerId].summonCompanion(companionId, entityId)

                    else:
                        raise GameException("Invalid companion placement !")
                else:
                    raise GameException("Companion not available !")
            else:
                raise GameException("Companion not in your deck !")
        else:
            raise GameException("Only one summon position is allowed !")

    def executeAbilities(self, abilityList, trigger, playerId, selfEntityId, targetEntityIdList, positionList, spellElem):
        auraUsed    = False
        opPlayerId  = self.getOpPlayerId(playerId)
        for ability in abilityList:
            if (trigger == ability["trigger"]):

                # Set targetIdx
                if ("targetIdx" in ability):
                    targetIdx = ability["targetIdx"]
                else:
                    targetIdx = 0

                # Check conditions
                conditionsValid = True
                for condition in ability["conditionList"]:
                    if (condition["feature"] == "elemState"):
                        if (condition["value"] in ["oiled", "wet", "muddy", "windy"]):
                            if (self._entities[targetEntityIdList[targetIdx]].elemState == condition["value"]):
                                self._entities[targetEntityIdList[targetIdx]].setElemState("")
                            else:
                                conditionsValid = False
                        else:
                            raise GameException("ElemState to consume does not exist !")

                    elif (condition["feature"] == "elem"):
                        if (condition["value"] in ["fire", "water", "earth", "air", "neutral"]):
                            if (spellElem == condition["value"]):
                                pass
                            else:
                                conditionsValid = False
                        else:
                            raise GameException("Elem of the spell does not exist !")

                    else:
                        raise GameException("Wrong ability condition !")

                # Choose abilityEntity
                if (ability["target"] == "target"):
                    abilityEntityId = targetEntityIdList[targetIdx]
                elif (ability["target"] == "self"):
                    abilityEntityId = selfEntityId
                elif (ability["target"] == "myPlayer"):
                    abilityEntityId = self._players[playerId].heroEntityId
                elif (ability["target"] == "opPlayer"):
                    abilityEntityId = self._players[opPlayerId].heroEntityId
                elif (ability["target"] == "tile"):
                    pass
                else:
                    raise GameException("Wrong ability target !")
                   
                # Execute ability
                executed = False
                if conditionsValid:
                    if (ability["behavior"] == ""):
                        if (ability["feature"] == "pv"):
                            self._entities[abilityEntityId].modifyPv(ability["value"])
                            executed = True
                        elif (ability["feature"] == "elemState"):
                            self._entities[abilityEntityId].setElemState(ability["value"])
                            executed = True
                        elif (ability["feature"] == "pm"):
                            self._entities[abilityEntityId].modifyPm(ability["value"])
                            executed = True
                        elif (ability["feature"] == "gauges"):
                            if isinstance(ability["value"], dict):
                                for gaugeType in list(ability["value"].keys()):
                                    self._players[playerId].modifyGauge(gaugeType, ability["value"][gaugeType])
                                    executed = True
                            else:
                                raise GameException("Ability value for gauges must be a dict !")
                        elif (ability["feature"] == "atk"):
                            self._entities[self._players[playerId].heroEntityId].modifyAtk(ability["value"])
                            executed = True
                        elif (ability["feature"] == "position"):
                            self._entities[self._players[playerId].heroEntityId].tp(positionList[targetIdx]["x"], positionList[targetIdx]["y"])
                            executed = True

                    elif (ability["behavior"] == "melee"):
                        if (ability["feature"] == "atk"): 
                            mult = len(self.entityIdAroundTile(self._entities[self._players[playerId].heroEntityId].x, self._entities[self._players[playerId].heroEntityId].y, self.getOpTeam(playerId)))
                            self._entities[self._players[playerId].heroEntityId].modifyAtk(mult*ability["value"])
                            executed = True
                        
                    elif (ability["behavior"] == "addAura"):
                        if (self._entities[self._players[playerId].heroEntityId].aura and ability["feature"] == self._entities[self._players[playerId].heroEntityId].aura["type"]):
                            self._entities[self._players[playerId].heroEntityId].addAura(ability["value"])
                            executed = True
                        else:
                            self._entities[self._players[playerId].heroEntityId].newAura(ability["feature"], ability["value"])
                            executed = True

                    elif (ability["behavior"] == "charge"):
                        if (self._entities[selfEntityId].x == self._entities[abilityEntity].x):
                            if (self._entities[selfEntityId].y < self._entities[abilityEntity].y):
                                self._entities[selfEntityId].tp(self._entities[selfEntityId].x, self._entities[abilityEntity].y - 1)
                                executed = True
                            elif (self._entities[selfEntityId].y > self._entities[abilityEntity].y):
                                self._entities[selfEntityId].tp(self._entities[selfEntityId].x, self._entities[abilityEntity].y + 1)
                                executed = True
                            else:
                                raise GameException("Target can't be on the same tile than selfEntity !")
                        elif (self._entities[selfEntityId].y == self._entities[abilityEntity].y):
                            if (self._entities[selfEntityId].x < self._entities[abilityEntity].x):
                                self._entities[selfEntityId].tp(self._entities[selfEntityId].x - 1, self._entities[abilityEntity].y)
                                executed = True
                            elif (self._entities[selfEntityId].x > self._entities[abilityEntity].x):
                                self._entities[selfEntityId].tp(self._entities[selfEntityId].x + 1, self._entities[abilityEntity].y)
                                executed = True
                            else:
                                raise GameException("Target can't be on the same tile than selfEntity !")
                        else:
                            raise GameException("Target not aligned with selfEntity !")

                    elif (ability["behavior"] == "explosion"):
                        for entityId in self.entityIdAroundTile(self._entities[abilityEntity].x, self._entities[abilityEntity].y, self.getOpTeam(playerId)):
                            self._entities[entityId].modifyPv(ability["value"])
                            executed = True

                # Check if an aura has been used
                if (executed and ability["behavior"] == "aura"):
                    auraUsed = True

        if auraUsed:
            self._entities[selfEntityId].modifyAuraNb(-1)