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
                                    self.executeAbilities(self._entities[entityId].abilities, "attack", playerId, entityId, attackedEntityId, {}, None)
                                    self.executeAbilities(self._entities[attackedEntityId].abilities, "attacked", playerId, attackedEntityId, None, {}, None)
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
                                        self.executeAbilities(self._entities[entityId].abilities, "attack", playerId, entityId, attackedEntityId, {}, None)
                                        self.executeAbilities(self._entities[attackedEntityId].abilities, "attacked", playerId, attackedEntityId, None, {}, None)
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
                            if (targetEntityId != None):
                               self.executeAbilities(spell["abilities"], "spellCast", playerId, None, targetEntityId, {}, spell["elem"])
                               for entityId in range(0, len(self._entities)):
                                   self.executeAbilities(self._entities[entityId].abilities, "spellCast", playerId, entityId, None, {}, spell["elem"])
                            else:
                               raise GameException("No entity on this tile !")

                        elif (spell["allowedTargetList"][0] == "emptyTile"):
                            pass

                        elif (spell["allowedTargetList"][0] == "myEntity"):
                            pass

                        elif (spell["allowedTargetList"][0] == "opEntity"):
                            pass

                        elif (spell["allowedTargetList"][0] == "myPlayer"):
                            targetEntityId = self.entityIdOnTile(targetPositionList[0]["x"], targetPositionList[0]["y"])
                            if (targetEntityId == self._players[playerId].heroEntityId):
                                self.executeAbilities(spell["abilities"], "spellCast", playerId, None, targetEntityId, {}, spell["elem"])
                                for entityId in range(0, len(self._entities)):
                                    self.executeAbilities(self._entities[entityId].abilities, "spellCast", playerId, entityId, None, {}, spell["elem"])
                            else:
                                raise GameException("Wrong spell target !")

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

    def executeAbilities(self, abilityList, trigger, playerId, selfEntityId, targetEntityId, position, spellElem):
        auraUsed    = False
        opPlayerId  = self.getOpPlayerId(playerId)
        for ability in abilityList:
            if (trigger == ability["trigger"]):
                # Check condition
                for condition in ability["conditionList"]:
                    if (condition["feature"] == "elemState"):
                        if (condition["value"] in ["oiled", "wet", "muddy", "windy"]):
                            if (self._entities[targetEntityId].elemState == condition["value"]):
                                self._entities[targetEntityId].setElemState("")
                            else:
                                return None # Condition not verified
                        else:
                            raise GameException("ElemState to consume does not exist !")

                    elif (condition["feature"] == "elem"):
                        if (condition["value"] in ["fire", "water", "earth", "air", "neutral"]):
                            if (spellElem == condition["value"]):
                                pass
                            else:
                                return None # Condition not verified
                        else:
                            raise GameException("Elem of the spell does not exist !")

                    else:
                        raise GameException("Wrong ability condition !")

                # Choose entity
                if (ability["target"] == "target"):
                    abilityEntityId = targetEntityId
                elif (ability["target"] == "self"):
                    abilityEntityId = selfEntityId
                elif (ability["target"] == "myPlayer"):
                    abilityEntityId = self._players[playerId].heroEntityId
                elif (ability["target"] == "opPlayer"):
                    abilityEntityId = self._players[opPlayerId].heroEntityId
                else:
                    raise GameException("Wrong ability target !")
                   
                # Execute ability
                executed = False
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
                    if (ability["behavior"] == "melee"):
                        mult = len(self.entityIdAroundTile(self._entities[self._players[playerId].heroEntityId].x, self._entities[self._players[playerId].heroEntityId].y, self.getOpTeam(playerId)))
                        self._entities[self._players[playerId].heroEntityId].modifyAtk(mult*ability["value"])
                        executed = True
                    else:
                        self._entities[self._players[playerId].heroEntityId].modifyAtk(ability["value"])
                        executed = True
                # TODO : Improve this behavior
                elif (ability["behavior"] == "addAura"):
                    if (self._entities[self._players[playerId].heroEntityId].aura and ability["feature"] == self._entities[self._players[playerId].heroEntityId].aura["type"]):
                        self._entities[self._players[playerId].heroEntityId].addAura(ability["value"])
                        executed = True
                    else:
                        self._entities[self._players[playerId].heroEntityId].newAura(ability["feature"], ability["value"])
                        executed = True

                # Check aura
                if (executed and ability["behavior"] == "aura"):
                    auraUsed = True

        if auraUsed:
            self._entities[selfEntityId].modifyAuraNb(-1)