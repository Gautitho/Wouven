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
        self._nextEntityId          = 0
        self._nextTileEntityId      = 0
        self._entitiesDict          = {}
        self._playersDict           = {}
        self._ongoingAbilityList    = []
        self._oneByTurnAbilityList  = []
        self._turn                  = "blue"

    @property
    def entitiesDict(self):
        return dict(self._entitiesDict)

    @property
    def playersDict(self):
        return dict(self._playersDict)

    @property
    def turn(self):
        return self._turn

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

    def removeEntity(self, entityId, sendBack=False):
        found = False
        self.removeOngoingAbilities("death", selfId=entityId)
        self.executeAbilities(self._entitiesDict[entityId].abilities, "death", self.getPlayerIdFromTeam(self._entitiesDict[entityId].team), entityId, [None])
        for playerId in list(self._playersDict.keys()):
            if entityId in self._playersDict[playerId].boardEntityIds:
                self._playersDict[playerId].removeEntity(entityId, sendBack)
                found = True
                break
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

    def entityIdAdjacentToTile(self, x, y, team):
        entityIdList = []
        matchId = self.entityIdOnTile(x-1, y)
        if (matchId != None):
            if (team == "all" or team == self._entitiesDict[matchId].team):
                entityIdList.append(matchId)
        matchId = self.entityIdOnTile(x+1, y)
        if (matchId != None):
            if (team == "all" or team == self._entitiesDict[matchId].team):
                entityIdList.append(matchId)
        matchId = self.entityIdOnTile(x, y-1)
        if (matchId != None):
            if (team == "all" or team == self._entitiesDict[matchId].team):
                entityIdList.append(matchId)
        matchId = self.entityIdOnTile(x, y+1)
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

    def entityIdFirstAlignedToTile(self, x, y, team):
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

    def entityIdAlignedToTileInDirection(self, xStart, yStart, xDir, yDir, rangeCondition, team):
        entityIdList = []
        if (yStart == yDir):
            rangeCondition = BOARD_COLS if rangeCondition == -1 else rangeCondition
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
            rangeCondition = BOARD_ROWS if rangeCondition == -1 else rangeCondition
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
        rangeCondition = rangeCondition if rangeCondition > -1 else 100
        for xa in range(max(x-rangeCondition, 0), min(x+rangeCondition+1, BOARD_COLS)):
            for ya in range(max(y-(rangeCondition - (x-xa)), 0), min(y+(rangeCondition - (xa-x))+1, BOARD_ROWS)):
                matchId = self.entityIdOnTile(xa, ya)
                if (matchId != None):
                    if (team == "all" or team == self._entitiesDict[matchId].team):
                        entityIdList.append(matchId)
        return entityIdList

    def entityIdFromDescId(self, descId, team):
        for eid in list(self._entitiesDict.keys()):
            if (type(self._entitiesDict[eid]).__name__ == "Entity"):
                if (self._entitiesDict[eid].descId == descId and team == self._entitiesDict[eid].team):
                    return eid
        return None

    def entityIdWithHighestPv(self, team):
        entityIdList = []
        highestPv = 0
        for eid in list(self._entitiesDict.keys()):
            if (type(self._entitiesDict[eid]).__name__ == "Entity"):
                if (team == "all" or team == self._entitiesDict[eid].team):
                    if (self._entitiesDict[eid].pv > highestPv):
                        entityIdList = []
                        entityIdList.append(eid)
                        highestPv = self._entitiesDict[eid].pv
                    elif (self._entitiesDict[eid].pv == highestPv):
                        entityIdList.append(eid)
        return entityIdList

    def isAdjacentToTile(self, xSelf, ySelf, xTarget, yTarget):
        return ((xTarget == xSelf and (yTarget == ySelf + 1 or yTarget == ySelf - 1)) or (yTarget == ySelf and (xTarget == xSelf + 1 or xTarget == xSelf - 1)))

    def isAlignedToTile(self, xSelf, ySelf, xTarget, yTarget):
        return ((xTarget == xSelf) ^ (yTarget == ySelf))

    def startTurn(self, playerId):
        self._oneByTurnAbilityList = []
        self.removeOngoingAbilities("startTurn", playerId=playerId)
        self._turn = self._playersDict[playerId].team
        self._playersDict[playerId].startTurn()
        for entityId in self._playersDict[playerId].boardEntityIds:
            self._entitiesDict[entityId].startTurn()
            self.executeAbilities(self._entitiesDict[entityId].abilities, "startTurn", self.getPlayerIdFromTeam(self._entitiesDict[entityId].team), entityId, [None])

    def endTurn(self, playerId):
        self.removeOngoingAbilities("endTurn", playerId=playerId)
        self._playersDict[playerId].endTurn()
        for entityId in self._playersDict[playerId].boardEntityIds:
            self._entitiesDict[entityId].endTurn()
            self.executeAbilities(self._entitiesDict[entityId].abilities, "endTurn", self.getPlayerIdFromTeam(self._entitiesDict[entityId].team), entityId, [None])

    def useReserve(self, playerId):
        self._playersDict[playerId].useReserve()

    # This function is called after each action
    def always(self):
        self.garbageCollector()
        self.removeOngoingAbilities("always")
        self.removeOngoingAbilities("alwaysAfterEnd")
        for entityId in list(self._entitiesDict.keys()):
            self.executeAbilities(self._entitiesDict[entityId].abilities, "always", self.getPlayerIdFromTeam(self._entitiesDict[entityId].team), entityId, [None])
            self._entitiesDict[entityId].endAction()
            self.executeAbilities(self._entitiesDict[entityId].abilities, "alwaysAfterEnd", self.getPlayerIdFromTeam(self._entitiesDict[entityId].team), entityId, [None])
            self._entitiesDict[entityId].endAction()
        for playerId in list(self._playersDict.keys()):
            if (self._playersDict[playerId].heroEntityId in self._entitiesDict):
                for spellIdx in range(0, len(list(self._playersDict[playerId].handSpellDict.keys()))):
                    spellId = list(self._playersDict[playerId].handSpellDict.keys())[spellIdx]
                    self.executeAbilities(self._playersDict[playerId].handSpellDict[spellId].abilities, "always", playerId, self._playersDict[playerId].heroEntityId, [None], spellId=spellId)
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
        self.executeAbilities(self._entitiesDict[entityId].abilities, "move", playerId, entityId, [None])
        if (attackedEntityId != None):
            self.executeAbilities(self._entitiesDict[entityId].abilities, "attack", playerId, entityId, [attackedEntityId])
            self.executeAbilities(self._entitiesDict[attackedEntityId].abilities, "attacked", playerId, attackedEntityId, [entityId])
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
                    if (spell.race in [self._entitiesDict[self._playersDict[playerId].heroEntityId].descId, self._playersDict[playerId].race]):
                        selfEntityId        = self._playersDict[playerId].heroEntityId
                    else:
                        selfEntityId        = self.entityIdFromDescId(spell.race, self._playersDict[playerId].team)
                    if (selfEntityId == None):
                        raise GameException("Race of self entity is not known !")

                    for allowedTargetIdx in range(0, len(spell.allowedTargetList)):
                        targetDict = {}
                        targetDict["entity"]        = False         if not("entity" in spell.allowedTargetList[allowedTargetIdx])       else bool(spell.allowedTargetList[allowedTargetIdx]["entity"])
                        targetDict["empty"]         = False         if not("empty" in spell.allowedTargetList[allowedTargetIdx])        else bool(spell.allowedTargetList[allowedTargetIdx]["empty"])
                        targetDict["main"]          = "all"         if not("main" in spell.allowedTargetList[allowedTargetIdx])         else spell.allowedTargetList[allowedTargetIdx]["main"]
                        targetDict["ref"]           = "self"        if not("ref" in spell.allowedTargetList[allowedTargetIdx])          else spell.allowedTargetList[allowedTargetIdx]["ref"]
                        targetDict["team"]          = "all"         if not("team" in spell.allowedTargetList[allowedTargetIdx])         else spell.allowedTargetList[allowedTargetIdx]["team"]
                        targetDict["typeList"]      = []            if not("typeList" in spell.allowedTargetList[allowedTargetIdx])     else spell.allowedTargetList[allowedTargetIdx]["typeList"]
                        targetDict["noTypeList"]    = []            if not("noTypeList" in spell.allowedTargetList[allowedTargetIdx])   else spell.allowedTargetList[allowedTargetIdx]["noTypeList"]

                        # Set reference tile
                        if (targetDict["ref"] == "self"):
                            refX = self._entitiesDict[selfEntityId].x
                            refY = self._entitiesDict[selfEntityId].y
                        elif (targetDict["ref"] == "firstTarget"):
                            if (len(targetEntityIdList) > 0):
                                refX = self._entitiesDict[targetEntityIdList[0]].x
                                refY = self._entitiesDict[targetEntityIdList[0]].y
                            else:
                                raise GameException("Wrong allowedTarget (ref) : No first target !")
                        else:
                            raise GameException("Wrong allowedTarget (ref) !")

                        # Entity and empty check
                        if (targetDict["entity"]):
                            targetEntityIdList.append(self.entityIdOnTile(targetPositionList[allowedTargetIdx]["x"], targetPositionList[allowedTargetIdx]["y"]))
                            if (targetEntityIdList[-1] != None):
                                if (self._entitiesDict[targetEntityIdList[-1]].isInStates("untargetable") and self._entitiesDict[targetEntityIdList[-1]].team == self.getOpTeam(self._entitiesDict[selfEntityId].team)):
                                    raise GameException("Target is untargetable !")
                            else:
                                raise GameException("Target must be an entity !")
                        else:
                            targetEntityIdList.append(self.appendTileEntity(targetPositionList[allowedTargetIdx]["x"], targetPositionList[allowedTargetIdx]["y"]))
                            if (targetDict["empty"]):
                                if (self.entityIdOnTile(targetPositionList[allowedTargetIdx]["x"], targetPositionList[allowedTargetIdx]["y"]) != None):
                                    raise GameException("Target tile must be empty !")

                        # Main check
                        if (targetDict["main"] == "all"):
                            pass
                        elif (targetDict["main"] == "adjacent"):
                            if not(self.isAdjacentToTile(refX, refY, targetPositionList[allowedTargetIdx]["x"], targetPositionList[allowedTargetIdx]["y"])):
                                raise GameException("Target must be adjacent to self !")
                        elif (targetDict["main"] == "aligned"):
                            if not(self.isAlignedToTile(refX, refY, targetPositionList[allowedTargetIdx]["x"], targetPositionList[allowedTargetIdx]["y"])):
                                raise GameException("Target must be aligned to self !")
                        elif (targetDict["main"] == "firstAligned"):
                            if not(targetEntityIdList[-1] in self.entityIdFirstAlignedToTile(refX, refY, "all")):
                                raise GameException("Target must be fisrt aligned to self !")
                        elif (targetDict["main"] == "hero"):
                            if not(targetEntityIdList[-1] in [self._playersDict[playerId].heroEntityId, self._playersDict[self.getOpPlayerId(playerId)].heroEntityId]):
                                raise GameException("Target must be an hero !")
                        elif (targetDict["main"] == "self"):
                            if not(targetEntityIdList[-1] == selfEntityId):
                                raise GameException("Target must be self (hero or associed companion) !")
                        else:
                            raise GameException("Wrong allowedTarget (main) !")

                        # Team check
                        if (targetDict["team"] == "my"):
                            if (self._entitiesDict[targetEntityIdList[-1]].team == self.getOpTeam(self._entitiesDict[selfEntityId].team)):
                                raise GameException("Target must be in your team !")
                        elif (targetDict["team"] == "op"):
                            if (self._entitiesDict[targetEntityIdList[-1]].team == self._entitiesDict[selfEntityId].team):
                                raise GameException("Target must be in your opponent team !")

                        # Type check
                        if (targetDict["entity"]):
                            typeFoundList = [False for i in targetDict["typeList"]]
                            for entityType in self._entitiesDict[targetEntityIdList[-1]].typeList:
                                if (entityType in targetDict["noTypeList"]):
                                    raise GameException(f"Target can't be of type ({entityType}) !")
                                for i in range(len(targetDict["typeList"])):
                                    if (entityType == targetDict["typeList"][i]):
                                        typeFoundList[i] = True
                            if (False in typeFoundList):
                                raise GameException(f"Target miss some mandatory type !")
                else:
                    raise GameException("Wrong number of target !")

                # Execute spell
                self.removeOngoingAbilities("spellCast") # WARNING : This line is here only because, for now, the only spellCast ongoingAbilities affect cost
                self.executeAbilities(spell.abilities, "spellCast", playerId, selfEntityId, targetEntityIdList, spellElem=spell.elem, allowedTargetList=spell.allowedTargetList)
                for entityId in [e for e in list(self._entitiesDict.keys()) if not("tile" in str(e))]:
                    self.executeAbilities(self._entitiesDict[entityId].abilities, "spellCast", playerId, entityId, targetEntityIdList, spellElem=spell.elem, allowedTargetList=spell.allowedTargetList)
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
                        elif (placement["ref"] == "myHero"):
                            if (calcDist(self._entitiesDict[self._playersDict[playerId].heroEntityId].x, self._entitiesDict[self._playersDict[playerId].heroEntityId].y, summonPositionList[0]["x"], summonPositionList[0]["y"]) <= placement["range"]):
                                placementValid = True
                        else:
                            raise GameException("Summon reference not allowed !")

                    # Summon
                    if placementValid:
                        entityId = self.appendEntity(playerId, companion["entityDescId"], self._playersDict[playerId].team, summonPositionList[0]["x"], summonPositionList[0]["y"])
                        self._entitiesDict[entityId].startTurn()
                        self._playersDict[playerId].summonCompanion(companionId, entityId)
                        self.executeAbilities(self._entitiesDict[entityId].abilities, "spawn", playerId, entityId, [None])
                        self.executeAbilities(self._entitiesDict[self._playersDict[playerId].heroEntityId].abilities, "summon", playerId, self._playersDict[playerId].heroEntityId, [entityId])

                    else:
                        raise GameException("Invalid companion placement !")
                else:
                    raise GameException("Companion not available !")
            else:
                raise GameException("Companion not in your deck !")
        else:
            raise GameException("Only one summon position is allowed !")

    def executeAbilities(self, abilityList, trigger, playerId, selfId, targetEntityIdList, spellElem=None, spellId=None, triggingAbility=None, allowedTargetList=None, passiveTriggedList=None, inAffectedIdList=None, force=False):
        auraUsed                        = False
        opPlayerId                      = self.getOpPlayerId(playerId) if playerId else ""
        elemStateToRemoveEntityIdList   = []
        for ability in abilityList:

            if (trigger == ability["trigger"] or force):

                passiveTriggerList  = [] # [{actor / trigger / targetId / value}] # Behavior to handle very specific cases, avoid it

                # Set stopTrigger
                stopTriggerList = [] if not("stopTriggerList" in ability) else ability["stopTriggerList"]

                # Set targetDict
                targetDict = {}
                targetDict["main"]              = "target"      if not("main" in ability["target"])             else ability["target"]["main"]
                targetDict["team"]              = "all"         if not("team" in ability["target"])             else ability["target"]["team"]
                targetDict["targetIdx"]         = 0             if not("targetIdx" in ability["target"])        else int(ability["target"]["targetIdx"])
                targetDict["range"]             = -1            if not("range" in ability["target"])            else int(ability["target"]["range"])
                targetDict["typeList"]          = []            if not("typeList" in ability["target"])         else ability["target"]["typeList"]
                targetDict["noTypeList"]        = []            if not("noTypeList" in ability["target"])       else ability["target"]["noTypeList"]
                targetDict["ref"]               = "self"        if not("ref" in ability["target"])              else ability["target"]["ref"]
                targetDict["refIdx"]            = 0             if not("refIdx" in ability["target"])           else int(ability["target"]["refIdx"])
                targetDict["refTypeList"]       = []            if not("refTypeList" in ability["target"])      else ability["target"]["refTypeList"]
                targetDict["refNoTypeList"]     = []            if not("refNoTypeList" in ability["target"])    else ability["target"]["refNoTypeList"]

                # Team
                affectedPlayerIdList = []
                if (targetDict["team"] == "my"):
                    team = self._entitiesDict[selfId].team
                    affectedPlayerIdList.append(self.getPlayerIdFromTeam(team))
                elif (targetDict["team"] == "op"):
                    team = self.getOpTeam(self._entitiesDict[selfId].team)
                    affectedPlayerIdList.append(self.getPlayerIdFromTeam(team))
                elif (targetDict["team"] == "all"):
                    team = "all"
                    affectedPlayerIdList.append(playerId)
                    affectedPlayerIdList.append(opPlayerId)
                elif (targetDict["team"] == "target"):
                    team = self._entitiesDict[targetEntityIdList[targetDict["targetIdx"]]].team
                    affectedPlayerIdList.append(self.getPlayerIdFromTeam(self._entitiesDict[targetEntityIdList[targetDict["targetIdx"]]].team))
                else:
                    raise GameException("Wrong ability target (team) !")

                # Reference
                if (targetDict["ref"] == "self"):
                    refIdList = [selfId]
                elif (targetDict["ref"] == "target"):
                    refIdList = [targetEntityIdList[targetDict["refIdx"]]]
                elif (targetDict["ref"] == "myHero"):
                    refIdList = [self._playersDict[playerId].heroEntityId]
                elif (targetDict["ref"] == "opHero"):
                    refIdList = [self._playersDict[opPlayerId].heroEntityId]
                elif (targetDict["ref"] == "myBoard"):
                    refIdList = self._playersDict[playerId].boardEntityIds
                else:
                    raise GameException("Wrong ability target (ref) !")

                for refId in list(refIdList):
                    typeFoundList = [False for i in targetDict["refTypeList"]]
                    if (refId != None):
                        if (type(self._entitiesDict[refId]).__name__ == "Entity"):
                            for entityType in self._entitiesDict[refId].typeList:
                                if (entityType in targetDict["refNoTypeList"]):
                                    refIdList.remove(refId)
                                    break
                                for i in range(len(targetDict["refTypeList"])):
                                    if (entityType == targetDict["refTypeList"][i]):
                                        typeFoundList[i] = True
                            if (False in typeFoundList):
                                refIdList.remove(refId)

                # Main
                abilityTargetIdList = []
                if (targetDict["main"] == "target"):
                    abilityTargetIdList.append(targetEntityIdList[targetDict["targetIdx"]])
                elif (targetDict["main"] == "self"):
                    abilityTargetIdList.append(selfId)
                elif (targetDict["main"] == "player"):
                    for afpId in affectedPlayerIdList:
                        abilityTargetIdList.append(afpId)
                elif (targetDict["main"] == "hero"):
                    for afpId in affectedPlayerIdList:
                        abilityTargetIdList.append(self._playersDict[afpId].heroEntityId)
                elif (targetDict["main"] == "around"):
                    for refId in refIdList:
                        abilityTargetIdList.extend(self.entityIdAroundTile(self._entitiesDict[refId].x, self._entitiesDict[refId].y, team))
                elif (targetDict["main"] == "adjacent"):
                    for refId in refIdList:
                        abilityTargetIdList.extend(self.entityIdAdjacentToTile(self._entitiesDict[refId].x, self._entitiesDict[refId].y, team))
                elif (targetDict["main"] == "aligned"):
                    for refId in refIdList:
                        abilityTargetIdList.extend(self.entityIdAlignedToTile(self._entitiesDict[refId].x, self._entitiesDict[refId].y, team))
                elif (targetDict["main"] == "firstAligned"):
                    for refId in refIdList:
                        abilityTargetIdList.extend(self.entityIdFirstAlignedToTile(self._entitiesDict[refId].x, self._entitiesDict[refId].y, team))
                elif (targetDict["main"] == "alignedInDirection"):
                    for refId in refIdList:
                        abilityTargetIdList.extend(self.entityIdAlignedToTileInDirection(self._entitiesDict[refId].x, self._entitiesDict[refId].y, self._entitiesDict[targetEntityIdList[targetDict["targetIdx"]]].x, self._entitiesDict[targetEntityIdList[targetDict["targetIdx"]]].y, targetDict["range"], team))
                elif (targetDict["main"] == "cross"):
                    abilityTargetIdList.extend(self.entityIdInCross(self._entitiesDict[targetEntityIdList[targetDict["targetIdx"]]].x, self._entitiesDict[targetEntityIdList[targetDict["targetIdx"]]].y, targetDict["range"], team))
                elif (targetDict["main"] == "board"):
                    for afpId in affectedPlayerIdList:
                        abilityTargetIdList.extend(self._playersDict[afpId].boardEntityIds)
                elif (targetDict["main"] == "highestPv"):
                    abilityTargetIdList.extend(self.entityIdWithHighestPv(team))
                elif (targetDict["main"] == "currentSpell"):
                    abilityTargetIdList.append(spellId)
                elif (targetDict["main"] == "hand"):
                    if (force):
                        abilityTargetIdList.extend(list(set(inAffectedIdList).intersection(self._playersDict[playerId].handSpellDict.keys())))
                    else:
                        abilityTargetIdList.extend(list(self._playersDict[playerId].handSpellDict.keys())) # WARNING : if a spell is draw, it is not taken
                else:
                    raise GameException("Wrong ability target (main) !")

                if not(targetDict["main"] in ["player", "currentSpell", "hand"]):
                    # Check if targetList still exist : Removed entity during a previous ability in the same action
                    for targetId in abilityTargetIdList:
                        if (targetId != None):
                            if not(targetId in list(self._entitiesDict.keys())):
                                abilityTargetIdList.remove(targetId)

                    # Type
                    for targetId in list(abilityTargetIdList):
                        typeFoundList = [False for i in targetDict["typeList"]]
                        if (targetId != None):
                            if (type(self._entitiesDict[targetId]).__name__ == "Entity"):
                                for entityType in self._entitiesDict[targetId].typeList:
                                    if (entityType in targetDict["noTypeList"]):
                                        abilityTargetIdList.remove(targetId)
                                        break
                                    for i in range(len(targetDict["typeList"])):
                                        if (entityType == targetDict["typeList"][i]):
                                            typeFoundList[i] = True
                                if (False in typeFoundList):
                                    abilityTargetIdList.remove(targetId)

                # Check conditions
                conditionsValid = True
                for condition in ability["conditionList"]:
                    conditionDict = {}
                    conditionDict["feature"]    = "none"            if not("feature" in condition)      else condition["feature"]
                    conditionDict["operator"]   = "=="              if not("operator" in condition)     else condition["operator"]
                    conditionDict["target"]     = "abilityTarget"   if not("target" in condition)       else condition["target"]
                    conditionDict["targetIdx"]  = 0                 if not("targetIdx" in condition)    else int(condition["targetIdx"])
                    conditionDict["ref"]        = "self"            if not("ref" in condition)          else condition["ref"]
                    conditionDict["refIdx"]     = 0                 if not("refIdx" in condition)       else int(condition["refIdx"])
                    conditionDict["value"]      = "0"               if not("value" in condition)        else condition["value"]
                    conditionDict["trigger"]    = "all"             if not("trigger" in condition)      else condition["trigger"]

                    # Target
                    if (conditionDict["target"] == "spellTarget"):
                        conditionTargetId = targetEntityIdList[conditionDict["targetIdx"]]
                        if not(conditionTargetId in list(self._entitiesDict.keys())): # Removed entity during a previous ability in the same action
                            conditionsValid = False
                            break
                    elif (conditionDict["target"] == "spellTargetPlayer"):
                        conditionTargetId = self.getPlayerIdFromTeam(self._entitiesDict[targetEntityIdList[conditionDict["targetIdx"]]].team)
                    elif (conditionDict["target"] == "abilityTarget"):
                        conditionTargetId = abilityTargetIdList[conditionDict["targetIdx"]]
                        if not(conditionTargetId in list(self._entitiesDict.keys())): # Removed entity during a previous ability in the same action
                            conditionsValid = False
                            break
                    elif (conditionDict["target"] == "self"):
                        conditionTargetId = selfId
                        if not(conditionTargetId in list(self._entitiesDict.keys())): # Removed entity during a previous ability in the same action
                            conditionsValid = False
                            break
                    elif (conditionDict["target"] == "myPlayer"):
                        conditionTargetId = self.getPlayerIdFromTeam(self._entitiesDict[selfId].team)
                    elif (conditionDict["target"] == "opPlayer"):
                        conditionTargetId = self.getPlayerIdFromTeam(self.getOpTeam(self._entitiesDict[selfId].team))
                    elif (conditionDict["target"] == "none"):
                        pass
                    else:
                        raise GameException("Wrong condition (target) !")

                    # Operator
                    if not(conditionDict["operator"] in ["==", "!=", ">", "<", ">=", "<="]):
                        raise GameException("Wrong condition (operator) !")

                    operatorDict = {'==':   lambda x, y: x == y,
                                    '!=':   lambda x, y: x != y,
                                    '>':    lambda x, y: x > y,
                                    '<':    lambda x, y: x < y,
                                    '>=':   lambda x, y: x >= y,
                                    '<=':   lambda x, y: x <= y}
                    
                    # Reference
                    if (conditionDict["ref"] == "self"):
                        conditionRefId = selfId
                    elif (conditionDict["ref"] == "myHero"):
                        conditionRefId = self._playersDict[playerId].heroEntityId
                    elif (conditionDict["ref"] == "opHero"):
                        conditionRefId = self._playersDict[opPlayerId].heroEntityId
                    elif (conditionDict["ref"] == "abilityTarget"):
                        conditionRefId = abilityTargetIdList[conditionDict["refIdx"]]
                    elif (conditionDict["ref"] == "spellTarget"):
                        conditionRefId = targetEntityIdList[conditionDict["refIdx"]]

                    # Feature
                    if (conditionDict["feature"] in ["elemState", "state", "type", "team", "pv", "auraNb"]):
                        if not(type(self._entitiesDict[conditionTargetId]).__name__ == "Entity"):
                            conditionsValid = False
                            break

                    if (conditionDict["feature"] == "none"):
                        pass
                    elif (conditionDict["feature"] == "elemState"):
                        if (conditionDict["value"] in ["oiled", "wet", "muddy", "windy"]):
                            if (operatorDict[conditionDict["operator"]](self._entitiesDict[conditionTargetId].elemState, conditionDict["value"])):
                                if (conditionDict["operator"] == "=="):
                                    elemStateToRemoveEntityIdList.append(conditionTargetId)
                            else:
                                conditionsValid = False
                                break
                        else:
                            raise GameException("ElemState to consume does not exist !")

                    elif (conditionDict["feature"] == "state"):
                        if not(conditionDict["operator"] == "==" and self._entitiesDict[conditionTargetId].isInStates(conditionDict["value"])):
                            conditionsValid = False
                            break

                    elif (conditionDict["feature"] == "elem"):
                        if (conditionDict["value"] in ["fire", "water", "earth", "air", "neutral"]):
                            if (targetDict["main"] == "hand"):
                                for spellIdIt in list(abilityTargetIdList):
                                    if not(operatorDict[conditionDict["operator"]](self._playersDict[playerId].handSpellDict[spellIdIt].elem, conditionDict["value"])):
                                        abilityTargetIdList.remove(spellIdIt)
                            elif not(operatorDict[conditionDict["operator"]](spellElem, conditionDict["value"])):
                                conditionsValid = False
                                break
                        else:
                            raise GameException("Elem of the spell does not exist !")

                    elif (conditionDict["feature"] == "paStock"):
                        if not(operatorDict[conditionDict["operator"]](self._playersDict[conditionTargetId].paStock, int(conditionDict["value"]))):
                            conditionsValid = False
                            break

                    elif (conditionDict["feature"] == "myCompanions"):
                        myCompanions = 0
                        for companion in self._playersDict[playerId].companionList:
                            if (companion["state"] == "alive"):
                                myCompanions += 1
                        if not(operatorDict[conditionDict["operator"]](myCompanions, int(conditionDict["value"]))):
                            conditionsValid = False
                            break

                    elif (conditionDict["feature"] == "myMechanisms"):
                        myMechanisms = 0
                        for eid in self._playersDict[playerId].boardEntityIds:
                            if ("mechanism" in self._entitiesDict[eid].typeList):
                                myMechanisms += 1
                        if not(operatorDict[conditionDict["operator"]](myMechanisms, int(conditionDict["value"]))):
                            conditionsValid = False
                            break

                    elif (conditionDict["feature"] == "range"):
                        if (operatorDict[conditionDict["operator"]](calcDist(self._entitiesDict[conditionRefId].x, self._entitiesDict[conditionRefId].y, self._entitiesDict[conditionTargetId].x, self._entitiesDict[conditionTargetId].y), int(conditionDict["value"]))):
                            rangeCondition = condition["value"]
                        else:
                            conditionsValid = False
                            break

                    elif (conditionDict["feature"] == "turn"):
                        if (conditionDict["value"] == "my" and self._entitiesDict[selfId].myTurn):
                            pass
                        elif (conditionDict["value"] == "op" and not(self._entitiesDict[selfId].myTurn)):
                            pass
                        else:
                            conditionsValid = False
                            break

                    elif (conditionDict["feature"] == "team"):
                        if (conditionDict["value"] == "my" and self._entitiesDict[conditionTargetId].team == self._entitiesDict[selfId].team):
                            pass
                        elif (conditionDict["value"] == "op" and self._entitiesDict[conditionTargetId].team == self.getOpTeam(self._entitiesDict[selfId].team)):
                            pass
                        else:
                            conditionsValid = False
                            break

                    elif (conditionDict["feature"] == "type"):
                        if (conditionDict["operator"] == "=="):
                            if not(conditionDict["value"] in self._entitiesDict[conditionTargetId].typeList):
                                conditionsValid = False
                                break
                        elif (conditionDict["operator"] == "!="):
                            if (conditionDict["value"] in self._entitiesDict[conditionTargetId].typeList):
                                conditionsValid = False
                                break

                    elif (conditionDict["feature"] == "allowedTarget"):
                        if (conditionDict["value"] == "aligned"):
                            if not("main" in allowedTargetList[targetDict["targetIdx"]]):
                                conditionsValid = False
                                break
                            else:
                                if not(allowedTargetList[targetDict["targetIdx"]]["main"] in ["aligned", "firstAligned"]):
                                    conditionsValid = False
                                    break

                    elif (conditionDict["feature"] == "opsAround"):
                        if not(operatorDict[conditionDict["operator"]](len(self.entityIdAroundTile(self._entitiesDict[conditionTargetId].x, self._entitiesDict[conditionTargetId].y, self.getOpTeam(self._entitiesDict[conditionTargetId].team))), int(conditionDict["value"]))):
                            conditionsValid = False
                            break

                    elif (conditionDict["feature"] == "spellsPlayedDuringTurn"):
                        if not(operatorDict[conditionDict["operator"]](self._playersDict[playerId].spellsPlayedDuringTurn, int(conditionDict["value"]))):
                            conditionsValid = False
                            break

                    elif (conditionDict["feature"] == "pv"):
                        if not(operatorDict[conditionDict["operator"]](self._entitiesDict[conditionTargetId].pv, int(conditionDict["value"]))):
                            conditionsValid = False
                            break

                    elif (conditionDict["feature"] == "auraNb"):
                        if not(operatorDict[conditionDict["operator"]](self._entitiesDict[conditionTargetId].aura["nb"], int(conditionDict["value"]))):
                            conditionsValid = False
                            break

                    elif (conditionDict["feature"] == "oneByTurn"):
                        if (conditionDict["value"] in self._oneByTurnAbilityList):
                            conditionsValid = False
                            break

                    elif (conditionDict["feature"] == "behavior"):
                        if not(conditionDict["value"] == triggingAbility["behavior"]):
                            conditionsValid = False
                            break

                    elif (conditionDict["feature"] == "feature"):
                        if not(conditionDict["value"] == triggingAbility["feature"]):
                            conditionsValid = False
                            break

                    elif (conditionDict["feature"] == "handSpells"):
                        if not(operatorDict[conditionDict["operator"]](len(list(self._playersDict[conditionTargetId].handSpellDict.keys())), int(conditionDict["value"]))):
                            conditionsValid = False
                            break

                    # Custom case
                    elif (conditionDict["feature"] == "passive"):
                        found = False
                        for passive in passiveTriggedList:
                            if (conditionDict["value"] == passive["action"] and conditionTargetId == passive["actorId"] and conditionDict["trigger"] in ["all", passive["trigger"]]):
                                found = True
                                break

                        if not(found):
                            conditionsValid = False
                            break

                    else:
                        raise GameException("Wrong condition (feature) !")

                if (not(conditionsValid) and ability["break"] == "True"):
                    raise GameException("The conditions to launch this spell are not respected !")

                if (conditionsValid):
                    for condition in ability["conditionList"]:
                        if (condition["feature"] == "oneByTurn"):
                            self._oneByTurnAbilityList.append(condition["value"])

                # Handle variable value case
                if isinstance(ability["value"], int):
                    value = ability["value"]
                elif isinstance(ability["value"], dict):
                    value = ability["value"]
                elif isinstance(ability["value"], str):
                    refId = refIdList[0]
                    refPlayerId = self.getPlayerIdFromTeam(self._entitiesDict[refId].team)
                    if (ability["value"] == "-atk"):
                        value = -self._entitiesDict[refId].atk
                    elif (ability["value"] == "atk"):
                        value = self._entitiesDict[refId].atk
                    elif (ability["value"] == "pa"):
                        value = self._playersDict[refPlayerId].pa
                    elif (ability["value"] == "paStock"):
                        value = self._playersDict[refPlayerId].paStock
                    elif (ability["value"] == "pv"):
                        value = self._entitiesDict[refId].pv
                    elif (ability["value"] == "-pv"):
                        value = -self._entitiesDict[refId].pv
                    elif (ability["value"] == "kokoroPassiveValue"):
                        value = 0
                        for passive in passiveTriggedList:
                            if (passive["action"] == "heal" and passive["actorId"] != selfId and self._entitiesDict[passive["actorId"]].team == self._entitiesDict[selfId].team):
                                value += passive["value"] 
                    else:
                        value = ability["value"]
                else:
                    raise GameException(f"Ability value {ability['value']} must be an int, an str or a dict !")
                   
                # Execute ability
                executed = False
                mult = 1 if not("mult" in ability) else ability["mult"] # Usefull to handle stopTrigger case
                if (conditionsValid or force):
                    affectedIdList = list(abilityTargetIdList)
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
                                    pvVar = self._entitiesDict[guardId].modifyPv(value)
                                else:
                                    pvVar = self._entitiesDict[abilityEntityId].modifyPv(value)
                                if (pvVar > 0):
                                    passiveTriggerList.append({"action" : "heal", "trigger" : trigger, "actorId" : abilityEntityId, "value" : pvVar})
                                if (ability["feature"] == "stealLife"):
                                    self._entitiesDict[selfId].modifyPv(-pvVar)
                                    if (-pvVar > 0):
                                        passiveTriggerList.append({"action" : "heal", "trigger" : trigger, "actorId" : selfId, "value" : -pvVar})
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
                            self._entitiesDict[abilityTargetIdList[targetDict["targetIdx"]]].tp(self._entitiesDict[targetEntityIdList[value]].x, self._entitiesDict[targetEntityIdList[value]].y)
                            passiveTriggerList.append({"action" : "deplace", "trigger" : trigger, "actorId" : abilityTargetIdList[targetDict["targetIdx"]]})
                            passiveTriggerList.append({"action" : "tp", "trigger" : trigger, "actorId" : abilityTargetIdList[targetDict["targetIdx"]]})
                            executed = True
                        elif (ability["feature"] == "paStock"):
                            self._playersDict[abilityTargetIdList[0]].modifyPaStock(value)
                            executed = True
                        elif (ability["feature"] == "armor"):
                            for abilityEntityId in abilityTargetIdList:
                                self._entitiesDict[abilityEntityId].modifyArmor(value)
                                passiveTriggerList.append({"action" : "armorWin", "trigger" : trigger, "actorId" : abilityEntityId})
                                executed = True
                        elif (ability["feature"] == "cost"):
                            for spellIdIt in abilityTargetIdList:
                                self._playersDict[playerId].modifySpellCost(spellIdIt, value)
                                executed = True

                    elif (ability["behavior"] == "swap"):
                        x = self._entitiesDict[selfId].x
                        y = self._entitiesDict[selfId].y
                        self._entitiesDict[selfId].tp(self._entitiesDict[abilityTargetIdList[value]].x, self._entitiesDict[abilityTargetIdList[value]].y)
                        passiveTriggerList.append({"action" : "deplace", "trigger" : trigger, "actorId" : selfId})
                        passiveTriggerList.append({"action" : "tp", "trigger" : trigger, "actorId" : selfId})
                        self._entitiesDict[abilityTargetIdList[value]].tp(x, y)
                        passiveTriggerList.append({"action" : "deplace", "trigger" : trigger, "actorId" : abilityTargetIdList[value]})
                        passiveTriggerList.append({"action" : "tp", "trigger" : trigger, "actorId" : abilityTargetIdList[value]})
                        executed = True

                    elif (ability["behavior"] == "melee"):
                        multIdList = list(self.entityIdAroundTile(self._entitiesDict[selfId].x, self._entitiesDict[selfId].y, self._playersDict[opPlayerId].team))
                        for eid in multIdList:
                            for entityType in self._entitiesDict[eid].typeList:
                                if (entityType in ["mechanism"]):
                                    multIdList.remove(eid)
                                    break
                        mult = len(multIdList) if not(force) else mult # Handle the stopTrigger case
                        if (ability["feature"] == "pv"): 
                            pvVar = self._entitiesDict[abilityTargetIdList[targetDict["targetIdx"]]].modifyPv(mult*value)
                            if (pvVar > 0):
                                passiveTriggerList.append({"action" : "heal", "trigger" : trigger, "actorId" : abilityTargetIdList[targetDict["targetIdx"]], "value" : pvVar})
                            executed = True
                        elif (ability["feature"] == "atk"): 
                            self._entitiesDict[abilityTargetIdList[targetDict["targetIdx"]]].modifyAtk(mult*value)
                            executed = True
                        elif (ability["feature"] == "armor"): 
                            self._entitiesDict[abilityTargetIdList[targetDict["targetIdx"]]].modifyArmor(mult*value)
                            passiveTriggerList.append({"action" : "armorWin", "trigger" : trigger, "actorId" : abilityTargetIdList[targetDict["targetIdx"]]})
                            executed = True
                        elif (ability["feature"] == "cost"):
                            for spellIdIt in abilityTargetIdList:
                                self._playersDict[playerId].modifySpellCost(spellIdIt, mult*value)
                                executed = True

                    elif (ability["behavior"] == "melee+draw"):
                        multIdList = list(self.entityIdAroundTile(self._entitiesDict[selfId].x, self._entitiesDict[selfId].y, self._playersDict[opPlayerId].team))
                        for eid in multIdList:
                            for entityType in self._entitiesDict[eid].typeList:
                                if (entityType in ["mechanism"]):
                                    multIdList.remove(eid)
                                    break
                        mult = len(multIdList) if not(force) else mult # Handle the stopTrigger case
                        self._playersDict[abilityTargetIdList[targetDict["targetIdx"]]].draw(mult*value, ability["feature"])

                    elif (ability["behavior"] == "support"):
                        multIdList = list(self.entityIdAroundTile(self._entitiesDict[selfId].x, self._entitiesDict[selfId].y, self._playersDict[playerId].team))
                        for eid in multIdList:
                            for entityType in self._entitiesDict[eid].typeList:
                                if (entityType in ["mechanism"]):
                                    multIdList.remove(eid)
                                    break
                        mult = len(multIdList) if not(force) else mult # Handle the stopTrigger case
                        if (ability["feature"] == "pv"): 
                            pvVar = self._entitiesDict[abilityTargetIdList[targetDict["targetIdx"]]].modifyPv(mult*value)
                            if (pvVar > 0):
                                passiveTriggerList.append({"action" : "heal", "trigger" : trigger, "actorId" : abilityTargetIdList[targetDict["targetIdx"]], "value" : pvVar})
                            executed = True
                        elif (ability["feature"] == "atk"): 
                            self._entitiesDict[abilityTargetIdList[targetDict["targetIdx"]]].modifyAtk(mult*value)
                            executed = True
                        elif (ability["feature"] == "cost"):
                            for spellIdIt in abilityTargetIdList:
                                self._playersDict[playerId].modifySpellCost(spellIdIt, mult*value)
                                executed = True

                    elif (ability["behavior"] == "support+draw"):
                        multIdList = list(self.entityIdAroundTile(self._entitiesDict[selfId].x, self._entitiesDict[selfId].y, self._playersDict[playerId].team))
                        for eid in multIdList:
                            for entityType in self._entitiesDict[eid].typeList:
                                if (entityType in ["mechanism"]):
                                    multIdList.remove(eid)
                                    break
                        mult = len(multIdList) if not(force) else mult # Handle the stopTrigger case
                        self._playersDict[abilityTargetIdList[targetDict["targetIdx"]]].draw(mult*value, ability["feature"])

                    elif (ability["behavior"] == "distance"):
                        mult = calcDist(self._entitiesDict[selfId].x, self._entitiesDict[selfId].y, self._entitiesDict[abilityTargetIdList[0]].x, self._entitiesDict[abilityTargetIdList[0]].y, offset=-1) if not(force) else mult # Handle the stopTrigger case
                        if (ability["feature"] == "atk"): 
                            self._entitiesDict[selfId].modifyAtk(mult*value)
                            executed = True
                        elif (ability["feature"] == "cost"):
                            for spellIdIt in abilityTargetIdList:
                                self._playersDict[playerId].modifySpellCost(spellIdIt, mult*value)
                                executed = True
                        elif (ability["feature"] == "pv"):
                            for abilityEntityId in abilityTargetIdList:
                                pvVar = self._entitiesDict[abilityEntityId].modifyPv(mult*value)
                                if (pvVar > 0):
                                    passiveTriggerList.append({"action" : "heal", "trigger" : trigger, "actorId" : abilityEntityId, "value" : pvVar})
                                executed = True

                    elif (ability["behavior"] == "auraNb"):
                        mult = self._entitiesDict[selfId].aura["nb"] if not(force) else mult # Handle the stopTrigger case
                        if (ability["feature"] == "cost"):
                            for spellIdIt in abilityTargetIdList:
                                self._playersDict[playerId].modifySpellCost(spellIdIt, mult*value)
                                executed = True
                        elif (ability["feature"] == "pv"):
                            for abilityEntityId in abilityTargetIdList:
                                pvVar = self._entitiesDict[abilityEntityId].modifyPv(mult*value)
                                if (pvVar > 0):
                                    passiveTriggerList.append({"action" : "heal", "trigger" : trigger, "actorId" : abilityEntityId, "value" : pvVar})
                                executed = True
                        elif (ability["feature"] == "pm"):
                            for abilityEntityId in abilityTargetIdList:
                                self._entitiesDict[abilityEntityId].modifyPm(mult*value)
                                executed = True
                        elif (ability["feature"] == "paStock"):
                            self._playersDict[playerId].modifyPaStock(mult*value)
                            executed = True

                    # TODO : Awfull and not coherent behavior
                    elif (ability["behavior"] == "opAffected"):
                        multIdList = list(abilityTargetIdList)
                        for eid in multIdList:
                            for entityType in self._entitiesDict[eid].typeList:
                                if (entityType in ["mechanism"]):
                                    multIdList.remove(eid)
                                    break
                        mult = len(multIdList) if not(force) else mult # Handle the stopTrigger case
                        if (ability["feature"] == "gauges"):
                            if isinstance(value, dict):
                                for gaugeType in list(value.keys()):
                                    self._playersDict[playerId].modifyGauge(gaugeType, mult*value[gaugeType])
                                    executed = True
                            else:
                                raise GameException("Ability value for gauges must be a dict !")
                        elif (ability["feature"] == "paStock"):
                            self._playersDict[playerId].modifyPaStock(mult*value)
                            executed = True

                    elif (ability["behavior"] == "distance+addAuraWeak"):
                        mult = calcDist(self._entitiesDict[selfId].x, self._entitiesDict[selfId].y, self._entitiesDict[abilityTargetIdList[0]].x, self._entitiesDict[abilityTargetIdList[0]].y, offset=-1) if not(force) else mult # Handle the stopTrigger case
                        self._entitiesDict[selfId].addAuraBuffer(ability["feature"], mult*value, "WEAK")
                        executed = True

                    elif (ability["behavior"] == "myTargetAdjacentNocturiens"): # TODO : Generalise this behavior to all types
                        mult = 0
                        for abilityEntityId in abilityTargetIdList:
                            for eid in self.entityIdAdjacentToTile(self._entitiesDict[abilityEntityId].x, self._entitiesDict[abilityEntityId].y, self._entitiesDict[refId].team):
                                if ("nocturien" in self._entitiesDict[eid].typeList):
                                    mult += 1
                            pvVar = self._entitiesDict[abilityEntityId].modifyPv(mult*value)

                    elif (ability["behavior"] == "addAuraWeak"):
                        for abilityEntityId in abilityTargetIdList:
                            self._entitiesDict[abilityEntityId].addAuraBuffer(ability["feature"], value, "WEAK")
                            executed = True
                    
                    elif (ability["behavior"] == "addAuraStrong"):
                        for abilityEntityId in abilityTargetIdList:
                            self._entitiesDict[abilityEntityId].addAuraBuffer(ability["feature"], value, "STRONG")
                            executed = True

                    elif (ability["behavior"] == "addAuraReset"):
                        for abilityEntityId in abilityTargetIdList:
                            self._entitiesDict[abilityEntityId].addAuraBuffer(ability["feature"], value, "RESET")
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
                        passiveTriggerList.append({"action" : "charge", "trigger" : trigger, "actorId" : selfId})
                        passiveTriggerList.append({"action" : "deplace", "trigger" : trigger, "actorId" : selfId})

                    elif (ability["behavior"] == "pull"):
                        for abilityEntityId in abilityTargetIdList:
                            if (self._entitiesDict[selfId].x == self._entitiesDict[abilityEntityId].x):
                                if (self._entitiesDict[selfId].y < self._entitiesDict[abilityEntityId].y):
                                    self._entitiesDict[abilityEntityId].tp(self._entitiesDict[selfId].x, self._entitiesDict[selfId].y + 1)
                                    executed = True
                                elif (self._entitiesDict[selfId].y > self._entitiesDict[abilityEntityId].y):
                                    self._entitiesDict[abilityEntityId].tp(self._entitiesDict[selfId].x, self._entitiesDict[selfId].y - 1)
                                    executed = True
                                else:
                                    raise GameException("Target can't be on the same tile than selfEntity !")
                            elif (self._entitiesDict[selfId].y == self._entitiesDict[abilityEntityId].y):
                                if (self._entitiesDict[selfId].x < self._entitiesDict[abilityEntityId].x):
                                    self._entitiesDict[abilityEntityId].tp(self._entitiesDict[selfId].x + 1, self._entitiesDict[selfId].y)
                                    executed = True
                                elif (self._entitiesDict[selfId].x > self._entitiesDict[abilityEntityId].x):
                                    self._entitiesDict[abilityEntityId].tp(self._entitiesDict[selfId].x - 1, self._entitiesDict[selfId].y)
                                    executed = True
                                else:
                                    raise GameException("Target can't be on the same tile than selfEntity !")
                            else:
                                raise GameException("Target not aligned with selfEntity !")
                            passiveTriggerList.append({"action" : "deplace", "trigger" : trigger, "actorId" : abilityEntityId})

                    elif (ability["behavior"] == "push"):
                        for abilityEntityId in abilityTargetIdList:
                            self.pushEntity(abilityEntityId, self._entitiesDict[targetEntityIdList[1]].x, self._entitiesDict[targetEntityIdList[1]].y, value)
                            passiveTriggerList.append({"action" : "deplace", "trigger" : trigger, "actorId" : abilityEntityId})
                            executed = True

                    elif (ability["behavior"] == "pushBack"):
                        for abilityEntityId in abilityTargetIdList:
                            self.pushEntity(abilityEntityId, self._entitiesDict[targetEntityIdList[0]].x, self._entitiesDict[targetEntityIdList[0]].y, -value)
                            passiveTriggerList.append({"action" : "deplace", "trigger" : trigger, "actorId" : abilityEntityId})
                            executed = True

                    elif (ability["behavior"] == "pushAwayFromSelf"):
                        for abilityEntityId in abilityTargetIdList:
                            self.pushEntity(abilityEntityId, self._entitiesDict[selfId].x, self._entitiesDict[selfId].y, -value)
                            passiveTriggerList.append({"action" : "deplace", "trigger" : trigger, "actorId" : abilityEntityId})
                            executed = True

                    elif (ability["behavior"] == "bounce"):
                        affectableIdList = abilityTargetIdList
                        for eid in affectableIdList:
                            for entityType in self._entitiesDict[eid].typeList:
                                if (entityType in ["mechanism"]):
                                    affectableIdList.remove(eid)
                                    break
                        for abilityEntityId in affectableIdList:
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
                            executed = True

                    elif (ability["behavior"] == "removeState"):
                        if (":" in ability["feature"]):
                            stateFeature = ability["feature"].split(':')[0]
                        else:
                            stateFeature = ability["feature"]
                        for abilityEntityId in abilityTargetIdList:
                            self._entitiesDict[abilityEntityId].removeState(stateFeature)

                    elif (ability["behavior"] == "summon"):
                        if ("unique" in db.entities[ability["feature"]]["typeList"]):
                            eid = self.entityIdFromDescId(ability["feature"], self._playersDict[playerId].team)
                            if (eid != None):
                                self.removeEntity(eid)
                        entityId = self.appendEntity(playerId, ability["feature"], self._playersDict[playerId].team, self._entitiesDict[targetEntityIdList[targetDict["targetIdx"]]].x, self._entitiesDict[targetEntityIdList[targetDict["targetIdx"]]].y)
                        self._entitiesDict[entityId].startTurn()
                        self.executeAbilities(self._entitiesDict[entityId].abilities, "spawn", playerId, entityId, [None])
                        self.executeAbilities(self._entitiesDict[self._playersDict[playerId].heroEntityId].abilities, "summon", playerId, self._playersDict[playerId].heroEntityId, [entityId])
                        executed = True

                    elif (ability["behavior"] == "transform"):
                        x = self._entitiesDict[targetEntityIdList[targetDict["targetIdx"]]].x
                        y = self._entitiesDict[targetEntityIdList[targetDict["targetIdx"]]].y
                        self.removeEntity(abilityTargetIdList[targetDict["targetIdx"]])
                        if ("unique" in db.entities[ability["feature"]]["typeList"]):
                            eid = self.entityIdFromDescId(ability["feature"], self._playersDict[playerId].team)
                            if (eid != None):
                                self.removeEntity(eid)
                        entityId = self.appendEntity(playerId, ability["feature"], self._playersDict[playerId].team, x, y)
                        self._entitiesDict[entityId].startTurn()
                        self.executeAbilities(self._entitiesDict[entityId].abilities, "spawn", playerId, entityId, [None])
                        self.executeAbilities(self._entitiesDict[self._playersDict[playerId].heroEntityId].abilities, "summon", playerId, self._playersDict[playerId].heroEntityId, [entityId])
                        executed = True

                    elif (ability["behavior"] == "attackAgain"):
                        for abilityEntityId in abilityTargetIdList:
                            self._entitiesDict[abilityEntityId].attackAgain()
                            executed = True

                    elif (ability["behavior"] == "freeAura"):
                        self._entitiesDict[selfId].freeAura()
                        executed = True

                    elif (ability["behavior"] == "draw"):
                        self._playersDict[abilityTargetIdList[targetDict["targetIdx"]]].draw(value, ability["feature"])
                        executed = True

                    elif (ability["behavior"] == "generateSpell"):
                        self._playersDict[abilityTargetIdList[targetDict["targetIdx"]]].getSpell(ability["feature"], value)
                        executed = True

                    elif (ability["behavior"] == "sendBack"):
                        for abilityEntityId in abilityTargetIdList:
                            self.removeEntity(abilityEntityId, sendBack=True)
                            executed = True

                    elif (ability["behavior"] == "kill"):
                        for abilityEntityId in abilityTargetIdList:
                            self.removeEntity(abilityEntityId)
                            executed = True

                    elif (ability["behavior"] == "executeAbilities"):
                        # WARNING : force mult is used, this is wrong but mult is never used in this case (I hope ...)
                        for abilityEntityId in abilityTargetIdList:
                            self.executeAbilities(self._entitiesDict[abilityEntityId].abilities, "", self.getPlayerIdFromTeam(self._entitiesDict[abilityEntityId].team), abilityEntityId, [None], force=True)

                    # If stopTriggerList is defined, the ability must be added to the ongoingAbilityList
                    if stopTriggerList and not(force):
                        ongoingAbilityDict = {}
                        copiedAbility = copy.deepcopy(ability)
                        copiedAbility["mult"]                   = mult
                        ongoingAbilityDict["ability"]           = copiedAbility
                        ongoingAbilityDict["value"]             = value
                        ongoingAbilityDict["playerId"]          = playerId
                        ongoingAbilityDict["selfId"]            = selfId
                        ongoingAbilityDict["spellId"]           = spellId
                        ongoingAbilityDict["affectedIdList"]    = affectedIdList
                        ongoingAbilityDict["stopTriggerList"]   = stopTriggerList
                        self._ongoingAbilityList.append(ongoingAbilityDict)

                # Check if an aura has been used / aura must be specified only once by aura ability
                if (executed and ability["behavior"] == "aura"):
                    auraUsed = True

                # Adding default to passiveTriggerList
                for passiveTrigger in passiveTriggerList:
                    if (not "action" in passiveTrigger):
                        passiveTrigger["action"] = "none"
                    if (not "trigger" in passiveTrigger):
                        passiveTrigger["trigger"] = trigger
                    if (not "actorId" in passiveTrigger):
                        passiveTrigger["actorId"] = "self"
                    if (not "value" in passiveTrigger):
                        passiveTrigger["value"] = 0
                
                if (trigger != "ability"):
                    for entityId in self._entitiesDict:
                        if (type(self._entitiesDict[entityId]).__name__ == "Entity"):
                            self.executeAbilities(self._entitiesDict[entityId].abilities, "ability", self.getPlayerIdFromTeam(self._entitiesDict[entityId].team), entityId, targetEntityIdList, triggingAbility=ability, passiveTriggedList=passiveTriggerList)

        if auraUsed:
            self._entitiesDict[selfId].consumeAura(1)

        for eid in elemStateToRemoveEntityIdList:
            self._entitiesDict[eid].setElemState("")

    def removeOngoingAbilities(self, stopTrigger, playerId=None, selfId=None):
        copyOngoingAbilityList = list(self._ongoingAbilityList)
        for ongoingAbility in copyOngoingAbilityList:
            if (stopTrigger in ongoingAbility["stopTriggerList"] and (not(stopTrigger in ["startTurn", "endTurn"]) or playerId == ongoingAbility["playerId"])):
                if (ongoingAbility["ability"]["feature"] == "bodyguard" and selfId == ongoingAbility["selfId"]):
                    for state in self._entitiesDict[ongoingAbility["selfId"]].states:
                        if (state["feature"] == "bodyguard"):
                            bodyguardedId = state["value"]
                            break
                    self._entitiesDict[ongoingAbility["selfId"]].removeState("bodyguard")
                    self._entitiesDict[bodyguardedId].removeState("bodyguarded")
                    self._ongoingAbilityList.remove(ongoingAbility)
                else:
                    if (ongoingAbility["selfId"] in list(self._entitiesDict.keys())):
                        if (ongoingAbility["spellId"] == None or ongoingAbility["spellId"] in list(self._playersDict[ongoingAbility["playerId"]].handSpellDict.keys())):
                            if (ongoingAbility["ability"]["behavior"] == "addState"):
                                ongoingAbility["ability"]["behavior"] = "removeState"
                            ongoingAbility["ability"]["value"] = -ongoingAbility["value"]
                            self.executeAbilities([ongoingAbility["ability"]], "", ongoingAbility["playerId"], ongoingAbility["selfId"], ongoingAbility["affectedIdList"], spellId=ongoingAbility["spellId"], inAffectedIdList=ongoingAbility["affectedIdList"], force=True)
                            self._ongoingAbilityList.remove(ongoingAbility)
            elif (stopTrigger == "always" and "noArmor" in ongoingAbility["stopTriggerList"]):
                if (self._entitiesDict[self._playersDict[ongoingAbility["playerId"]].heroEntityId].armor == 0):
                    if (ongoingAbility["ability"]["behavior"] == "addState"):
                        ongoingAbility["ability"]["behavior"] = "removeState"
                    ongoingAbility["ability"]["value"] = -ongoingAbility["value"]
                    self.executeAbilities([ongoingAbility["ability"]], "", ongoingAbility["playerId"], ongoingAbility["selfId"], ongoingAbility["affectedIdList"], spellId=ongoingAbility["spellId"], force=True)
                    self._ongoingAbilityList.remove(ongoingAbility)