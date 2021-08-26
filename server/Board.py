from functions import *
from Player import *
from Entity import *
from Database import *
from GameException import *

class Board:

    def __init__(self):
        self._nextEntityId  = 0
        self._entitiesDict  = {}
        self._playersDict   = {}

    @property
    def entitiesDict(self):
        return dict(self._entitiesDict)

    @property
    def playersDict(self):
        return dict(self._playersDict)

    def appendPlayer(self, playerId, deck, team, pseudo):
        if (team == "blue"):
            x = BOARD_COLS - 1
            y = 0
        elif (team == "red"):
            x = 0
            y = BOARD_ROWS - 1
        self._playersDict[playerId] = Player(deck, team, pseudo)
        self._playersDict[playerId].setHeroEntityId(self.appendEntity(playerId, db.heroes[deck["heroDescId"]]["entityDescId"], team, x, y))

    # Return the entityId
    def appendEntity(self, playerId, entityDescId, team, x, y):
        if (self.entityIdOnTile(x, y) == None):
            self._entitiesDict[self._nextEntityId] = Entity(entityDescId, team, x, y)
            self._playersDict[playerId].addEntity(self._nextEntityId)
            self._nextEntityId +=1
            return self._nextEntityId - 1
        else:
            raise GameException("Tile is not empty !")

    def removeEntity(self, entityIdx):
        found = False
        for playerId in list(self._playersDict.keys()):
            if entityIdx in self._playersDict[playerId].boardEntityIds:
                self._playersDict[playerId].removeEntity(entityIdx)
                found = True
                break
        for state in self._entitiesDict[entityIdx].states:
            if (state["feature"] == "bodyguard"):
                rmState = {}
                rmState["feature"]  = "bodyguarded"
                rmState["value"]    = entityIdx
                self._entitiesDict[state["value"]].removeState(rmState)
                break
        del self._entitiesDict[entityIdx]
        if not(found):
            raise GameException("Entity to remove not found in playersDict entitiesDict list !")

    def garbageCollector(self):
        entityId = 0
        while (entityId < len(self._entitiesDict)):
            if (self._entitiesDict[entityId].pv <= 0):
                self.removeEntity(entityId)
                entityId = 0
            else:
                entityId += 1

    def getPlayerIdFromTeam(self, team):
        for pId in list(self._playersDict.keys()):
            if (self._playersDict[pId].team == team):
                return pId

    def getOpPlayerId(self, playerId):
        for pId in list(self._playersDict.keys()):
            if (pId != playerId):
                return pId

    def getOpTeam(self, team):
        if (team == "blue"):
            return "red"
        elif (team == "red"):
            return "blue"
        else:
            raise GameException(f"Team ({team}) does not exist !")

    def entityIdOnTile(self, x, y):
        for entityId in range(0, len(self._entitiesDict)):
            if ((self._entitiesDict[entityId].x == x) and (self._entitiesDict[entityId].y == y)):
                return entityId
        return None

    def entityIdAroundTile(self, x, y, team):
        entityIdList = []
        for xa in range(max(x-1, 0), min(x+2, BOARD_COLS)):
            for ya in range(max(y-1, 0), min(y+2, BOARD_ROWS)):
                if (xa != x or ya != y):
                    matchId = self.entityIdOnTile(xa, ya)
                    if (matchId != None):
                        if (team == "all" or team == self._entitiesDict[matchId].team):
                            entityIdList.append(matchId)
        return entityIdList

    def entityIdNextToTile(self, x, y, team):
        entityIdList = []
        matchId = self.entityIdOnTile(max(x-1, 0), y)
        if (matchId != None):
            if (team == "all" or team == self._entitiesDict[matchId].team):
                entityIdList.append(matchId)
        matchId = self.entityIdOnTile(min(x+1, BOARD_COLS), y)
        if (matchId != None):
            if (team == "all" or team == self._entitiesDict[matchId].team):
                entityIdList.append(matchId)
        matchId = self.entityIdOnTile(x, max(y-1, 0))
        if (matchId != None):
            if (team == "all" or team == self._entitiesDict[matchId].team):
                entityIdList.append(matchId)
        matchId = self.entityIdOnTile(x, min(y+1, BOARD_ROWS))
        if (matchId != None):
            if (team == "all" or team == self._entitiesDict[matchId].team):
                entityIdList.append(matchId)
        return entityIdList

    def entityIdAlignedToTile(self, x, y, team):
        entityIdList = []
        for xa in range(0, BOARD_COLS):
            if (xa != x):
                matchId = self.entityIdOnTile(xa, y)
                if (matchId != None):
                    if (team == "all" or team == self._entitiesDict[matchId].team):
                        entityIdList.append(matchId)
        for ya in range(0, BOARD_ROWS):
            if (ya != y):
                matchId = self.entityIdOnTile(x, ya)
                if (matchId != None):
                    if (team == "all" or team == self._entitiesDict[matchId].team):
                        entityIdList.append(matchId)
        return entityIdList

    def firstEntityIdAlignedToTile(self, x, y, team):
        entityIdList = []
        for xa in range(x-1, -1, -1):
            matchId = self.entityIdOnTile(xa, y)
            if (matchId != None):
                if (team == "all" or team == self._entitiesDict[matchId].team):
                    entityIdList.append(matchId)
                    break
        for xa in range(x+1, BOARD_COLS):
            matchId = self.entityIdOnTile(xa, y)
            if (matchId != None):
                if (team == "all" or team == self._entitiesDict[matchId].team):
                    entityIdList.append(matchId)
                    break
        for ya in range(y-1, -1, -1):
            matchId = self.entityIdOnTile(x, ya)
            if (matchId != None):
                if (team == "all" or team == self._entitiesDict[matchId].team):
                    entityIdList.append(matchId)
                    break
        for ya in range(y+1, BOARD_ROWS):
            matchId = self.entityIdOnTile(x, ya)
            if (matchId != None):
                if (team == "all" or team == self._entitiesDict[matchId].team):
                    entityIdList.append(matchId)
                    break
        return entityIdList

    def startTurn(self, playerId):
        self._playersDict[playerId].startTurn()
        for entityId in self._playersDict[playerId].boardEntityIds:
            self._entitiesDict[entityId].startTurn()

    def endTurn(self, playerId):
        self._playersDict[playerId].endTurn()
        for entityId in self._playersDict[playerId].boardEntityIds:
            self._entitiesDict[entityId].endTurn()

    def useReserve(self, playerId):
        self._playersDict[playerId].useReserve()

    # This function is called after each action
    def always(self):
        self.garbageCollector()
        for entityId in range(0, len(self._entitiesDict)):
            self.executeAbilities(self._entitiesDict[entityId].abilities, "always", self.getPlayerIdFromTeam(self._entitiesDict[entityId].team), entityId, None, [], None)

    def moveEntity(self, playerId, entityId, path):
        x               = self._entitiesDict[entityId].x
        y               = self._entitiesDict[entityId].y
        pm              = self._entitiesDict[entityId].pm
        attackedEntity  = -1
        if (self._entitiesDict[entityId].canMove):
            if (path[0]["x"] == x and path[0]["y"] == y): # The path is given with the inital position of the entity
                path.pop(0)
                for tile in path:
                    nextX = tile["x"]
                    nextY = tile["y"]
                    if (0 <= nextX < BOARD_COLS and 0 <= nextY < BOARD_ROWS):
                        if (abs(x - nextX) + abs(y - nextY) == 1):
                            if (pm == 0):
                                if (self._entitiesDict[entityId].canAttack and self.entityIdOnTile(nextX, nextY) != None): # Attack after full pm move
                                    attackedEntityId  = self.entityIdOnTile(nextX, nextY)
                                    self.executeAbilities(self._entitiesDict[entityId].abilities, "attack", playerId, entityId, [attackedEntityId], [], None)
                                    self.executeAbilities(self._entitiesDict[attackedEntityId].abilities, "attacked", playerId, attackedEntityId, None, [], None)
                                    pm              = -1
                                else:
                                    raise GameException("Path length is higher than your pm !")
                            else:
                                if (self.entityIdOnTile(nextX, nextY) == None): # The next tile is empty
                                    x             = nextX
                                    y             = nextY
                                    pm            -= 1
                                else: # There is an entity on next tile
                                    if (self._entitiesDict[entityId].canAttack):
                                        attackedEntityId  = self.entityIdOnTile(nextX, nextY)
                                        self.executeAbilities(self._entitiesDict[entityId].abilities, "attack", playerId, entityId, [attackedEntityId], [], None)
                                        self.executeAbilities(self._entitiesDict[attackedEntityId].abilities, "attacked", playerId, attackedEntityId, None, [], None)
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

        self._entitiesDict[entityId].move(x, y)
        self.executeAbilities(self._entitiesDict[entityId].abilities, "move", playerId, entityId, [], [], None)

    def spellCast(self, playerId, spellId, targetPositionList):
        # Check if spell in hand
        if (0 <= spellId < len(self._playersDict[playerId].handSpellDescIds)):
            spell = db.spells[self._playersDict[playerId].handSpellDescIds[spellId]]

            # Check if there is enough PA to play the spell
            if (spell["cost"] <= self._playersDict[playerId].pa):
                self._playersDict[playerId].playSpell(spellId, spell["cost"])

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
                            if (targetEntityIdList[-1] == self._playersDict[playerId].heroEntityId):
                                selfEntityId = self._playersDict[playerId].heroEntityId
                            else:
                                raise GameException("Target must be in your team !")

                        elif (spell["allowedTargetList"][allowedTargetIdx] == "firstAlignedEntity"):
                            targetEntityIdList[-1] = self.entityIdOnTile(targetPositionList[allowedTargetIdx]["x"], targetPositionList[allowedTargetIdx]["y"])
                            if (targetEntityIdList[-1] in self.firstEntityIdAlignedToTile(self._entitiesDict[self._playersDict[playerId].heroEntityId].x, self._entitiesDict[self._playersDict[playerId].heroEntityId].y, "all")):
                                selfEntityId = self._playersDict[playerId].heroEntityId
                            else:
                                raise GameException("Target is not the first aligned entity !")
                        else:
                            raise GameException("Wrong target type !")
                else:
                    raise GameException("Wrong number of target !")

                # Execute spell
                self.executeAbilities(spell["abilities"], "spellCast", playerId, selfEntityId, targetEntityIdList, positionList, spell["elem"])
                for entityId in range(0, len(self._entitiesDict)):
                    self.executeAbilities(self._entitiesDict[entityId].abilities, "spellCast", playerId, entityId, None, positionList, spell["elem"])

            else:
                raise GameException("Not enough pa to cast this spell !")
        else:
            raise GameException("Spell not in your hand !")

    def summon(self, playerId, companionId, summonPositionList):
        if (len(summonPositionList) == 1):
            # Check if companion available
            if (0 <= companionId < len(self._playersDict[playerId].companions)):
                if (self._playersDict[playerId].companions[companionId]["state"] == "available"):
                    companion = db.companions[self._playersDict[playerId].companions[companionId]["descId"]]

                    # Check if the player have enough gauges to summon
                    for gaugeType in list(companion["cost"].keys()):
                        self._playersDict[playerId].modifyGauge(gaugeType, -companion["cost"][gaugeType])

                    # Check placement
                    placementValid = False
                    for placement in companion["placementList"]:
                        if (placement["ref"] == "ally"):
                            for allyEntityId in self._playersDict[playerId].boardEntityIds:
                                if (calcDist(self._entitiesDict[allyEntityId].x, self._entitiesDict[allyEntityId].y, summonPositionList[0]["x"], summonPositionList[0]["y"]) <= placement["range"]):
                                    placementValid = True
                        elif (placement["ref"] == "myPlayer"):
                            if (calcDist(self._entitiesDict[self._playersDict[playerId].heroEntityId].x, self._entitiesDict[self._playersDict[playerId].heroEntityId].y, summonPositionList[0]["x"], summonPositionList[0]["y"]) <= placement["range"]):
                                placementValid = True
                        else:
                            raise GameException("Summon reference not allowed !")

                    # Summon
                    if placementValid:
                        entityId = self.appendEntity(playerId, companion["entityDescId"], self._playersDict[playerId].team, summonPositionList[0]["x"], summonPositionList[0]["y"])
                        self.executeAbilities(self._entitiesDict[entityId].abilities, "spawn", playerId, entityId, None, {}, None)
                        self._playersDict[playerId].summonCompanion(companionId, entityId)

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
        opPlayerId  = self.getOpPlayerId(playerId) if playerId else ""
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
                            if (self._entitiesDict[targetEntityIdList[targetIdx]].elemState == condition["value"]):
                                self._entitiesDict[targetEntityIdList[targetIdx]].setElemState("")
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

                    elif (condition["feature"] == "allyCompanions"):
                        allyCompanions = 0
                        for companion in self._playersDict[playerId].companions:
                            if (companion["state"] == "alive"):
                                allyCompanions += 1

                        if (allyCompanions == condition["value"]):
                            pass
                        else:
                            conditionsValid = False

                    elif (condition["feature"] == "range"):
                        if (calcDist(self._entitiesDict[self._playersDict[playerId].heroEntityId].x, self._entitiesDict[self._playersDict[playerId].heroEntityId].y, positionList[targetIdx]["x"], positionList[targetIdx]["y"]) <= condition["value"]):
                            pass
                        else:
                            conditionsValid = False

                    elif (condition["feature"] == "rangeFromFirstTarget"):
                        if (calcDist(positionList[0]["x"], positionList[0]["y"], positionList[targetIdx]["x"], positionList[targetIdx]["y"]) <= condition["value"]):
                            pass
                        else:
                            conditionsValid = False

                    else:
                        raise GameException("Wrong ability condition !")

                if (not(conditionsValid) and ability["break"] == "True"):
                    raise GameException(f"The condition {condition['feature']} is not respected !")

                # Choose abilityEntity
                if (ability["target"] == "target"):
                    abilityEntityIdList = [targetEntityIdList[targetIdx]]
                elif (ability["target"] == "self"):
                    abilityEntityIdList = [selfEntityId]
                elif (ability["target"] == "targetPlayer"):
                    abilityEntityIdList = [self._playersDict[self.getPlayerIdFromTeam(self._entitiesDict[targetEntityIdList[targetIdx]].team)].heroEntityId]
                elif (ability["target"] == "myPlayer"):
                    abilityEntityIdList = [self._playersDict[playerId].heroEntityId]
                elif (ability["target"] == "opPlayer"):
                    abilityEntityIdList = [self._playersDict[opPlayerId].heroEntityId]
                elif (ability["target"] == "around"):
                    abilityEntityIdList = self.entityIdAroundTile(self._entitiesDict[selfEntityId].x, self._entitiesDict[selfEntityId].y, "all")
                elif (ability["target"] == "opAround"):
                    abilityEntityIdList = self.entityIdAroundTile(self._entitiesDict[selfEntityId].x, self._entitiesDict[selfEntityId].y, self.getOpTeam(self._entitiesDict[selfEntityId].team))
                elif (ability["target"] == "allyAround"):
                    abilityEntityIdList = self.entityIdAroundTile(self._entitiesDict[selfEntityId].x, self._entitiesDict[selfEntityId].y, self._entitiesDict[selfEntityId].team)
                elif (ability["target"] == "tile"):
                    pass
                else:
                    raise GameException("Wrong ability target !")

                # Handle variable value case
                if isinstance(ability["value"], int):
                    value = ability["value"]
                elif isinstance(ability["value"], dict):
                    value = ability["value"]
                elif isinstance(ability["value"], str):
                    if (ability["value"] == "-atk"):
                        value = -self._entitiesDict[selfEntityId].atk
                    elif (ability["value"] == "atk"):
                        value = self._entitiesDict[selfEntityId].atk
                    else:
                        value = ability["value"]
                else:
                    raise GameException(f"Ability value {ability['value']} must be an int, an str or a dict !")
                   
                # Execute ability
                executed = False
                if conditionsValid:
                    if (ability["behavior"] in ["", "aura"]):
                        if (ability["feature"] == "pv"):
                            for abilityEntityId in abilityEntityIdList:
                                guarded = False
                                if (value < 0):
                                    for state in self._entitiesDict[abilityEntityId].states:
                                        if (state["feature"] == "bodyguarded"):
                                            guardId = state["value"]
                                            guarded = True
                                            break
                                if guarded:
                                    self._entitiesDict[guardId].modifyPv(value)
                                else:
                                    self._entitiesDict[abilityEntityId].modifyPv(value)
                                executed = True
                        elif (ability["feature"] == "elemState"):
                            for abilityEntityId in abilityEntityIdList:
                                self._entitiesDict[abilityEntityId].setElemState(value)
                                executed = True
                        elif (ability["feature"] == "pm"):
                            for abilityEntityId in abilityEntityIdList:
                                self._entitiesDict[abilityEntityId].modifyPm(value)
                                executed = True
                        elif (ability["feature"] == "gauges"):
                            if isinstance(value, dict):
                                for gaugeType in list(value.keys()):
                                    self._playersDict[playerId].modifyGauge(gaugeType, value[gaugeType])
                                    executed = True
                            else:
                                raise GameException("Ability value for gauges must be a dict !")
                        elif (ability["feature"] == "atk"):
                            for abilityEntityId in abilityEntityIdList:
                                self._entitiesDict[abilityEntityId].modifyAtk(value)
                                executed = True
                        elif (ability["feature"] == "position"):
                            self._entitiesDict[self._playersDict[playerId].heroEntityId].tp(positionList[targetIdx]["x"], positionList[targetIdx]["y"])
                            executed = True
                        elif (ability["feature"] == "paStock"):
                            self._playersDict[playerId].modifyPaStock(value)
                            executed = True

                    elif (ability["behavior"] == "melee"):
                        if (ability["feature"] == "atk"): 
                            mult = len(self.entityIdAroundTile(self._entitiesDict[self._playersDict[playerId].heroEntityId].x, self._entitiesDict[self._playersDict[playerId].heroEntityId].y, self._playersDict[self.getOpPlayerId(playerId)].team))
                            self._entitiesDict[self._playersDict[playerId].heroEntityId].modifyAtk(mult*value)
                            executed = True
                        
                    elif (ability["behavior"] == "addAura"):
                        if (self._entitiesDict[self._playersDict[playerId].heroEntityId].aura and ability["feature"] == self._entitiesDict[self._playersDict[playerId].heroEntityId].aura["type"]):
                            self._entitiesDict[self._playersDict[playerId].heroEntityId].addAura(value)
                            executed = True
                        else:
                            self._entitiesDict[self._playersDict[playerId].heroEntityId].newAura(ability["feature"], value)
                            executed = True

                    elif (ability["behavior"] == "charge"):
                        for abilityEntityId in abilityEntityIdList:
                            if (self._entitiesDict[selfEntityId].x == self._entitiesDict[abilityEntityId].x):
                                if (self._entitiesDict[selfEntityId].y < self._entitiesDict[abilityEntityId].y):
                                    self._entitiesDict[selfEntityId].tp(self._entitiesDict[selfEntityId].x, self._entitiesDict[abilityEntityId].y - 1)
                                    executed = True
                                elif (self._entitiesDict[selfEntityId].y > self._entitiesDict[abilityEntityId].y):
                                    self._entitiesDict[selfEntityId].tp(self._entitiesDict[selfEntityId].x, self._entitiesDict[abilityEntityId].y + 1)
                                    executed = True
                                else:
                                    raise GameException("Target can't be on the same tile than selfEntity !")
                            elif (self._entitiesDict[selfEntityId].y == self._entitiesDict[abilityEntityId].y):
                                if (self._entitiesDict[selfEntityId].x < self._entitiesDict[abilityEntityId].x):
                                    self._entitiesDict[selfEntityId].tp(self._entitiesDict[selfEntityId].x - 1, self._entitiesDict[abilityEntityId].y)
                                    executed = True
                                elif (self._entitiesDict[selfEntityId].x > self._entitiesDict[abilityEntityId].x):
                                    self._entitiesDict[selfEntityId].tp(self._entitiesDict[selfEntityId].x + 1, self._entitiesDict[abilityEntityId].y)
                                    executed = True
                                else:
                                    raise GameException("Target can't be on the same tile than selfEntity !")
                            else:
                                raise GameException("Target not aligned with selfEntity !")

                    elif (ability["behavior"] == "explosion"):
                        for abilityEntityId in abilityEntityIdList:
                            for entityId in self.entityIdAroundTile(self._entitiesDict[abilityEntityId].x, self._entitiesDict[abilityEntityId].y, self._playersDict[self.getOpPlayerId(playerId)].team):
                                self._entitiesDict[entityId].modifyPv(value)
                                executed = True

                    elif (ability["behavior"] == "state"):
                        state = {}
                        for abilityEntityId in abilityEntityIdList:
                            if (ability["feature"] == "bodyguard"):
                                state["feature"]    = "bodyguard"
                                state["value"]      = abilityEntityId
                                self._entitiesDict[selfEntityId].addState(state)
                                state["feature"]    = "bodyguarded"
                                state["value"]      = selfEntityId
                                self._entitiesDict[abilityEntityId].addState(state)
                            else:
                                state["feature"]    = ability["feature"]
                                state["value"]      = value
                                self._entitiesDict[abilityEntityId].addState(state)
                else:
                    if (ability["behavior"] == "state"):
                        state = {}
                        for abilityEntityId in abilityEntityIdList:
                            state["feature"]    = ability["feature"]
                            state["value"]      = value
                            self._entitiesDict[abilityEntityId].removeState(state)

                # Check if an aura has been used
                if (executed and ability["behavior"] == "aura"):
                    auraUsed = True

        if auraUsed:
            self._entitiesDict[selfEntityId].modifyAuraNb(-1)