import traceback
from functions import *
from Player import *
from Entity import *
from TileEntity import *
from Database import *
from GameException import *
from Spell import *

class Board:

    def __init__(self):
        self._nextEntityId      = 0
        self._nextTileEntityId  = 0
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

    def removeEntity(self, entityId):
        found = False
        self.removeOngoingAbilities("death", selfId=entityId)
        self.executeAbilities(self._entitiesDict[entityId].abilities, "death", self.getPlayerIdFromTeam(self._entitiesDict[entityId].team), entityId, [])
        for playerId in list(self._playersDict.keys()):
            if entityId in self._playersDict[playerId].boardEntityIds:
                self._playersDict[playerId].removeEntity(entityId)
                found = True
                break
        #for state in self._entitiesDict[entityId].states:
        #    if (state["feature"] == "bodyguard"):
        #        rmState = {}
        #        rmState["feature"]  = "bodyguarded"
        #        rmState["value"]    = entityId
        #        self._entitiesDict[state["value"]].removeState(rmState)
        #        break
        del self._entitiesDict[entityId]
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

    # Fake entity to have a regular beahvaior in abilities
    def appendTileEntity(self, x, y):
        self._entitiesDict["tile" + str(self._nextTileEntityId)] = TileEntity(x, y)
        self._nextTileEntityId += 1
        return "tile" + str(self._nextTileEntityId - 1)

    def removeTileEntity(self, tileEntityIdx):
        del self._entitiesDict[tileEntityIdx]

    def tileGarbageCollector(self):
        tileEntityIdx = 0
        while (tileEntityIdx < len(list(self._entitiesDict.keys()))):
            if ("tile" in str(list(self._entitiesDict.keys())[tileEntityIdx])):
                self.removeTileEntity(list(self._entitiesDict.keys())[tileEntityIdx])
                tileEntityIdx = 0
            else:
                tileEntityIdx += 1

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
        for entityId in list(self._entitiesDict.keys()):
            if (type(self._entitiesDict[entityId]).__name__ == "Entity"):
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
            rangeCondition = BOARD_COLS if rangeCondition == None else rangeCondition
            if (xDir > xStart):
                for x in range(xStart + 1, min(xStart + rangeCondition + 1, BOARD_COLS)):
                    matchId = self.entityIdOnTile(x, yStart)
                    if (matchId != None):
                        if (team == "all" or team == self._entitiesDict[matchId].team):
                            entityIdList.append(matchId)
            elif (xDir < xStart):
                for x in range(xStart - 1, max(xStart - rangeCondition - 1, -1), -1):
                    matchId = self.entityIdOnTile(x, yStart)
                    if (matchId != None):
                        if (team == "all" or team == self._entitiesDict[matchId].team):
                            entityIdList.append(matchId)
        elif (xStart == xDir):
            rangeCondition = BOARD_ROWS if rangeCondition == None else rangeCondition
            if (yDir > yStart):
                for y in range(yStart + 1, min(yStart + rangeCondition + 1, BOARD_ROWS)):
                    matchId = self.entityIdOnTile(xStart, y)
                    if (matchId != None):
                        if (team == "all" or team == self._entitiesDict[matchId].team):
                            entityIdList.append(matchId)
            elif (yDir < yStart):
                for y in range(yStart - 1, max(yStart - rangeCondition - 1, -1), -1):
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

    def isAlignedToTile(self, xSelf, ySelf, xTarget, yTarget):
        return ((xTarget == xSelf) ^ (yTarget == ySelf))

    def startTurn(self, playerId):
        self._playersDict[playerId].startTurn()
        for entityId in self._playersDict[playerId].boardEntityIds:
            self._entitiesDict[entityId].startTurn()
            self.executeAbilities(self._entitiesDict[entityId].abilities, "startTurn", self.getPlayerIdFromTeam(self._entitiesDict[entityId].team), entityId, [])

    def endTurn(self, playerId):
        self._playersDict[playerId].endTurn()
        self.removeOngoingAbilities("endTurn")
        for entityId in self._playersDict[playerId].boardEntityIds:
            self._entitiesDict[entityId].endTurn()
            self.executeAbilities(self._entitiesDict[entityId].abilities, "endTurn", self.getPlayerIdFromTeam(self._entitiesDict[entityId].team), entityId, [])

    def useReserve(self, playerId):
        self._playersDict[playerId].useReserve()

    # This function is called after each action
    def always(self):
        self.garbageCollector()
        self.removeOngoingAbilities("always")
        self.removeOngoingAbilities("alwaysAfterEnd")
        for entityId in list(self._entitiesDict.keys()):
            self.executeAbilities(self._entitiesDict[entityId].abilities, "always", self.getPlayerIdFromTeam(self._entitiesDict[entityId].team), entityId, [])
            self._entitiesDict[entityId].endAction()
            self.executeAbilities(self._entitiesDict[entityId].abilities, "alwaysAfterEnd", self.getPlayerIdFromTeam(self._entitiesDict[entityId].team), entityId, [])
            self._entitiesDict[entityId].endAction()
        for playerId in list(self._playersDict.keys()):
            if (self._playersDict[playerId].heroEntityId in self._entitiesDict):
                for spellIdx in range(0, len(list(self._playersDict[playerId].handSpellDict.keys()))):
                    spellId = list(self._playersDict[playerId].handSpellDict.keys())[spellIdx]
                    self.executeAbilities(self._playersDict[playerId].handSpellDict[spellId].abilities, "always", playerId, self._playersDict[playerId].heroEntityId, [], spellId=spellId)
        self.garbageCollector()

    def moveEntity(self, playerId, entityId, path):
        x               = self._entitiesDict[entityId].x
        y               = self._entitiesDict[entityId].y
        pm              = self._entitiesDict[entityId].pm
        attackedEntityId= None
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
                                if (not(self._entitiesDict[attackedEntityId].isInStates("elusive"))):
                                    pm              = -1
                                else:
                                    raise GameException("You can't attack the target because it is elusive !")
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
                                    if (not(self._entitiesDict[attackedEntityId].isInStates("elusive"))):
                                        pm              = -1
                                    else:
                                        raise GameException("You can't attack the target because it is elusive !")
                                else:
                                    raise GameException("You can't attack this turn !")
                    else:
                        raise GameException("Successive tiles must be contiguous in path or an entity is on your path !")
                else:
                    raise GameException("Tile out of the board !")
        else:
            raise GameException("First tile of the path must be the current entity position !")

        self._entitiesDict[entityId].move(x, y)
        self.executeAbilities(self._entitiesDict[entityId].abilities, "move", playerId, entityId, [])
        if (attackedEntityId != None):
            self.executeAbilities(self._entitiesDict[entityId].abilities, "attack", playerId, entityId, [attackedEntityId])
            self.executeAbilities(self._entitiesDict[attackedEntityId].abilities, "attacked", playerId, attackedEntityId, [])
            self._entitiesDict[entityId].attack(self._playersDict[playerId]) # Only used for agonyMaster / Awfull

    def pushEntity(self, entityId, x, y, distance):
        xe  = self._entitiesDict[entityId].x
        ye  = self._entitiesDict[entityId].y
        remainingDistance = abs(distance)
        nextX = xe
        nextY = ye
        if (x == xe and y == ye):
            pass
        elif (x == xe and ((y > ye and distance >= 0) or (y < ye and distance <= 0))):
            while (0 <= nextY + 1 < BOARD_ROWS and self.entityIdOnTile(nextX, nextY + 1) == None and remainingDistance > 0):
                remainingDistance -= 1
                nextY += 1
        elif (x == xe and ((y < ye and distance >= 0) or (y > ye and distance <= 0))):
            while (0 <= nextY - 1 < BOARD_ROWS and self.entityIdOnTile(nextX, nextY - 1) == None and remainingDistance > 0):
                remainingDistance -= 1
                nextY -= 1
        elif (((x > xe and distance >= 0) or (x < xe and distance <= 0)) and y == ye):
            while (0 <= nextX + 1 < BOARD_COLS and self.entityIdOnTile(nextX + 1, nextY) == None and remainingDistance > 0):
                remainingDistance -= 1
                nextX += 1
        elif (((x < xe and distance >= 0) or (x > xe and distance <= 0)) and y == ye):
            while (0 <= nextX - 1 < BOARD_COLS and self.entityIdOnTile(nextX - 1, nextY) == None and remainingDistance > 0):
                remainingDistance -= 1
                nextX -= 1
        else:
            raise GameException("You can't push if you are not aligned with target !")
        self._entitiesDict[entityId].tp(nextX, nextY)

    def spellCast(self, playerId, spellIdx, targetPositionList):
        # Check if spell in hand
        if (0 <= spellIdx < len(list(self._playersDict[playerId].handSpellDict.keys()))):
            spellId = list(self._playersDict[playerId].handSpellDict.keys())[spellIdx]
            spell = self._playersDict[playerId].handSpellDict[spellId]

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
                    selfEntityId        = self._playersDict[playerId].heroEntityId
                    for allowedTargetIdx in range(0, len(spell.allowedTargetList)):
                        targetEntityIdList.append(None)
                        if (spell.allowedTargetList[allowedTargetIdx] == "all"):
                            targetEntityIdList[-1] = self.appendTileEntity(targetPositionList[allowedTargetIdx]["x"], targetPositionList[allowedTargetIdx]["y"])

                        elif (spell.allowedTargetList[allowedTargetIdx] == "emptyTile"):
                            if (self.entityIdOnTile(targetPositionList[allowedTargetIdx]["x"], targetPositionList[allowedTargetIdx]["y"]) == None):
                                targetEntityIdList[-1] = self.appendTileEntity(targetPositionList[allowedTargetIdx]["x"], targetPositionList[allowedTargetIdx]["y"])
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
                            if (targetEntityIdList[-1] != None and not("mechanism" in self._entitiesDict[targetEntityIdList[-1]].typeList)):
                               pass
                            else:
                               raise GameException("An entity, not mechanism, must be targeted !")

                        elif (spell.allowedTargetList[allowedTargetIdx] == "allMechanism"):
                            targetEntityIdList[-1] = self.entityIdOnTile(targetPositionList[allowedTargetIdx]["x"], targetPositionList[allowedTargetIdx]["y"])
                            if (targetEntityIdList[-1] != None and "mechanism" in self._entitiesDict[targetEntityIdList[-1]].typeList):
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
                            if (targetEntityIdList[-1] != None and self._entitiesDict[targetEntityIdList[-1]].team == self._playersDict[playerId].team and not("mechanism" in self._entitiesDict[targetEntityIdList[-1]].typeList)):
                               pass
                            else:
                               raise GameException("An entity, owned by you, not mechanism, must be targeted !")

                        elif (spell.allowedTargetList[allowedTargetIdx] == "myMechanism"):
                            targetEntityIdList[-1] = self.entityIdOnTile(targetPositionList[allowedTargetIdx]["x"], targetPositionList[allowedTargetIdx]["y"])
                            if (targetEntityIdList[-1] != None and self._entitiesDict[targetEntityIdList[-1]].team == self._playersDict[playerId].team and "mechanism" in self._entitiesDict[targetEntityIdList[-1]].typeList):
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
                            if (targetEntityIdList[-1] != None and self._entitiesDict[targetEntityIdList[-1]].team == self._playersDict[self.getOpPlayerId(playerId)].team and not("mechanism" in self._entitiesDict[targetEntityIdList[-1]].typeList)):
                               pass
                            else:
                               raise GameException("An entity, owned by your opponent, not mechanism, must be targeted !")

                        elif (spell.allowedTargetList[allowedTargetIdx] == "opMechanism"):
                            targetEntityIdList[-1] = self.entityIdOnTile(targetPositionList[allowedTargetIdx]["x"], targetPositionList[allowedTargetIdx]["y"])
                            if (targetEntityIdList[-1] != None and self._entitiesDict[targetEntityIdList[-1]].team == self._playersDict[self.getOpPlayerId(playerId)].team and "mechanism" in self._entitiesDict[targetEntityIdList[-1]].typeList):
                               pass
                            else:
                               raise GameException("An entity, owned by your opponent, not mechanism, must be targeted !")

                        elif (spell.allowedTargetList[allowedTargetIdx] == "myHero"):
                            targetEntityIdList[-1] = self.entityIdOnTile(targetPositionList[allowedTargetIdx]["x"], targetPositionList[allowedTargetIdx]["y"])
                            if (targetEntityIdList[-1] == self._playersDict[playerId].heroEntityId):
                                pass
                            else:
                                raise GameException("Target must be your hero !")

                        elif (spell.allowedTargetList[allowedTargetIdx] == "opHero"):
                            targetEntityIdList[-1] = self.entityIdOnTile(targetPositionList[allowedTargetIdx]["x"], targetPositionList[allowedTargetIdx]["y"])
                            if (targetEntityIdList[-1] == self._playersDict[self.getOpPlayerId(playerId)].heroEntityId):
                                pass
                            else:
                                raise GameException("Target must be opponent hero !")

                        elif (spell.allowedTargetList[allowedTargetIdx] == "allOrganicAligned"):
                            targetEntityIdList[-1] = self.entityIdOnTile(targetPositionList[allowedTargetIdx]["x"], targetPositionList[allowedTargetIdx]["y"])
                            if (targetEntityIdList[-1] in self.entityIdAligned(self._entitiesDict[self._playersDict[playerId].heroEntityId].x, self._entitiesDict[self._playersDict[playerId].heroEntityId].y, targetPositionList[allowedTargetIdx]["x"], targetPositionList[allowedTargetIdx]["y"], None, "all") and not("mechanism" in self._entitiesDict[targetEntityIdList[-1]].typeList)):
                                pass
                            else:
                                raise GameException("Target is not the first, not mechanism, aligned entity !")

                        elif (spell.allowedTargetList[allowedTargetIdx] == "allFirstEntityAligned"):
                            targetEntityIdList[-1] = self.entityIdOnTile(targetPositionList[allowedTargetIdx]["x"], targetPositionList[allowedTargetIdx]["y"])
                            if (targetEntityIdList[-1] in self.firstEntityIdAlignedToTile(self._entitiesDict[self._playersDict[playerId].heroEntityId].x, self._entitiesDict[self._playersDict[playerId].heroEntityId].y, "all")):
                                pass
                            else:
                                raise GameException("Target is not the first aligned entity !")

                        elif (spell.allowedTargetList[allowedTargetIdx] == "allFirstOrganicAligned"):
                            targetEntityIdList[-1] = self.entityIdOnTile(targetPositionList[allowedTargetIdx]["x"], targetPositionList[allowedTargetIdx]["y"])
                            if (targetEntityIdList[-1] in self.firstEntityIdAlignedToTile(self._entitiesDict[self._playersDict[playerId].heroEntityId].x, self._entitiesDict[self._playersDict[playerId].heroEntityId].y, "all") and not("mechanism" in self._entitiesDict[targetEntityIdList[-1]].typeList)):
                                pass
                            else:
                                raise GameException("Target is not the first, not mechanism, aligned entity !")

                        elif (spell.allowedTargetList[allowedTargetIdx] == "heroAdjacentTile"):
                            if (self.isAdjacentToTile(self._entitiesDict[self._playersDict[playerId].heroEntityId].x, self._entitiesDict[self._playersDict[playerId].heroEntityId].y, targetPositionList[allowedTargetIdx]["x"], targetPositionList[allowedTargetIdx]["y"])):
                                targetEntityIdList[-1] = self.appendTileEntity(targetPositionList[allowedTargetIdx]["x"], targetPositionList[allowedTargetIdx]["y"])
                            else:
                                raise GameException("Target must be adjacent to your hero !")
                    
                        elif (spell.allowedTargetList[allowedTargetIdx] == "allOrganicAdjacent"):
                            targetEntityIdList[-1] = self.entityIdOnTile(targetPositionList[allowedTargetIdx]["x"], targetPositionList[allowedTargetIdx]["y"])
                            if (targetEntityIdList[-1] in self.entityIdAligned(self._entitiesDict[self._playersDict[playerId].heroEntityId].x, self._entitiesDict[self._playersDict[playerId].heroEntityId].y, targetPositionList[allowedTargetIdx]["x"], targetPositionList[allowedTargetIdx]["y"], 1, "all")):
                                pass
                            else:
                                raise GameException("Target must be an entity, not mechanism, adjacent to your hero !")

                        elif (spell.allowedTargetList[allowedTargetIdx] == "firstTargetAdjacentTile"):
                            if (self.isAdjacentToTile(targetPositionList[0]["x"], targetPositionList[0]["y"], targetPositionList[allowedTargetIdx]["x"], targetPositionList[allowedTargetIdx]["y"]) or (targetPositionList[0]["x"] == targetPositionList[allowedTargetIdx]["x"] and targetPositionList[0]["y"] == targetPositionList[allowedTargetIdx]["y"])):
                                targetEntityIdList[-1] = self.appendTileEntity(targetPositionList[allowedTargetIdx]["x"], targetPositionList[allowedTargetIdx]["y"])
                            else:
                                raise GameException("Second target must be adjacent to first target !")

                        elif (spell.allowedTargetList[allowedTargetIdx] == "emptyAlignedTile"):
                            if (self.entityIdOnTile(targetPositionList[allowedTargetIdx]["x"], targetPositionList[allowedTargetIdx]["y"]) == None and self.isAlignedToTile(self._entitiesDict[self._playersDict[playerId].heroEntityId].x, self._entitiesDict[self._playersDict[playerId].heroEntityId].y, targetPositionList[allowedTargetIdx]["x"], targetPositionList[allowedTargetIdx]["y"])):
                                targetEntityIdList[-1] = self.appendTileEntity(targetPositionList[allowedTargetIdx]["x"], targetPositionList[allowedTargetIdx]["y"])
                            else:
                                raise GameException("The targeted tile must be empty and aligned !")

                        else:
                            raise GameException("Wrong target type !")

                else:
                    raise GameException("Wrong number of target !")

                # Execute spell
                self.removeOngoingAbilities("spellCast") # WARNING : This line is here only because, for now, the only spellCast ongoingAbilities affect cost
                self.executeAbilities(spell.abilities, "spellCast", playerId, selfEntityId, targetEntityIdList, spellElem=spell.elem)
                for entityId in [e for e in list(self._entitiesDict.keys()) if not("tile" in str(e))]:
                    self.executeAbilities(self._entitiesDict[entityId].abilities, "spellCast", playerId, entityId, targetEntityIdList, spellElem=spell.elem)
                self.tileGarbageCollector()

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
                        self.executeAbilities(self._entitiesDict[entityId].abilities, "spawn", playerId, entityId, [])
                        self._playersDict[playerId].summonCompanion(companionId, entityId)

                    else:
                        raise GameException("Invalid companion placement !")
                else:
                    raise GameException("Companion not available !")
            else:
                raise GameException("Companion not in your deck !")
        else:
            raise GameException("Only one summon position is allowed !")

    def executeAbilities(self, abilityList, trigger, playerId, selfId, targetEntityIdList, spellElem=None, spellId=None, triggingAbility=None, triggingAbilityTargetIdList=None, force=False):
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

                # Choose abilityEntity
                if (ability["target"] == "target"):
                    abilityTargetIdList = [targetEntityIdList[targetIdx]]
                elif (ability["target"] == "self"):
                    abilityTargetIdList = [selfId]
                elif (ability["target"] == "myPlayer"):
                    abilityTargetIdList = [playerId]
                elif (ability["target"] == "opPlayer"):
                    abilityTargetIdList = [opPlayerId]
                elif (ability["target"] == "targetPlayer"):
                    abilityTargetIdList = [self.getPlayerIdFromTeam(self._entitiesDict[targetEntityIdList[targetIdx]].team)]
                elif (ability["target"] == "myHero"):
                    abilityTargetIdList = [self._playersDict[playerId].heroEntityId]
                elif (ability["target"] == "opHero"):
                    abilityTargetIdList = [self._playersDict[opPlayerId].heroEntityId]
                elif (ability["target"] == "allOrganicAroundSelf"):
                    abilityTargetIdList = self.entityIdAroundTile(self._entitiesDict[selfId].x, self._entitiesDict[selfId].y, "all")
                elif (ability["target"] == "opOrganicAroundSelf"):
                    abilityTargetIdList = self.entityIdAroundTile(self._entitiesDict[selfId].x, self._entitiesDict[selfId].y, self.getOpTeam(self._entitiesDict[selfId].team))
                elif (ability["target"] == "myOrganicAroundSelf"):
                    abilityTargetIdList = self.entityIdAroundTile(self._entitiesDict[selfId].x, self._entitiesDict[selfId].y, self._entitiesDict[selfId].team)
                elif (ability["target"] == "allOrganicAroundTarget"):
                    abilityTargetIdList = self.entityIdAroundTile(self._entitiesDict[targetEntityIdList[targetIdx]].x, self._entitiesDict[targetEntityIdList[targetIdx]].y, "all")
                elif (ability["target"] == "opOrganicAroundTarget"):
                    abilityTargetIdList = self.entityIdAroundTile(self._entitiesDict[targetEntityIdList[targetIdx]].x, self._entitiesDict[targetEntityIdList[targetIdx]].y, self.getOpTeam(self._entitiesDict[selfId].team))
                elif (ability["target"] == "myOrganicAroundTarget"):
                    abilityTargetIdList = self.entityIdAroundTile(self._entitiesDict[targetEntityIdList[targetIdx]].x, self._entitiesDict[targetEntityIdList[targetIdx]].y, self._entitiesDict[selfId].team)
                elif (ability["target"].split(':')[0] == "allOrganicAligned"):
                    if (len(ability["target"].split(':')) > 1):
                        abilityTargetIdList = self.entityIdAligned(self._entitiesDict[selfId].x, self._entitiesDict[selfId].y, self._entitiesDict[targetEntityIdList[targetIdx]].x, self._entitiesDict[targetEntityIdList[targetIdx]].y, int(ability["target"].split(':')[1]), "all")
                    else:
                        abilityTargetIdList = self.entityIdAligned(self._entitiesDict[selfId].x, self._entitiesDict[selfId].y, self._entitiesDict[targetEntityIdList[targetIdx]].x, self._entitiesDict[targetEntityIdList[targetIdx]].y, None, "all")
                elif (ability["target"].split(':')[0] == "opOrganicAligned"):
                    if (len(ability["target"].split(':')) > 1):
                        abilityTargetIdList = self.entityIdAligned(self._entitiesDict[selfId].x, self._entitiesDict[selfId].y, self._entitiesDict[targetEntityIdList[targetIdx]].x, self._entitiesDict[targetEntityIdList[targetIdx]].y, int(ability["target"].split(':')[1]), self.getOpTeam(self._entitiesDict[selfId].team))
                    else:
                        abilityTargetIdList = self.entityIdAligned(self._entitiesDict[selfId].x, self._entitiesDict[selfId].y, self._entitiesDict[targetEntityIdList[targetIdx]].x, self._entitiesDict[targetEntityIdList[targetIdx]].y, None, self.getOpTeam(self._entitiesDict[selfId].team))
                elif (ability["target"].split(':')[0] == "allOrganicCross"):
                    abilityTargetIdList = self.entityIdInCross(self._entitiesDict[targetEntityIdList[targetIdx]].x, self._entitiesDict[targetEntityIdList[targetIdx]].y, int(ability["target"].split(':')[1]), "all")
                elif (ability["target"] == "currentSpell"):
                    abilityTargetIdList = [] if spellId == None else [spellId]
                elif (ability["target"] == "hand"):
                    abilityTargetIdList = range(len(list(self._playersDict[playerId].handSpellDict.keys()))) # WARNING : if a spell is draw, it is not taken
                else:
                    raise GameException("Wrong ability target !")

                # Check conditions
                conditionsValid = True
                for condition in ability["conditionList"]:
                    if ("operator" in condition):
                        operator = condition["operator"]
                    else:
                        operator = "="

                    if ("target" in condition):
                        if ("spellTarget:" in condition["target"]):
                            conditionTargetId = targetEntityIdList[int(condition["target"].split(':')[1])]
                        elif (condition["target"] == "spellTarget"):
                            conditionTargetId = targetEntityIdList[0]
                        elif (condition["target"] == "spellTargetPlayer"):
                            conditionTargetId = self.getPlayerIdFromTeam(self._entitiesDict[targetEntityIdList[0]].team)
                        elif ("abilityTarget:" in condition["target"]):
                            conditionTargetId = abilityTargetIdList[int(condition["target"].split(':')[1])]
                        elif (condition["target"] == "abilityTarget"):
                            conditionTargetId = abilityTargetIdList[0]
                        elif (condition["target"] == "self"):
                            conditionTargetId = selfId
                        else:
                            raise GameException("Wrong condition target !")
                    else:
                        conditionTargetId = abilityTargetIdList[0]

                    if (condition["feature"] == "elemState"):
                        if (operator == "=" and condition["value"] in ["oiled", "wet", "muddy", "windy"]):
                            if (self._entitiesDict[conditionTargetId].elemState == condition["value"]):
                                self._entitiesDict[conditionTargetId].setElemState("")
                            else:
                                conditionsValid = False
                        elif (operator == "!=" and condition["value"] in ["oiled", "wet", "muddy", "windy"]):
                            if (self._entitiesDict[conditionTargetId].elemState != condition["value"]):
                                pass
                            else:
                                conditionsValid = False
                        else:
                            raise GameException("ElemState to consume does not exist !")

                    elif (condition["feature"] == "state"):
                        if (operator == "=" and self._entitiesDict[conditionTargetId].isInStates(condition["value"])):
                            pass
                        else:
                            conditionsValid = False

                    elif (condition["feature"] == "elem"):
                        if (operator == "=" and condition["value"] in ["fire", "water", "earth", "air", "neutral"]):
                            if (spellElem == condition["value"]):
                                pass
                            else:
                                conditionsValid = False
                        else:
                            raise GameException("Elem of the spell does not exist !")

                    elif (condition["feature"] == "paStock"):
                        if (operator == "=" and self._playersDict[conditionTargetId].paStock == condition["value"]):
                            pass
                        elif (operator == ">=" and self._playersDict[conditionTargetId].paStock >= condition["value"]):
                            pass
                        else:
                            conditionsValid = False

                    elif (condition["feature"] == "myCompanions"):
                        myCompanions = 0
                        for companion in self._playersDict[playerId].companionList:
                            if (companion["state"] == "alive"):
                                myCompanions += 1

                        if (operator == "=" and myCompanions == condition["value"]):
                            pass
                        else:
                            conditionsValid = False

                    elif (condition["feature"] == "rangeFromHero"):
                        if (operator == "=" and calcDist(self._entitiesDict[self._playersDict[playerId].heroEntityId].x, self._entitiesDict[self._playersDict[playerId].heroEntityId].y, self._entitiesDict[conditionTargetId].x, self._entitiesDict[conditionTargetId].y) == condition["value"]):
                            rangeCondition = condition["value"]
                        elif (operator == "<=" and calcDist(self._entitiesDict[self._playersDict[playerId].heroEntityId].x, self._entitiesDict[self._playersDict[playerId].heroEntityId].y, self._entitiesDict[conditionTargetId].x, self._entitiesDict[conditionTargetId].y) <= condition["value"]):
                            rangeCondition = condition["value"]
                        else:
                            conditionsValid = False

                    elif (condition["feature"] == "rangeFromFirstTarget"):
                        if (operator == "=" and calcDist(self._entitiesDict[abilityTargetIdList[0]].x, self._entitiesDict[abilityTargetIdList[0]].y, self._entitiesDict[conditionTargetId].x, self._entitiesDict[conditionTargetId].y) == condition["value"]):
                            pass
                        elif (operator == "<=" and calcDist(self._entitiesDict[abilityTargetIdList[0]].x, self._entitiesDict[abilityTargetIdList[0]].y, self._entitiesDict[conditionTargetId].x, self._entitiesDict[conditionTargetId].y) <= condition["value"]):
                            pass
                        else:
                            conditionsValid = False

                    elif (condition["feature"] == "target"):
                        if (condition["value"] == "opOrganic"):
                            if (type(self._entitiesDict[conditionTargetId]).__name__ == "Entity" and not("mechanism" in self._entitiesDict[conditionTargetId].typeList) and self.getOpTeam(self._entitiesDict[conditionTargetId].team) == self._playersDict[playerId].team):
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
                        if (condition["value"] == "my" and self._entitiesDict[selfId].team == self._playersDict[playerId].team):
                            pass
                        elif (condition["value"] == "op" and self._entitiesDict[selfId].team == self.getOpTeam(self._playersDict[playerId].team)):
                            pass
                        else:
                            conditionsValid = False

                    elif (condition["feature"] == "pv"):
                        if (operator == "<=" and self._entitiesDict[conditionTargetId].pv <= condition["value"]):
                            pass
                        else:
                            conditionsValid = False

                    elif (condition["feature"] == "auraNb"):
                        if (operator == "=" and self._entitiesDict[selfId].aura["nb"] == condition["value"]):
                            pass
                        elif (operator == ">=" and self._entitiesDict[selfId].aura["nb"] >= condition["value"]):
                            pass
                        else:
                            conditionsValid = False

                    elif (condition["feature"] == "oneByTurn"):
                        if (condition["value"] in self._entitiesDict[selfId].oneByTurnAbilityList):
                            conditionsValid = False
                        else:
                            pass

                    elif (condition["feature"] == "behavior"):
                        if (condition["value"] == triggingAbility["behavior"]):
                            pass
                        else:
                            conditionsValid = False

                    # Only for Ombraden, ugly implementation
                    elif (condition["feature"] == "position"):
                        if (condition["value"] == "self" and ((triggingAbility["feature"] == "position" and selfId in triggingAbilityTargetIdList) or triggingAbility["behavior"] == "swap")):
                            pass
                        else:
                            conditionsValid = False

                    else:
                        raise GameException("Wrong ability condition !")

                if (not(conditionsValid) and ability["break"] == "True"):
                    raise GameException("The conditions to launch this spell are not respected !")

                if (conditionsValid):
                    for condition in ability["conditionList"]:
                        if (condition["feature"] == "oneByTurn"):
                            self._entitiesDict[abilityTargetIdList[0]].appendOneByTurnAbility(condition["value"])

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
                    else:
                        value = ability["value"]
                else:
                    raise GameException(f"Ability value {ability['value']} must be an int, an str or a dict !")
                   
                # Execute ability
                executed = False
                mult = 1 if not("mult" in ability) else ability["mult"] # Usefull to handle stopTrigger case
                if (conditionsValid or force):
                    if (trigger != "ability"):
                        for entityId in self._playersDict[playerId].boardEntityIds:
                            self.executeAbilities(self._entitiesDict[entityId].abilities, "ability", self.getPlayerIdFromTeam(self._entitiesDict[entityId].team), entityId, targetEntityIdList, triggingAbility=ability, triggingAbilityTargetIdList=abilityTargetIdList)
                    if (ability["behavior"] in ["", "explosion", "aura"]):
                        if (ability["feature"] == "pv" or ability["feature"] == "stealLife"):
                            for abilityEntityId in abilityTargetIdList:
                                guarded = False
                                if (value < 0):
                                    for state in self._entitiesDict[abilityEntityId].states:
                                        if (state["feature"] == "bodyguarded"):
                                            guardId = state["value"]
                                            guarded = True
                                            break
                                if guarded:
                                    removedPv = self._entitiesDict[guardId].modifyPv(value)
                                else:
                                    removedPv = self._entitiesDict[abilityEntityId].modifyPv(value)
                                if (ability["feature"] == "stealLife"):
                                    self._entitiesDict[selfId].modifyPv(-removedPv)
                                executed = True
                        elif (ability["feature"] == "elemState"):
                            for abilityEntityId in abilityTargetIdList:
                                self._entitiesDict[abilityEntityId].setElemState(value)
                                executed = True
                        elif (ability["feature"] == "pm"):
                            for abilityEntityId in abilityTargetIdList:
                                self._entitiesDict[abilityEntityId].modifyPm(value)
                                executed = True
                        elif (ability["feature"] == "gauges"):
                            if isinstance(value, dict):
                                for gaugeType in list(value.keys()):
                                    self._playersDict[abilityTargetIdList[0]].modifyGauge(gaugeType, value[gaugeType])
                                    executed = True
                            else:
                                raise GameException("Ability value for gauges must be a dict !")
                        elif (ability["feature"] == "atk"):
                            for abilityEntityId in abilityTargetIdList:
                                self._entitiesDict[abilityEntityId].modifyAtk(value)
                                executed = True
                        elif (ability["feature"] == "position"):
                            self._entitiesDict[abilityTargetIdList[targetIdx]].tp(self._entitiesDict[targetEntityIdList[value]].x, self._entitiesDict[targetEntityIdList[value]].y)
                            executed = True
                        elif (ability["feature"] == "paStock"):
                            self._playersDict[abilityTargetIdList[0]].modifyPaStock(value)
                            executed = True
                        elif (ability["feature"] == "armor"):
                            for abilityEntityId in abilityTargetIdList:
                                self._entitiesDict[abilityEntityId].modifyArmor(value)
                                executed = True
                        elif (ability["feature"] == "cost"):
                            for spellId in abilityTargetIdList:
                                self._playersDict[playerId].modifySpellCost(spellId, value)
                                executed = True

                    elif (ability["behavior"] == "swap"):
                        x = self._entitiesDict[selfId].x
                        y = self._entitiesDict[selfId].y
                        self._entitiesDict[selfId].tp(self._entitiesDict[abilityTargetIdList[value]].x, self._entitiesDict[abilityTargetIdList[value]].y)
                        self._entitiesDict[abilityTargetIdList[value]].tp(x, y)
                        executed = True

                    elif (ability["behavior"] == "melee"):
                        mult = len(self.entityIdAroundTile(self._entitiesDict[selfId].x, self._entitiesDict[selfId].y, self._playersDict[opPlayerId].team)) if not(force) else mult # Handle the stopTrigger case
                        if (ability["feature"] == "pv"): 
                            self._entitiesDict[abilityTargetIdList[targetIdx]].modifyPv(mult*value)
                            executed = True
                        elif (ability["feature"] == "atk"): 
                            self._entitiesDict[abilityTargetIdList[targetIdx]].modifyAtk(mult*value)
                            executed = True
                        elif (ability["feature"] == "armor"): 
                            self._entitiesDict[abilityTargetIdList[targetIdx]].modifyArmor(mult*value)
                            executed = True
                        elif (ability["feature"] == "cost"):
                            for spellId in abilityTargetIdList:
                                self._playersDict[playerId].modifySpellCost(spellId, mult*value)
                                executed = True

                    elif (ability["behavior"] == "support"):
                        mult = len(self.entityIdAroundTile(self._entitiesDict[selfId].x, self._entitiesDict[selfId].y, self._playersDict[playerId].team)) if not(force) else mult # Handle the stopTrigger case
                        if (ability["feature"] == "pv"): 
                            self._entitiesDict[abilityTargetIdList[targetIdx]].modifyPv(mult*value)
                            executed = True
                        elif (ability["feature"] == "atk"): 
                            self._entitiesDict[abilityTargetIdList[targetIdx]].modifyAtk(mult*value)
                            executed = True
                        elif (ability["feature"] == "cost"):
                            for spellId in abilityTargetIdList:
                                self._playersDict[playerId].modifySpellCost(spellId, mult*value)
                                executed = True

                    elif (ability["behavior"] == "distance"):
                        mult = calcDist(self._entitiesDict[selfId].x, self._entitiesDict[selfId].y, self._entitiesDict[abilityTargetIdList[0]].x, self._entitiesDict[abilityTargetIdList[0]].y, offset=-1) if not(force) else mult # Handle the stopTrigger case
                        if (ability["feature"] == "atk"): 
                            self._entitiesDict[selfId].modifyAtk(mult*value)
                            executed = True
                        elif (ability["feature"] == "cost"):
                            for spellId in abilityTargetIdList:
                                self._playersDict[playerId].modifySpellCost(spellId, mult*value)
                                executed = True
                        elif (ability["feature"] == "pv"):
                            for abilityEntityId in abilityTargetIdList:
                                self._entitiesDict[abilityEntityId].modifyPv(mult*value)
                                executed = True

                    elif (ability["behavior"] == "auraNb"):
                        mult = self._entitiesDict[selfId].aura["nb"] if not(force) else mult # Handle the stopTrigger case
                        if (ability["feature"] == "cost"):
                            for spellId in abilityTargetIdList:
                                self._playersDict[playerId].modifySpellCost(spellId, mult*value)
                                executed = True
                        elif (ability["feature"] == "pv"):
                            for entityId in abilityTargetIdList:
                                self._entitiesDict[entityId].modifyPv(mult*value)
                                executed = True
                        elif (ability["feature"] == "pm"):
                            for entityId in abilityTargetIdList:
                                self._entitiesDict[entityId].modifyPm(mult*value)
                                executed = True
                        elif (ability["feature"] == "paStock"):
                            self._playersDict[playerId].modifyPaStock(mult*value)
                            executed = True

                    elif (ability["behavior"] == "opAffected"):
                        mult = len(abilityTargetIdList) if not(force) else mult # Handle the stopTrigger case
                        if (ability["feature"] == "gauges"):
                            if isinstance(value, dict):
                                for gaugeType in list(value.keys()):
                                    self._playersDict[playerId].modifyGauge(gaugeType, mult*value[gaugeType])
                                    executed = True
                            else:
                                raise GameException("Ability value for gauges must be a dict !")

                    elif (ability["behavior"] == "addAuraWeak"):
                        self._entitiesDict[selfId].addAuraBuffer(ability["feature"], value, "WEAK")
                        executed = True
                    
                    elif (ability["behavior"] == "addAuraStrong"):
                        self._entitiesDict[selfId].addAuraBuffer(ability["feature"], value, "STRONG")
                        executed = True

                    elif (ability["behavior"] == "addAuraReset"):
                        self._entitiesDict[selfId].addAuraBuffer(ability["feature"], value, "RESET")
                        executed = True

                    elif (ability["behavior"] == "charge"):
                        for abilityEntityId in abilityTargetIdList:
                            if (self._entitiesDict[selfId].x == self._entitiesDict[abilityEntityId].x):
                                if (self._entitiesDict[selfId].y < self._entitiesDict[abilityEntityId].y):
                                    self._entitiesDict[selfId].tp(self._entitiesDict[abilityEntityId].x, self._entitiesDict[abilityEntityId].y - 1)
                                    executed = True
                                elif (self._entitiesDict[selfId].y > self._entitiesDict[abilityEntityId].y):
                                    self._entitiesDict[selfId].tp(self._entitiesDict[abilityEntityId].x, self._entitiesDict[abilityEntityId].y + 1)
                                    executed = True
                                else:
                                    raise GameException("Target can't be on the same tile than selfEntity !")
                            elif (self._entitiesDict[selfId].y == self._entitiesDict[abilityEntityId].y):
                                if (self._entitiesDict[selfId].x < self._entitiesDict[abilityEntityId].x):
                                    self._entitiesDict[selfId].tp(self._entitiesDict[abilityEntityId].x - 1, self._entitiesDict[abilityEntityId].y)
                                    executed = True
                                elif (self._entitiesDict[selfId].x > self._entitiesDict[abilityEntityId].x):
                                    self._entitiesDict[selfId].tp(self._entitiesDict[abilityEntityId].x + 1, self._entitiesDict[abilityEntityId].y)
                                    executed = True
                                else:
                                    raise GameException("Target can't be on the same tile than selfEntity !")
                            else:
                                raise GameException("Target not aligned with selfEntity !")

                    elif (ability["behavior"] == "push"):
                        for abilityEntityId in abilityTargetIdList:
                            self.pushEntity(abilityEntityId, self._entitiesDict[targetEntityIdList[1]].x, self._entitiesDict[targetEntityIdList[1]].y, value)
                            executed = True

                    elif (ability["behavior"] == "pushBack"):
                        for abilityEntityId in abilityTargetIdList:
                            self.pushEntity(abilityEntityId, self._entitiesDict[targetEntityIdList[0]].x, self._entitiesDict[targetEntityIdList[0]].y, -value)
                            executed = True

                    elif (ability["behavior"] == "explosion"):
                        for abilityEntityId in abilityTargetIdList:
                            for entityId in self.entityIdAroundTile(self._entitiesDict[abilityEntityId].x, self._entitiesDict[abilityEntityId].y, self._playersDict[self.getOpPlayerId(playerId)].team):
                                self._entitiesDict[entityId].modifyPv(value)
                                executed = True

                    elif (ability["behavior"] == "bounce"):
                        for abilityEntityId in abilityTargetIdList:
                            self._entitiesDict[abilityEntityId].modifyPv(value)
                            executed = True
                            affectedEntityList = [abilityEntityId]
                            toAffectEntityList = self.entityIdAroundTile(self._entitiesDict[abilityEntityId].x, self._entitiesDict[abilityEntityId].y, self._playersDict[self.getOpPlayerId(playerId)].team)
                            while toAffectEntityList:
                                affectedEntity = toAffectEntityList.pop(0)
                                affectedEntityList.append(affectedEntity)
                                for entityId in self.entityIdAroundTile(self._entitiesDict[affectedEntity].x, self._entitiesDict[affectedEntity].y, self._playersDict[self.getOpPlayerId(playerId)].team): 
                                    if not(entityId in affectedEntityList) and not(entityId in toAffectEntityList):
                                        toAffectEntityList.append(entityId)
                                self._entitiesDict[affectedEntity].modifyPv(value)

                    elif (ability["behavior"] == "addState"):
                        state = {}
                        if (":" in ability["feature"]):
                            stateFeature = ability["feature"].split(':')[0]
                            duration     = int(ability["feature"].split(':')[1])
                        else:
                            stateFeature = ability["feature"]
                            duration     = 1

                        for abilityEntityId in abilityTargetIdList:
                            if (stateFeature == "bodyguard"):
                                state["feature"]    = "bodyguard"
                                state["value"]      = abilityEntityId
                                state["duration"]   = -1
                                self._entitiesDict[selfId].addState(state)
                                state["feature"]    = "bodyguarded"
                                state["value"]      = selfId     
                                state["duration"]   = -1
                                self._entitiesDict[abilityEntityId].addState(state)
                            else:
                                state["feature"]    = stateFeature
                                state["value"]      = value
                                state["duration"]   = duration
                                self._entitiesDict[abilityEntityId].addState(state)

                    elif (ability["behavior"] == "summon"):
                        entityId = self.appendEntity(playerId, ability["feature"], self._playersDict[playerId].team, self._entitiesDict[targetEntityIdList[0]].x, self._entitiesDict[targetEntityIdList[0]].y)
                        self.executeAbilities(self._entitiesDict[entityId].abilities, "spawn", playerId, entityId, [])

                    elif (ability["behavior"] == "attackAgain"):
                        for abilityEntityId in abilityTargetIdList:
                            self._entitiesDict[abilityEntityId].attackAgain()

                    elif (ability["behavior"] == "freeAura"):
                        self._entitiesDict[selfId].freeAura()

                    elif (ability["behavior"] == "draw"):
                        self._playersDict[abilityTargetIdList[0]].draw(value, ability["feature"])

                    # If stopTrigger is defined, the ability must be added to the ongoingAbilityList
                    if stopTrigger and not(force):
                        ongoingAbilityDict = {}
                        copiedAbility = copy.deepcopy(ability)
                        copiedAbility["mult"]               = mult
                        ongoingAbilityDict["ability"]       = copiedAbility
                        ongoingAbilityDict["playerId"]      = playerId
                        ongoingAbilityDict["selfId"]        = selfId
                        ongoingAbilityDict["spellId"]       = spellId
                        ongoingAbilityDict["stopTrigger"]   = stopTrigger
                        self._ongoingAbilityList.append(ongoingAbilityDict)

                # Check if an aura has been used / aura must be specified only once by aura ability
                if (executed and ability["behavior"] == "aura"):
                    auraUsed = True

        if auraUsed:
            self._entitiesDict[selfId].consumeAura(1)

    def removeOngoingAbilities(self, stopTrigger, selfId=None):
        copyOngoingAbilityList = list(self._ongoingAbilityList)
        for ongoingAbility in copyOngoingAbilityList:
            if (stopTrigger == ongoingAbility["stopTrigger"]):
                if (ongoingAbility["ability"]["feature"] == "bodyguard" and selfId == ongoingAbility["selfId"]):
                    for state in self._entitiesDict[ongoingAbility["selfId"]].states:
                        if (state["feature"] == "bodyguard"):
                            bodyguardedId = state["value"]
                            break
                    self._entitiesDict[ongoingAbility["selfId"]].removeState("bodyguard")
                    self._entitiesDict[bodyguardedId].removeState("bodyguarded")
                    self._ongoingAbilityList.remove(ongoingAbility)
                else:
                    if (ongoingAbility["selfId"] in list(self._entitiesDict.keys()) and (ongoingAbility["spellId"] == None or ongoingAbility["spellId"] in list(self._playersDict[ongoingAbility["playerId"]].handSpellDict.keys()))):
                        ongoingAbility["ability"]["value"] = -ongoingAbility["ability"]["value"]
                        self.executeAbilities([ongoingAbility["ability"]], "", ongoingAbility["playerId"], ongoingAbility["selfId"], [], spellId=ongoingAbility["spellId"], force=True)
                        self._ongoingAbilityList.remove(ongoingAbility)
            elif (stopTrigger == "always" and ongoingAbility["stopTrigger"] == "noArmor"):
                if (self._entitiesDict[self._playersDict[ongoingAbility["playerId"]].heroEntityId].armor == 0):
                    ongoingAbility["ability"]["value"] = -ongoingAbility["ability"]["value"]
                    self.executeAbilities([ongoingAbility["ability"]], "", ongoingAbility["playerId"], ongoingAbility["selfId"], [], spellId=ongoingAbility["spellId"], force=True)
                    self._ongoingAbilityList.remove(ongoingAbility)