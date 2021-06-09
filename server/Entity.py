from functions import *
from Database import *

class Entity:

    def __init__(self, descId, team, x, y):
        self._descId        = descId
        self._team          = team
        self._x             = x
        self._y             = y
        self._pv            = db.entities[descId]["pv"]
        self._armor         = db.entities[descId]["armor"]
        self._atk           = db.entities[descId]["atk"]
        self._pm            = db.entities[descId]["pm"]
        self._elemState     = ""
        self._aura          = db.entities[descId]["aura"]
        self._states        = db.entities[descId]["states"]
        self._abilities     = db.entities[descId]["abilities"]

        self._canMove       = True
        self._canAttack     = True

    def check(self, descId, team, x, y):
        checkCondition(True, descId in db.entities, f"Entity descId ({descId}) does not exist !")
        checkCondition(True, team in ["blue", "red"], f"Entity team ({team}) does not exist !")
        checkCondition(True, 0 <= x <= BOARD_COLS, f"Entity x position ({x}) is not valid !")
        checkCondition(True, 0 <= y <= BOARD_ROWS, f"Entity y position ({y}) is not valid !")
        checkCondition(True, descId["pv"] > 0, f"Entity pv ({descId['pv']}) is not valid !")
        checkCondition(True, descId["armor"] >= 0, f"Entity armor ({descId['armor']}) is not valid !")
        checkCondition(True, descId["atk"] >= 0, f"Entity atk ({descId['atk']}) is not valid !")
        checkCondition(True, descId["pm"] >= 0, f"Entity pm ({descId['pm']}) is not valid !")
        if descId["aura"]:
            checkCondition(True, "type" in descId["aura"], f"Entity aura has no 'type' key !")
            checkCondition(True, descId["aura"]["type"] in ["bloodySword"], f"Entity aura type ({descId['aura']['type']}) is not valid !")
            checkCondition(True, "nb" in descId["aura"], f"Entity aura has no 'nb' key !")
            checkCondition(True, 0 <= descId["aura"]["nb"] <= 5, f"Entity aura type ({descId['aura']['nb']}) is not valid !")
        if descId["states"]:
            for state in descId["states"]:
                checkCondition(True, state in ["shield"], f"Entity state ({state}) is not valid !")
        if descId["abilities"]:
            for ability in descId["abilities"]:
                checkCondition(True, "trigger" in ability, f"Entity ability ({ability}) has no 'trigger' key !")
                checkCondition(True, "target" in ability, f"Entity ability ({ability}) has no 'target' key !")
                checkCondition(True, "feature" in ability, f"Entity ability ({ability}) has no 'feature' key !")
                checkCondition(True, "value" in ability, f"Entity ability ({ability}) has no 'value' key !")
                checkCondition(True, "effect" in ability, f"Entity ability ({ability}) has no 'effect' key !")
                checkCondition(True, ability["trigger"] in ["turnStart", "turnEnd", "spawn", "death", "attack", "finish"], f"Entity ability trigger ({ability['trigger']}) is not valid !")
                checkCondition(True, ability["target"] in ["self", "myPlayer", "opPlayer", "target", "aligned"], f"Entity ability target ({ability['target']}) is not valid !")
                checkCondition(True, ability["feature"] in ["pv", "pa", "pm"], f"Entity ability feature ({ability['feature']}) is not valid !")
                checkCondition(True, type(ability["value"]) == int, f"Entity ability value ({ability['value']}) is not valid !")
                checkCondition(True, ability["effect"] in ["recover"], f"Entity ability effect ({ability['effect']}) is not valid !")


    @property
    def descId(self):
        return self._descId

    @property
    def team(self):
        return self._team

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    @property
    def pv(self):
        return self._pv

    @property
    def armor(self):
        return self._armor

    @property
    def atk(self):
        return self._atk

    @property
    def pm(self):
        return self._pm

    @property
    def elemState(self):
        return list(self._elemState)

    @property
    def aura(self):
        return list(self._aura)

    @property
    def states(self):
        return list(self._states)

    @property
    def abilities(self):
        return list(self._abilities)

    @property
    def canMove(self):
        return self._canMove

    @property
    def canAttack(self):
        return self._canAttack

    def display(self, printType="DEBUG"):
        printInfo(f"descId      = {self._descId}", printType)
        printInfo(f"team        = {self._team}", printType)
        printInfo(f"x           = {self._x}", printType)
        printInfo(f"y           = {self._y}", printType)
        printInfo(f"pv          = {self._pv}", printType)
        printInfo(f"armor       = {self._armor}", printType)
        printInfo(f"atk         = {self._atk}", printType)
        printInfo(f"pm          = {self._pm}", printType)
        printInfo(f"elemState   = {self._elemState}", printType)
        printInfo(f"aura        = {self._aura}", printType)
        printInfo(f"states      = {self._states}", printType)
        printInfo(f"abilities   = {self._abilities}", printType)
        printInfo(f"canMove     = {self._canMove}", printType)
        printInfo(f"canAttack   = {self._canAttack}", printType)

    def getStatusDict(self):
        dic = {}
        dic["descId"]       = self._descId
        dic["team"]         = self._team
        dic["x"]            = self._x
        dic["y"]            = self._y
        dic["pv"]           = self._pv
        dic["armor"]        = self._armor
        dic["atk"]          = self._atk
        dic["pm"]           = self._pm
        dic["elemState"]    = self._elemState
        dic["aura"]         = self._aura
        dic["states"]       = self._states
        dic["abilities"]    = self._abilities
        dic["canMove"]      = self._canMove
        dic["canAttack"]    = self._canAttack
        return dic

    def newTurn(self):
        self._pm            = db.entities[self._descId]["pm"]
        self._canMove       = True
        self._canAttack     = True

    def move2(self, board, path):
        errorMsg        = ""
        x               = self._x
        y               = self._y
        pm              = self._pm
        attackedEntity  = -1
        if (self._canMove):
            if (int(path[0]["x"]) == x and int(path[0]["y"]) == y): # The path is given with the inital position of the entity
                path.pop(0)
                for tile in path:
                    if (abs(x - int(tile["x"])) + abs(y - int(tile["y"])) == 1):
                        if (pm == 0):
                            if (self._canAttack and board.entityIdOnTile(int(tile["x"]), int(tile["y"])) != -1): # Attack after full pm move
                                attackedEntity  = board.entityIdOnTile(int(tile["x"]), int(tile["y"]))
                                pm              = -1                           
                            else:
                                errorMsg = "Path length is higher than your pm !"
                                break
                        else:
                            if (board.entityIdOnTile(int(tile["x"]), int(tile["y"])) == -1): # The next tile is empty
                                x             = int(tile["x"])
                                y             = int(tile["y"])
                                pm            -= 1
                            else: # There is an entity on next tile
                                if (self._canAttack):
                                    attackedEntity  = board.entityIdOnTile(int(tile["x"]), int(tile["y"]))
                                    pm              = -1
                                else:
                                    errorMsg = "You can't attack this turn !"
                                    break
                    else:
                        errorMsg = "Successive tiles must be contiguous in path or an entity is on your path !"
                        break
            else:
                errorMsg = "You can't move anymore this turn !"
        else:
            errorMsg = "First tile of the path must be the current entity position !"

        if (errorMsg == ""):
            self._x         = x
            self._y         = y
            self._pm        = 0
            self._canMove   = False
            self._canAttack = False
            if (attackedEntity != -1):
                board.modifyPv(attackedEntity, -self._atk)

        return errorMsg

    def move(self, x, y):
        self._x         = x
        self._y         = y
        self._pm        = 0
        self._canMove   = False
        self._canAttack = False

    def modifyPv(self, value):
        if (value < 0):
            if "shield" in self._states:
                self._states.remove("shield")
            else:
                if (self._armor + value > 0):
                    self._armor += value
                else:
                    self._armor = 0
                    self._pv    += self._armor + value
        else:
            if (self._pv + value > db.entities[self._descId]["pv"]):
                self._pv = db.entities[self._descId]["pv"]
            else:
                self._pv += value