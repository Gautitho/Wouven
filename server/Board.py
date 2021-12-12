import traceback
from functions import *
from Player import *
from Entity import *
from Database import *
from GameException import *
from Spell import *

class Board:

    def __init__(self):
        self._nextEntityId      = 0
        self._entitiesDict      = {}
        self._playersDict       = {}
        self._ongoingAbilityList = []

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
        entityIdx = 0
        while (entityIdx < len(list(self._entitiesDict.keys()))):
            if (self._entitiesDict[list(self._entitiesDict.keys())[entityIdx]].pv <= 0):
                self.removeEntity(list(self._entitiesDict.keys())[entityIdx])
                entityIdx = 0
            else:
                entityIdx += 1

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

    def entityIdAligned(self, xStart, yStart, xDir, yDir, rangeCondition, team):
        entityIdList = []
        if (yStart == yDir):
            if (xDir > xStart):
                for x in range(xStart + 1, min(xStart + rangeCondition + 1, BOARD_COLS)):
                    matchId = self.entityIdOnTile(x, yStart)
                    if (matchId != None):
                        if (team == "all" or team == self._entitiesDict[matchId].team):
                            entityIdList.append(matchId)
            elif (xDir < xStart):
                for x in range(xStart - 1, min(xStart - rangeCondition - 1, -1), -1):
                    matchId = self.entityIdOnTile(x, yStart)
                    if (matchId != None):
                        if (team == "all" or team == self._entitiesDict[matchId].team):
                            entityIdList.append(matchId)
        elif (xStart == xDir):
            if (yDir > yStart):
                for y in range(yStart + 1, min(yStart + rangeCondition + 1, BOARD_ROWS)):
                    matchId = self.entityIdOnTile(xStart, y)
                    if (matchId != None):
                        if (team == "all" or team == self._entitiesDict[matchId].team):
                            entityIdList.append(matchId)
            elif (yDir < yStart):
                for y in range(yStart - 1, min(yStart - rangeCondition - 1, -1), -1):
                    matchId = self.entityIdOnTile(xStart, y)
                    if (matchId != None):
                        if (team == "all" or team == self._entitiesDict[matchId].team):
                            entityIdList.append(matchId)
        return entityIdList

    def entityIdInCross(self, x, y, rangeCondition, team):
        entityIdList = []
        for xa in range(max(x-rangeCondition, 0), min(x+rangeCondition+1, BOARD_COLS)):
            for ya in range(max(y-rangeCondition, 0), min(y+rangeCondition+1, BOARD_ROWS)):
                matchId = self.entityIdOnTile(xa, ya)
                if (matchId != None):
                    if (team == "all" or team == self._entitiesDict[matchId].team):
                        entityIdList.append(matchId)
        return entityIdList

    def isAdjacentToTile(self, xSelf, ySelf, xTarget, yTarget):
        return ((xTarget == xSelf and (yTarget == ySelf + 1 or yTarget == ySelf - 1)) or (yTarget == ySelf and (xTarget == xSelf + 1 or xTarget == xSelf - 1)))

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
        self.removeOngoingAbilities("always")
        for entityId in list(self._entitiesDict.keys()):
            self.executeAbilities(self._entitiesDict[entityId].abilities, "always", self.getPlayerIdFromTeam(self._entitiesDict[entityId].team), entityId, None, [], None)
        for playerId in list(self._playersDict.keys()):
            for spellId in range(0, len(self._playersDict[playerId].handSpellList)):
                self.executeAbilities(self._playersDict[playerId].handSpellList[spellId].abilities, "always", playerId, spellId, [], [], None)
        self.garbageCollector()

    def moveEntity(self, playerId, entityId, path):
        x               = self._entitiesDict[entityId].x
        y               = self._entitiesDict[entityId].y
        pm              = self._entitiesDict[entityId].pm
        attackedEntity  = -1
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
                                if (self._entitiesDict[entityId].canMove):
                                    x             = nextX
                                    y             = nextY
                                    pm            -= 1
                                else:
                                    raise GameException("You can't move anymore this turn !")
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
            raise GameException("First tile of the path must be the current entity position !")

        self._entitiesDict[entityId].move(x, y)
        self.executeAbilities(self._entitiesDict[entityId].abilities, "move", playerId, entityId, [], [], None)

    def pushEntity(self, entityId, x, y, distance):
        xe  = self._entitiesDict[entityId].x
        ye  = self._entitiesDict[entityId].y
        remainingDistance = distance
        nextX = xe
        nextY = ye
        if (x == xe and y == ye):
            pass
        elif (x == xe and y == ye + 1):
            while (0 <= nextY + 1 < BOARD_ROWS and self.entityIdOnTile(nextX, nextY + 1) == None and remainingDistance > 0):
                remainingDistance -= 1
                nextY += 1
        elif (x == xe and y == ye - 1):
            while (0 <= nextY - 1 < BOARD_ROWS and self.entityIdOnTile(nextX, nextY - 1) == None and remainingDistance > 0):
                remainingDistance -= 1
                nextY -= 1
        elif (x == xe + 1 and y == ye):
            while (0 <= nextX + 1 < BOARD_COLS and self.entityIdOnTile(nextX + 1, nextY) == None and remainingDistance > 0):
                remainingDistance -= 1
                nextX += 1
        elif (x == xe - 1 and y == ye):
            while (0 <= nextX - 1 < BOARD_COLS and self.entityIdOnTile(nextX - 1, nextY) == None and remainingDistance > 0):
                remainingDistance -= 1
                nextX -= 1
        else:
            raise GameException("To push, the second target tile must adjacent to the first target !")
        self._entitiesDict[entityId].tp(nextX, nextY)

    def spellCast(self, playerId, spellId, targetPositionList):
        # Check if spell in hand
        if (0 <= spellId < len(self._playersDict[playerId].handSpellList)):
            spell = self._playersDict[playerId].handSpellList[spellId]

            # Check if there is enough PA to play the spell
            if (spell.cost <= self._playersDict[playerId].pa):
                self._playersDict[playerId].playSpell(spellId)
                for playerEntityId in self._playersDict[playerId].boardEntityIds:
                    for state in self._entitiesDict[playerEntityId].states:
                        if (state["feature"] == "frozen"):
                            self._entitiesDict[playerEntityId].modifyPv(state["value"])

                # Check allowed targets
                if (len(spell.allowedTargetList) == len(targetPositionList)):
                    positionList        = targetPositionList
                    targetEntityIdList  = []
                    selfEntityId        = None
                    for allowedTargetIdx in range(0, len(spell.allowedTargetList)):
                        targetEntityIdList.append(None)
                        if (spell.allowedTargetList[allowedTargetIdx] == "all"):
                            pass

                        elif (spell.allowedTargetList[allowedTargetIdx] == "emptyTile"):
                            targetEntityIdList[-1] = self.entityIdOnTile(targetPositionList[allowedTargetIdx]["x"], targetPositionList[allowedTargetIdx]["y"])
                            if (targetEntityIdList[-1] == None):
                                pass
                            else:
                               raise GameException("Target tile must be empty !")

                        elif (spell.allowedTargetList[allowedTargetIdx] == "allEntity"):
                            targetEntityIdList[-1] = self.entityIdOnTile(targetPositionList[allowedTargetIdx]["x"], targetPositionList[allowedTargetIdx]["y"])
                            if (targetEntityIdList[-1] != None):
                               pass
                            else:
                               raise GameException("An entity must be targeted !")

                        elif (spell.allowedTargetList[allowedTargetIdx] == "allOrganic"):
                            targetEntityIdList[-1] = self.entityIdOnTile(targetPositionList[allowedTargetIdx]["x"], targetPositionList[allowedTargetIdx]["y"])
                            if (targetEntityIdList[-1] != None and not("mechanism" in self._entitiesDict[targetEntityIdList[-1]].types)):
                               pass
                            else:
                               raise GameException("An entity, not mechanism, must be targeted !")

                        elif (spell.allowedTargetList[allowedTargetIdx] == "allMechanism"):
                            targetEntityIdList[-1] = self.entityIdOnTile(targetPositionList[allowedTargetIdx]["x"], targetPositionList[allowedTargetIdx]["y"])
                            if (targetEntityIdList[-1] != None and "mechanism" in self._entitiesDict[targetEntityIdList[-1]].types):
                               pass
                            else:
                               raise GameException("An entity, mechanism, must be targeted !")

                        elif (spell.allowedTargetList[allowedTargetIdx] == "myEntity"):
                            targetEntityIdList[-1] = self.entityIdOnTile(targetPositionList[allowedTargetIdx]["x"], targetPositionList[allowedTargetIdx]["y"])
                            if (targetEntityIdList[-1] != None and self._entitiesDict[targetEntityIdList[-1]].team == self._playersDict[playerId].team):
                               pass
                            else:
                               raise GameException("An entity, owned by you, must be targeted !")

                        elif (spell.allowedTargetList[allowedTargetIdx] == "myOrganic"):
                            targetEntityIdList[-1] = self.entityIdOnTile(targetPositionList[allowedTargetIdx]["x"], targetPositionList[allowedTargetIdx]["y"])
                            if (targetEntityIdList[-1] != None and self._entitiesDict[targetEntityIdList[-1]].team == self._playersDict[playerId].team and not("mechanism" in self._entitiesDict[targetEntityIdList[-1]].types)):
                               pass
                            else:
                               raise GameException("An entity, owned by you, not mechanism, must be targeted !")

                        elif (spell.allowedTargetList[allowedTargetIdx] == "myMechanism"):
                            targetEntityIdList[-1] = self.entityIdOnTile(targetPositionList[allowedTargetIdx]["x"], targetPositionList[allowedTargetIdx]["y"])
                            if (targetEntityIdList[-1] != None and self._entitiesDict[targetEntityIdList[-1]].team == self._playersDict[playerId].team and "mechanism" in self._entitiesDict[targetEntityIdList[-1]].types):
                               pass
                            else:
                               raise GameException("An entity, owned by you, mechanism, must be targeted !")

                        elif (spell.allowedTargetList[allowedTargetIdx] == "opEntity"):
                            targetEntityIdList[-1] = self.entityIdOnTile(targetPositionList[allowedTargetIdx]["x"], targetPositionList[allowedTargetIdx]["y"])
                            if (targetEntityIdList[-1] != None and self._entitiesDict[targetEntityIdList[-1]].team == self._playersDict[self.getOpPlayerId(playerId)].team):
                               pass
                            else:
                               raise GameException("An entity, owned by your opponent, must be targeted !")

                        elif (spell.allowedTargetList[allowedTargetIdx] == "opOrganic"):
                            targetEntityIdList[-1] = self.entityIdOnTile(targetPositionList[allowedTargetIdx]["x"], targetPositionList[allowedTargetIdx]["y"])
                            if (targetEntityIdList[-1] != None and self._entitiesDict[targetEntityIdList[-1]].team == self._playersDict[self.getOpPlayerId(playerId)].team and not("mechanism" in self._entitiesDict[targetEntityIdList[-1]].types)):
                               pass
                            else:
                               raise GameException("An entity, owned by your opponent, not mechanism, must be targeted !")

                        elif (spell.allowedTargetList[allowedTargetIdx] == "opMechanism"):
                            targetEntityIdList[-1] = self.entityIdOnTile(targetPositionList[allowedTargetIdx]["x"], targetPositionList[allowedTargetIdx]["y"])
                            if (targetEntityIdList[-1] != None and self._entitiesDict[targetEntityIdList[-1]].team == self._playersDict[self.getOpPlayerId(playerId)].team and "mechanism" in self._entitiesDict[targetEntityIdList[-1]].types):
                               pass
                            else:
                               raise GameException("An entity, owned by your opponent, not mechanism, must be targeted !")

                        elif (spell.allowedTargetList[allowedTargetIdx] == "myPlayer"):
                            targetEntityIdList[-1] = self.entityIdOnTile(targetPositionList[allowedTargetIdx]["x"], targetPositionList[allowedTargetIdx]["y"])
                            if (targetEntityIdList[-1] == self._playersDict[playerId].heroEntityId):
                                selfEntityId = self._playersDict[playerId].heroEntityId
                            else:
                                raise GameException("Target must be your hero !")

                        elif (spell.allowedTargetList[allowedTargetIdx] == "opPlayer"):
                            targetEntityIdList[-1] = self.entityIdOnTile(targetPositionList[allowedTargetIdx]["x"], targetPositionList[allowedTargetIdx]["y"])
                            if (targetEntityIdList[-1] == self._playersDict[self.getOpPlayerId(playerId)].heroEntityId):
                                selfEntityId = self._playersDict[self.getOpPlayerId(playerId)].heroEntityId
                            else:
                                raise GameException("Target must be opponent hero !")

                        elif (spell.allowedTargetList[allowedTargetIdx] == "allfirstAlignedEntity"):
                            targetEntityIdList[-1] = self.entityIdOnTile(targetPositionList[allowedTargetIdx]["x"], targetPositionList[allowedTargetIdx]["y"])
                            if (targetEntityIdList[-1] in self.firstEntityIdAlignedToTile(self._entitiesDict[self._playersDict[playerId].heroEntityId].x, self._entitiesDict[self._playersDict[playerId].heroEntityId].y, "all")):
                                selfEntityId = self._playersDict[playerId].heroEntityId
                            else:
                                raise GameException("Target is not the first aligned entity !")

                        elif (spell.allowedTargetList[allowedTargetIdx] == "allfirstAlignedOrganic"):
                            targetEntityIdList[-1] = self.entityIdOnTile(targetPositionList[allowedTargetIdx]["x"], targetPositionList[allowedTargetIdx]["y"])
                            if (targetEntityIdList[-1] in self.firstEntityIdAlignedToTile(self._entitiesDict[self._playersDict[playerId].heroEntityId].x, self._entitiesDict[self._playersDict[playerId].heroEntityId].y, "all") and not("mechanism" in self._entitiesDict[targetEntityIdList[-1]].types)):
                                selfEntityId = self._playersDict[playerId].heroEntityId
                            else:
                                raise GameException("Target is not the first, not mechanism, aligned entity !")

                        elif (spell.allowedTargetList[allowedTargetIdx] == "heroAdjacentTile"):
                            if (self.isAdjacentToTile(self._entitiesDict[self._playersDict[playerId].heroEntityId].x, self._entitiesDict[self._playersDict[playerId].heroEntityId].y, targetPositionList[allowedTargetIdx]["x"], targetPositionList[allowedTargetIdx]["y"])):
                                targetEntityIdList[-1] = self.entityIdOnTile(targetPositionList[allowedTargetIdx]["x"], targetPositionList[allowedTargetIdx]["y"])
                                selfEntityId = self._playersDict[playerId].heroEntityId
                            else:
                                raise GameException("Target must be adjacent to your hero !")

                        elif (spell.allowedTargetList[allowedTargetIdx] == "firstTargetAdjacentTile"):
                            if (self.isAdjacentToTile(targetPositionList[0]["x"], targetPositionList[0]["y"], targetPositionList[allowedTargetIdx]["x"], targetPositionList[allowedTargetIdx]["y"]) or (targetPositionList[0]["x"] == targetPositionList[allowedTargetIdx]["x"] and targetPositionList[0]["y"] == targetPositionList[allowedTargetIdx]["y"])):
                                pass
                            else:
                                raise GameException("Second target must be adjacent to first target !")

                        else:
                            raise GameException("Wrong target type !")
                else:
                    raise GameException("Wrong number of target !")

                # Execute spell
                self.removeOngoingAbilities("spellCast") # WARNING : This line is here only because, for now, the only spellCast ongoingAbilities affect cost
                self.executeAbilities(spell.abilities, "spellCast", playerId, selfEntityId, targetEntityIdList, positionList, spell.elem)
                for entityId in range(0, len(self._entitiesDict)):
                    self.executeAbilities(self._entitiesDict[entityId].abilities, "spellCast", playerId, entityId, targetEntityIdList, positionList, spell.elem)

            else:
                raise GameException("Not enough pa to cast this spell !")
        else:
            raise GameException("Spell not in your hand !")

    def summon(self, playerId, companionId, summonPositionList):
        if (len(summonPositionList) == 1):
            # Check if companion available
            if (0 <= companionId < len(self._playersDict[playerId].companionList)):
                if (self._playersDict[playerId].companionList[companionId]["state"] == "available"):
                    companion = db.companions[self._playersDict[playerId].companionList[companionId]["descId"]]

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

    def executeAbilities(self, abilityList, trigger, playerId, selfId, targetEntityIdList, positionList, spellElem, force=False):
        auraUsed    = False
        opPlayerId  = self.getOpPlayerId(playerId) if playerId else ""
        for ability in abilityList:
            if (trigger == ability["trigger"] or force):

                # Set targetIdx
                if ("targetIdx" in ability):
                    targetIdx = ability["targetIdx"]
                else:
                    targetIdx = 0

                # Set stopTrigger
                if ("stopTrigger" in ability):
                    stopTrigger = ability["stopTrigger"]
                else:
                    stopTrigger = ""

                # Check conditions
                conditionsValid = True
                for condition in ability["conditionList"]:
                    if ("operator" in condition):
                        operator = condition["operator"]
                    else:
                        operator = "="
                    if (condition["feature"] == "elemState"):
                        if (operator == "=" and condition["value"] in ["oiled", "wet", "muddy", "windy"]):
                            if (self._entitiesDict[targetEntityIdList[targetIdx]].elemState == condition["value"]):
                                self._entitiesDict[targetEntityIdList[targetIdx]].setElemState("")
                            else:
                                conditionsValid = False
                        else:
                            raise GameException("ElemState to consume does not exist !")

                    elif (condition["feature"] == "elem"):
                        if (operator == "=" and condition["value"] in ["fire", "water", "earth", "air", "neutral"]):
                            if (spellElem == condition["value"]):
                                pass
                            else:
                                conditionsValid = False
                        else:
                            raise GameException("Elem of the spell does not exist !")

                    elif (condition["feature"] == "allyCompanions"):
                        allyCompanions = 0
                        for companion in self._playersDict[playerId].companionList:
                            if (companion["state"] == "alive"):
                                allyCompanions += 1

                        if (operator == "=" and allyCompanions == condition["value"]):
                            pass
                        else:
                            conditionsValid = False

                    elif (condition["feature"] == "range"):
                        if (operator == "=" and calcDist(self._entitiesDict[self._playersDict[playerId].heroEntityId].x, self._entitiesDict[self._playersDict[playerId].heroEntityId].y, positionList[targetIdx]["x"], positionList[targetIdx]["y"]) == condition["value"]):
                            rangeCondition = condition["value"]
                        elif (operator == "<=" and calcDist(self._entitiesDict[self._playersDict[playerId].heroEntityId].x, self._entitiesDict[self._playersDict[playerId].heroEntityId].y, positionList[targetIdx]["x"], positionList[targetIdx]["y"]) <= condition["value"]):
                            rangeCondition = condition["value"]
                        else:
                            conditionsValid = False

                    elif (condition["feature"] == "rangeFromFirstTarget"):
                        if (operator == "=" and calcDist(positionList[0]["x"], positionList[0]["y"], positionList[targetIdx]["x"], positionList[targetIdx]["y"]) == condition["value"]):
                            pass
                        elif (operator == "<=" and calcDist(positionList[0]["x"], positionList[0]["y"], positionList[targetIdx]["x"], positionList[targetIdx]["y"]) <= condition["value"]):
                            pass
                        else:
                            conditionsValid = False

                    elif (condition["feature"] == "target"):
                        if (condition["value"] == "opOrganic"):
                            if (targetEntityIdList != [None] and self.getOpTeam(self._entitiesDict[targetEntityIdList[0]].team) == self._playersDict[playerId].team):
                                pass
                            else:
                                conditionsValid = False

                    elif (condition["feature"] == "opAroundSelf"):
                        if (len(self.entityIdAroundTile(self._entitiesDict[selfId].x, self._entitiesDict[selfId].y, self.getOpTeam(self._entitiesDict[selfId].team))) == condition["value"]):
                            pass
                        else:
                            conditionsValid = False

                    elif (condition["feature"] == "spellsPlayedDuringTurn"):
                        if (operator == "=" and self._playersDict[playerId].spellsPlayedDuringTurn == condition["value"]):
                            pass
                        elif (operator == ">" and self._playersDict[playerId].spellsPlayedDuringTurn > condition["value"]):
                            pass
                        else:
                            conditionsValid = False

                    elif (condition["feature"] == "turn"):
                        if (condition["value"] == "my"):
                            if (self._entitiesDict[selfId].team == self._playersDict[playerId].team):
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
                    abilityEntityIdList = [selfId]
                elif (ability["target"] == "targetPlayer"):
                    abilityEntityIdList = [self._playersDict[self.getPlayerIdFromTeam(self._entitiesDict[targetEntityIdList[targetIdx]].team)].heroEntityId]
                elif (ability["target"] == "myPlayer"):
                    abilityEntityIdList = [self._playersDict[playerId].heroEntityId]
                elif (ability["target"] == "opPlayer"):
                    abilityEntityIdList = [self._playersDict[opPlayerId].heroEntityId]
                elif (ability["target"] == "allOrganicAround"):
                    abilityEntityIdList = self.entityIdAroundTile(self._entitiesDict[selfId].x, self._entitiesDict[selfId].y, "all")
                elif (ability["target"] == "opOrganicAround"):
                    abilityEntityIdList = self.entityIdAroundTile(self._entitiesDict[selfId].x, self._entitiesDict[selfId].y, self.getOpTeam(self._entitiesDict[selfId].team))
                elif (ability["target"] == "myOrganicAround"):
                    abilityEntityIdList = self.entityIdAroundTile(self._entitiesDict[selfId].x, self._entitiesDict[selfId].y, self._entitiesDict[selfId].team)
                elif (ability["target"] == "allOrganicAligned"):
                    abilityEntityIdList = self.entityIdAligned(self._entitiesDict[selfId].x, self._entitiesDict[selfId].y, positionList[targetIdx]["x"], positionList[targetIdx]["y"], rangeCondition, "all")
                elif (ability["target"] == "opOrganicAligned"):
                    abilityEntityIdList = self.entityIdAligned(self._entitiesDict[selfId].x, self._entitiesDict[selfId].y, positionList[targetIdx]["x"], positionList[targetIdx]["y"], rangeCondition, self.getOpTeam(self._entitiesDict[selfId].team))
                elif (ability["target"].split(':')[0] == "allOrganicCross"):
                    abilityEntityIdList = self.entityIdInCross(positionList[targetIdx]["x"], positionList[targetIdx]["y"], int(ability["target"].split(':')[1]), "all")
                elif (ability["target"] == "tile"):
                    pass
                elif (ability["target"] == "currentSpell"):
                    abilityEntityIdList = [selfId]
                elif (ability["target"] == "hand"):
                    abilityEntityIdList = range(len(self._playersDict[playerId].handSpellList)) # WARNING : if a spell is draw, it is not taken
                else:
                    raise GameException("Wrong ability target !")

                # Handle variable value case
                if isinstance(ability["value"], int):
                    value = ability["value"]
                elif isinstance(ability["value"], dict):
                    value = ability["value"]
                elif isinstance(ability["value"], str):
                    if (ability["value"] == "-atk"):
                        value = -self._entitiesDict[selfId].atk
                    elif (ability["value"] == "atk"):
                        value = self._entitiesDict[selfId].atk
                    elif (ability["value"].split(':')[0] == "target"):
                        value = int(ability["value"].split(':')[1])
                    else:
                        value = ability["value"]
                else:
                    raise GameException(f"Ability value {ability['value']} must be an int, an str or a dict !")
                   
                # Execute ability
                executed = False
                if (conditionsValid or force):
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
                            for abilityEntityId in abilityEntityIdList:
                                self._entitiesDict[abilityEntityId].tp(positionList[value]["x"], positionList[value]["y"])
                                executed = True
                        elif (ability["feature"] == "paStock"):
                            self._playersDict[playerId].modifyPaStock(value)
                            executed = True
                        elif (ability["feature"] == "armor"):
                            for abilityEntityId in abilityEntityIdList:
                                self._entitiesDict[abilityEntityId].modifyArmor(value)
                                executed = True

                    elif (ability["behavior"] == "melee"):
                        mult = len(self.entityIdAroundTile(self._entitiesDict[self._playersDict[playerId].heroEntityId].x, self._entitiesDict[self._playersDict[playerId].heroEntityId].y, self._playersDict[self.getOpPlayerId(playerId)].team))
                        if (ability["feature"] == "atk"): 
                            self._entitiesDict[self._playersDict[playerId].heroEntityId].modifyAtk(mult*value)
                            executed = True
                        elif (ability["feature"] == "cost"):
                            for spellId in abilityEntityIdList:
                                self._playersDict[playerId].modifySpellCost(spellId, mult*value)
                                executed = True

                    elif (ability["behavior"] == "auraNb"):
                        if (self._entitiesDict[self._playersDict[playerId].heroEntityId].aura):
                            mult = self._entitiesDict[self._playersDict[playerId].heroEntityId].aura["nb"]
                        else:
                            mult = 0
                        if (ability["feature"] == "cost"):
                            for spellId in abilityEntityIdList:
                                self._playersDict[playerId].modifySpellCost(spellId, mult*value)
                                executed = True

                    elif (ability["behavior"] == "opAffected"):
                        if (ability["target"] == "opOrganicAligned"):
                            opsAffected = len(self.entityIdAligned(self._entitiesDict[selfId].x, self._entitiesDict[selfId].y, positionList[targetIdx]["x"], positionList[targetIdx]["y"], rangeCondition, self.getOpTeam(self._entitiesDict[selfId].team)))
                        if (ability["feature"] == "gauges"):
                            if isinstance(value, dict):
                                for gaugeType in list(value.keys()):
                                    self._playersDict[playerId].modifyGauge(gaugeType, opsAffected*value[gaugeType])
                                    executed = True
                            else:
                                raise GameException("Ability value for gauges must be a dict !")

                    elif (ability["behavior"] == "addAura"):
                        if (self._entitiesDict[self._playersDict[playerId].heroEntityId].aura and ability["feature"] == self._entitiesDict[self._playersDict[playerId].heroEntityId].aura["type"]):
                            self._entitiesDict[self._playersDict[playerId].heroEntityId].modifyAuraNb(value)
                            executed = True
                        else:
                            self._entitiesDict[self._playersDict[playerId].heroEntityId].newAura(ability["feature"], value)
                            executed = True
                    
                    elif (ability["behavior"] == "transformAura"):
                        if (self._entitiesDict[self._playersDict[playerId].heroEntityId].aura):
                            self._entitiesDict[self._playersDict[playerId].heroEntityId].modifyAuraType(ability["feature"])
                            executed = True

                    elif (ability["behavior"] == "charge"):
                        for abilityEntityId in abilityEntityIdList:
                            if (self._entitiesDict[selfId].x == self._entitiesDict[abilityEntityId].x):
                                if (self._entitiesDict[selfId].y < self._entitiesDict[abilityEntityId].y):
                                    self._entitiesDict[selfId].tp(self._entitiesDict[selfId].x, self._entitiesDict[abilityEntityId].y - 1)
                                    executed = True
                                elif (self._entitiesDict[selfId].y > self._entitiesDict[abilityEntityId].y):
                                    self._entitiesDict[selfId].tp(self._entitiesDict[selfId].x, self._entitiesDict[abilityEntityId].y + 1)
                                    executed = True
                                else:
                                    raise GameException("Target can't be on the same tile than selfEntity !")
                            elif (self._entitiesDict[selfId].y == self._entitiesDict[abilityEntityId].y):
                                if (self._entitiesDict[selfId].x < self._entitiesDict[abilityEntityId].x):
                                    self._entitiesDict[selfId].tp(self._entitiesDict[selfId].x - 1, self._entitiesDict[abilityEntityId].y)
                                    executed = True
                                elif (self._entitiesDict[selfId].x > self._entitiesDict[abilityEntityId].x):
                                    self._entitiesDict[selfId].tp(self._entitiesDict[selfId].x + 1, self._entitiesDict[abilityEntityId].y)
                                    executed = True
                                else:
                                    raise GameException("Target can't be on the same tile than selfEntity !")
                            else:
                                raise GameException("Target not aligned with selfEntity !")

                    elif (ability["behavior"] == "push"):
                        for abilityEntityId in abilityEntityIdList:
                            self.pushEntity(abilityEntityId, positionList[1]["x"], positionList[1]["y"], value)
                            executed = True

                    elif (ability["behavior"] == "explosion"):
                        for abilityEntityId in abilityEntityIdList:
                            for entityId in self.entityIdAroundTile(self._entitiesDict[abilityEntityId].x, self._entitiesDict[abilityEntityId].y, self._playersDict[self.getOpPlayerId(playerId)].team):
                                self._entitiesDict[entityId].modifyPv(value)
                                executed = True

                    elif (ability["behavior"] == "bounce"):
                        for abilityEntityId in abilityEntityIdList:
                            self._entitiesDict[abilityEntityId].modifyPv(value)
                            executed = True
                            affectedEntityList = [abilityEntityId]
                            toAffectEntityList = self.entityIdAroundTile(self._entitiesDict[abilityEntityId].x, self._entitiesDict[abilityEntityId].y, self._playersDict[self.getOpPlayerId(playerId)].team)
                            while toAffectEntityList:
                                affectedEntity = toAffectEntityList.pop(0)
                                affectedEntityList.append(affectedEntity)
                                toAffectEntityList.extend(list(set(self.entityIdAroundTile(self._entitiesDict[affectedEntity].x, self._entitiesDict[affectedEntity].y, self._playersDict[self.getOpPlayerId(playerId)].team)) - set(affectedEntityList)))
                                self._entitiesDict[affectedEntity].modifyPv(value)

                    elif (ability["behavior"] == "permanentState"): # TODO : Change behavior to ongoingAbilities
                        state = {}
                        for abilityEntityId in abilityEntityIdList:
                            if (ability["feature"] == "bodyguard"):
                                state["feature"]    = "bodyguard"
                                state["value"]      = abilityEntityId
                                self._entitiesDict[selfId].addState(state)
                                state["feature"]    = "bodyguarded"
                                state["value"]      = selfId     
                                self._entitiesDict[abilityEntityId].addState(state)
                            else:
                                state["feature"]    = ability["feature"]
                                state["value"]      = value
                                self._entitiesDict[abilityEntityId].addState(state)

                    elif (ability["behavior"] == "addState"):
                        state = {}
                        for abilityEntityId in abilityEntityIdList:
                            state["feature"]    = ability["feature"]
                            state["value"]      = value
                            self._entitiesDict[abilityEntityId].addState(state)

                    elif (ability["behavior"] == "summon"):
                        entityId = self.appendEntity(playerId, ability["feature"], self._playersDict[playerId].team, positionList[0]["x"], positionList[0]["y"])
                        self.executeAbilities(caller, self._entitiesDict[entityId].abilities, "spawn", playerId, entityId, None, {}, None)

                    elif (ability["behavior"] == "freeAura"):
                        self._entitiesDict[self._playersDict[playerId].heroEntityId].freeAura()

                    # If stopTrigger is defined, the ability must be added to the ongoingAbilityList
                    if stopTrigger and not(force):
                        ongoingAbilityDict = {}
                        ongoingAbilityDict["ability"]       = copy.deepcopy(ability)
                        ongoingAbilityDict["playerId"]      = playerId
                        ongoingAbilityDict["selfId"]        = selfId
                        ongoingAbilityDict["stopTrigger"]   = stopTrigger
                        self._ongoingAbilityList.append(ongoingAbilityDict)

                # Check if an aura has been used
                if (executed and ability["behavior"] == "aura"):
                    auraUsed = True

        if auraUsed:
            self._entitiesDict[selfId].modifyAuraNb(-1)

    def removeOngoingAbilities(self, stopTrigger):
        copyOngoingAbilityList = list(self._ongoingAbilityList)
        for ongoingAbility in copyOngoingAbilityList:
            if (stopTrigger == ongoingAbility["stopTrigger"]):
                ongoingAbility["ability"]["value"] = -ongoingAbility["ability"]["value"]
                self.executeAbilities([ongoingAbility["ability"]], "", ongoingAbility["playerId"], ongoingAbility["selfId"], [], [], "", True)
                self._ongoingAbilityList.remove(ongoingAbility)
            elif (stopTrigger == "always" and ongoingAbility["stopTrigger"] == "noArmor"):
                if (self._entitiesDict[self._playersDict[ongoingAbility["playerId"]].heroEntityId].armor == 0):
                    ongoingAbility["ability"]["value"] = -ongoingAbility["ability"]["value"]
                    self.executeAbilities([ongoingAbility["ability"]], "", ongoingAbility["playerId"], ongoingAbility["selfId"], [], [], "", True)
                    self._ongoingAbilityList.remove(ongoingAbility)

                    