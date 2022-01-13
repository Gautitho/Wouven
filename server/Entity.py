import copy
from functions import *
from Database import *
from GameException import *

class Entity:

    def __init__(self, descId, team, x, y):
        self._descId        = descId
        self._name          = db.entities[descId]["name"]
        self._team          = team
        self._x             = x
        self._y             = y
        self._pv            = db.entities[descId]["pv"]
        self._maxPv         = db.entities[descId]["pv"]
        self._armor         = db.entities[descId]["armor"]
        self._atk           = db.entities[descId]["atk"]
        self._pm            = db.entities[descId]["pm"]
        self._typeList      = [] if not("typeList" in db.entities[descId]) else copy.deepcopy(db.entities[descId]["typeList"])
        self._elemState     = ""
        self._aura          = {"type" : "null", "nb" : 0} if db.entities[descId]["aura"] == {} else copy.deepcopy(db.entities[descId]["aura"])
        self._states        = copy.deepcopy(db.entities[descId]["states"])
        self._abilities     = copy.deepcopy(db.entities[descId]["abilities"])

        self._canMove               = True
        self._canAttack             = True
        self._storedCanMove         = True
        self._storedCanAttack       = True
        self._oneByTurnAbilityList  = []

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
    def name(self):
        return self._name

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
    def maxPv(self):
        return self._maxPv

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
    def types(self):
        return list(self._typeList)

    @property
    def elemState(self):
        return self._elemState

    @property
    def aura(self):
        return dict(self._aura)

    @property
    def states(self):
        return list(self._states)

    @property
    def oneByTurnAbilityList(self):
        return list(self._oneByTurnAbilityList)

    @property
    def abilities(self):
        if (self._aura["type"] != "null"):
            outList = list(self._abilities)
            outList.extend(list(db.auras[self._aura["type"]]["abilities"]))
            return outList
        else:
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
        printInfo(f"maxPv       = {self._maxPv}", printType)
        printInfo(f"armor       = {self._armor}", printType)
        printInfo(f"atk         = {self._atk}", printType)
        printInfo(f"pm          = {self._pm}", printType)
        printInfo(f"typeList    = {self._typeList}", printType)
        printInfo(f"elemState   = {self._elemState}", printType)
        printInfo(f"aura        = {self._aura}", printType)
        printInfo(f"states      = {self._states}", printType)
        printInfo(f"abilities   = {self._abilities}", printType)
        printInfo(f"canMove     = {self._canMove}", printType)
        printInfo(f"canAttack   = {self._canAttack}", printType)

    def getStatusDict(self):
        dic = {}
        dic["descId"]           = self._descId
        dic["spritePath"]       = db.entities[self._descId]["spritePath"]
        dic["descSpritePath"]   = db.entities[self._descId]["descSpritePath"]
        dic["team"]             = self._team
        dic["x"]                = self._x
        dic["y"]                = self._y
        dic["pv"]               = self._pv
        dic["maxPv"]            = self._maxPv
        dic["armor"]            = self._armor
        dic["atk"]              = self._atk
        dic["pm"]               = self._pm
        dic["typeList"]         = self._typeList
        dic["elemState"]        = self._elemState
        dic["aura"]             = self._aura
        dic["states"]           = self._states
        dic["abilities"]        = self._abilities
        dic["canMove"]          = self._canMove
        dic["canAttack"]        = self._canAttack
        return dic

    def startTurn(self):
        self._pm                = db.entities[self._descId]["pm"]
        self._canMove           = True
        self._canAttack         = True
        self._storedCanMove     = True
        self._storedCanAttack   = True
        self.applyStates()

    def endTurn(self):
        self._oneByTurnAbilityList = []
        if (self.isInStates("disarmed")):
            self.removeState("disarmed")
        if (self.isInStates("locked")):
            self.removeState("locked")
        if (self.isInStates("frozen")):
            self.removeState("frozen")
        if (self.isInStates("petrified")):
            self.removeState("petrified")
        if (self.isInStates("stunned")):
            self.removeState("stunned")

    def move(self, x, y):
        self._x         = x
        self._y         = y
        self._canMove   = False
        self._canAttack = False

    def tp(self, x, y):
        self._x = x
        self._y = y

    def modifyPm(self, value):
        self._pm = max(self._pm + value, 0)

    def modifyAtk(self, value):
        self._atk = max(self._atk + value, 0)

    def modifyArmor(self, value):
        self._armor = max(self._armor + value, 0)

    def applyStates(self):
        self._storedCanMove     = self._canMove
        self._storedCanAttack   = self._canAttack
        if (self.isInStates("disarmed")):
            self._canAttack = False
        if (self.isInStates("locked")):
            self._canMove = False
        if (self.isInStates("petrified")):
            self._canAttack = False
            self._canMove = False
        if (self.isInStates("stunned")):
            self._canAttack = False
            self._canMove = False

    def addState(self, state):
        cpyState        = dict(state)
        uniqueStateList = ["disarmed", "locked", "frozen", "stunned"]
        if not(cpyState in self._states):
            for presentState in self._states:
                if (cpyState["feature"] in uniqueStateList):
                    if (presentState["feature"] in uniqueStateList):
                        self.removeState(presentState["feature"])
            self._states.append(cpyState)
            self.applyStates()

    def removeState(self, stateFeature):
        stateFound = False
        for state in self._states:
            if (state["feature"] == stateFeature):
                self._states.remove(state)
                self._canAttack = self._storedCanAttack
                self._canMove = self._storedCanMove
                stateFound = True
                break
        if not(stateFound):
            raise GameException(f"This state {state} is not applied, it can't be removed !")

    def modifyPv(self, value):
        removedPv = 0
        if (value < 0):
            apply = True
            if (self.isInStates("shield")):
                self.removeState("shield")
                apply = False
            if (self.isInStates("petrified")):
                apply = False

            if apply:
                if (self.isInStates("stunned")):
                    self.removeState("stunned")
                if (self._armor + value > 0):
                    self._armor += value
                else:
                    self._pv    += self._armor + value
                    self._armor = 0
                    removedPv = self._armor + value
        else:
            if (self._pv + value > db.entities[self._descId]["pv"]):
                self._pv = db.entities[self._descId]["pv"]
            else:
                self._pv += value

        return removedPv

    def newAura(self, type, nb):
        self._aura["type"]  = type
        self._aura["nb"]    = min(nb, 5)

    def attackAgain(self):
        self._canMove   = True
        self._canAttack = True

    def modifyAuraNb(self, nb):
        if (self._aura["nb"] + nb > 0):
            self._aura["nb"] = min(self._aura["nb"] + nb, 5)
        elif (self._aura["nb"] + nb == 0):
            self._aura = {"type" : "null", "nb" : 0}
        else:
            raise GameException(f"You have not aura anymore !")

    def modifyAuraType(self, auraType):
        if (self._aura):
            self._aura["type"] = auraType
        else:
            raise GameException(f"You have not aura anymore !")

    def freeAura(self):
        self._aura = {"type" : "null", "nb" : 0}

    def setElemState(self, value):
        if value in ["", "oiled", "muddy", "windy", "wet"]:
            self._elemState = value
        else:
            raise GameException(f"ElemState {value} to apply is not supported !")

    def isInStates(self, stateFeature):
        for state in self._states:
            if (state["feature"] == stateFeature):
                return True
        return False

    def appendOneByTurnAbility(self, ability):
        self._oneByTurnAbilityList.append(ability)