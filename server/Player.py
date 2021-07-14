import copy
import random
from functions import *
from Database import *
from GameException import *

class Player:

    def __init__(self, deck, team, pseudo):
        self.checkDeck(deck)
        self._heroDescId                = deck["heroDescId"]
        self._race                      = db.heroes[self._heroDescId]["race"]
        self._team                      = team
        self._pseudo                    = pseudo
        self._pa                        = 6
        self._paStock                   = 0
        self._gauges                    = {"fire" : 0, "water" : 0, "earth" : 0, "air" : 0, "neutral" : 0}
        self._handSpellDescIds          = []
        random.seed(0) #ONLY FOR DEBUG
        self._deckSpellDescIds          = random.sample(deck["spells"], len(deck["spells"]))
        self._companions                = []
        for companionDescId in deck["companions"]:
            self._companions.append({"descId" : companionDescId, "state" : "available", "entityId" : None})
        self._playedCompanionDescIds    = []
        self._boardEntityIds            = []
        self._heroEntityId              = None

    def checkDeck(self, deck):
        # TODO: Check if deck is valid (spells from the good weapon, existing hero and companions, hero spell here, ...)
        if (len(deck["spells"]) != 9):
            raise GameException("You have to choose 9 spells !")
        if (len(deck["companions"]) != 4):
            raise GameException("You have to choose 4 companions !")

    @property
    def heroDescId(self):
        return self._heroDescId

    @property
    def race(self):
        return self._race

    @property
    def team(self):
        return self._team

    @property
    def pseudo(self):
        return self._pseudo

    @property
    def pa(self):
        return self._pa

    @property
    def paStock(self):
        return self._paStock

    @property
    def gauges(self):
        return dict(self._gauges)

    @property
    def handSpellDescIds(self):
        return list(self._handSpellDescIds)

    @property
    def deckSpellDescIds(self):
        return list(self._deckSpellDescIds)

    @property
    def companions(self):
        return list(self._companions)

    @property
    def boardEntityIds(self):
        return list(self._boardEntityIds)

    @property
    def heroEntityId(self):
        return self._heroEntityId

    def setHeroEntityId(self, heroEntityId):
        self._heroEntityId = heroEntityId

    def summonCompanion(self, companionId, entityId):
        self._companions[companionId]["state"]      = "alive"
        self._companions[companionId]["entityId"]   = entityId
        if (db.companions[self._companions[companionId]["descId"]]["spellDescId"]):
            if (len(self._handSpellDescIds) < HAND_SPELLS):
                self._handSpellDescIds.append(db.companions[self._companions[companionId]["descId"]]["spellDescId"])
            else:
                self._deckSpellDescIds.append(db.companions[self._companions[companionId]["descId"]]["spellDescId"])

    def removeCompanion(self, companionId):
        self._companions[companionId]["state"]      = "dead"
        self._companions[companionId]["entityId"]   = None
        if (db.companions[self._companions[companionId]["descId"]]["spellDescId"]):
            if (db.companions[self._companions[companionId]["descId"]]["spellDescId"] in self._handSpellDescIds):
                self._handSpellDescIds.remove(db.companions[self._companions[companionId]["descId"]]["spellDescId"])
            if (db.companions[self._companions[companionId]["descId"]]["spellDescId"] in self._deckSpellDescIds):
                self._deckSpellDescIds.remove(db.companions[self._companions[companionId]["descId"]]["spellDescId"])

    def storeCompanion(self, companionId):
        self._companions[companionId]["state"]      = "available"
        self._companions[companionId]["entityId"]   = None

    def startTurn(self):
        self._pa = 6
     
    def endTurn(self):
        self.draw()

    def modifyPaStock(self, value):
        self._paStock = max(min(self._paStock + value, 9), 0)

    def useReserve(self):
        self._pa += self._paStock
        self._paStock = 0

    def draw(self):
        if (len(self._handSpellDescIds) < HAND_SPELLS):
            self._handSpellDescIds.append(self._deckSpellDescIds.pop(0))

    def modifyGauge(self, gaugeType, value):
        if (gaugeType in ["fire", "water", "earth", "air", "neutral"]):
            if (self._gauges[gaugeType] + value < 0):
                if (gaugeType != "neutral" and self._gauges[gaugeType] + self._gauges["neutral"] + value >= 0):
                    self._gauges["neutral"] = self._gauges["neutral"] + value + self._gauges[gaugeType]
                    self._gauges[gaugeType] = 0
                else:
                    raise GameException("Not enough " + gaugeType + " gauge !")
            else:
                self._gauges[gaugeType] = min(self._gauges[gaugeType] + value, 9)
        else:
            raise GameException("Wrong gauge type !")

    def playSpell(self, spellId, pa):
        self._deckSpellDescIds.append(self._handSpellDescIds.pop(spellId))
        self._pa -= pa

    def addEntity(self, entityId):
        self._boardEntityIds.append(entityId)

    def removeEntity(self, entityId):
        self._boardEntityIds.remove(entityId)
        for companionId in range(0, len(self._companions)):
            if (self._companions[companionId]["entityId"] == entityId):
                self.removeCompanion(companionId)

    def display(self, printType="DEBUG"):
        printInfo(f"heroDescId              = {self._heroDescId}", printType)
        printInfo(f"race                    = {self._race}", printType)
        printInfo(f"team                    = {self._team}", printType)
        printInfo(f"pseudo                  = {self._pseudo}", printType)
        printInfo(f"pa                      = {self._pa}", printType)
        printInfo(f"paStock                 = {self._paStock}", printType)
        printInfo(f"gauges                  = {self._gauges}", printType)
        printInfo(f"handSpellDescIds        = {self._handSpellDescIds}", printType)
        printInfo(f"deckSpellDescIds        = {self._deckSpellDescIds}", printType)
        printInfo(f"companions              = {self._companions}", printType)
        printInfo(f"playedCompanionDescIds  = {self._playedCompanionDescIds}", printType)
        printInfo(f"boardEntityIds          = {self._boardEntityIds}", printType)
        printInfo(f"heroEntityId            = {self._heroEntityId}", printType)

    def getMyStatusDict(self):
        dic = {}
        dic["heroDescId"]               = self._heroDescId
        dic["team"]                     = self._team
        dic["pseudo"]                   = self._pseudo
        dic["pa"]                       = self._pa
        dic["paStock"]                  = self._paStock
        dic["gauges"]                   = self._gauges
        dic["handSpellDescIds"]         = self._handSpellDescIds
        dic["companions"]               = self._companions
        dic["boardEntityIds"]           = self._boardEntityIds
        dic["heroEntityId"]             = self._heroEntityId
        return dic

    def getOpStatusDict(self):
        dic = {}
        dic["heroDescId"]           = self._heroDescId
        dic["team"]                 = self._team
        dic["pseudo"]               = self._pseudo
        dic["pa"]                   = self._pa
        dic["paStock"]              = self._paStock
        dic["gauges"]               = self._gauges
        dic["boardEntityIds"]       = self._boardEntityIds
        dic["heroEntityId"]         = self._heroEntityId
        return dic