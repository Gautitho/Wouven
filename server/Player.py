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
        self._handSpellDescIdList       = []
        if TEST_ENABLE:
            random.seed(0) #ONLY FOR DEBUG
        self._deckSpellDescIdList       = random.sample(deck["spellDescIdList"], len(deck["spellDescIdList"]))
        self._companionList             = []
        for companionDescId in deck["companionDescIdList"]:
            self._companionList.append({"descId" : companionDescId, "state" : "available", "entityId" : None})
        self._playedCompanionDescIds    = []
        self._boardEntityIds            = []
        self._heroEntityId              = None

    def checkDeck(self, deck):
        if not(deck["heroDescId"] in db.heroes):
            raise GameException(f"The hero ({deck['heroDescId']}) you picked does not exist !")
        if (len(deck["spellDescIdList"]) != 9):
            raise GameException("You have to choose 9 spells !")
        if (len(deck["companionDescIdList"]) != 4):
            raise GameException("You have to choose 4 companions !")
        heroSpellFound = False
        for spellDescId in deck["spellDescIdList"]:
            if not(spellDescId in db.spells):
                raise GameException(f"The spell ({spellDescId}) you picked does not exist !")
            elif (deck["spellDescIdList"].count(spellDescId) > 1):
                raise GameException(f"You can't pick a spell ({spellDescId}) more than 1 time !")
            else:
                if (db.spells[spellDescId]["race"] == deck["heroDescId"]):
                    heroSpellFound = True
                elif (db.spells[spellDescId]["race"] != db.heroes[deck["heroDescId"]]["race"]):
                    raise GameException(f"You have picked a spell ({spellDescId}) with the wrong race !")
        if not(heroSpellFound):
            raise GameException("You haven't picked a your hero spell !")
        for companionDescId in deck["companionDescIdList"]:
            if not(companionDescId in db.companions):
                raise GameException(f"The companion ({companionDescId}) you picked does not exist !")
            elif (deck["companionDescIdList"].count(companionDescId) > 1):
                raise GameException(f"You can't pick a companion ({companionDescId}) more than 1 time !") 

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
    def handSpellDescIdList(self):
        return list(self._handSpellDescIdList)

    @property
    def deckSpellDescIdList(self):
        return list(self._deckSpellDescIdList)

    @property
    def companionList(self):
        return list(self._companionList)

    @property
    def boardEntityIds(self):
        return list(self._boardEntityIds)

    @property
    def heroEntityId(self):
        return self._heroEntityId

    def setHeroEntityId(self, heroEntityId):
        self._heroEntityId = heroEntityId

    def summonCompanion(self, companionId, entityId):
        self._companionList[companionId]["state"]      = "alive"
        self._companionList[companionId]["entityId"]   = entityId
        if (db.companions[self._companionList[companionId]["descId"]]["spellDescId"]):
            if (len(self._handSpellDescIdList) < HAND_SPELLS):
                self._handSpellDescIdList.append(db.companionList[self._companionList[companionId]["descId"]]["spellDescId"])
            else:
                self._deckSpellDescIdList.append(db.companionList[self._companionList[companionId]["descId"]]["spellDescId"])

    def removeCompanion(self, companionId):
        self._companionList[companionId]["state"]      = "dead"
        self._companionList[companionId]["entityId"]   = None
        if (db.companionList[self._companionList[companionId]["descId"]]["spellDescId"]):
            if (db.companionList[self._companionList[companionId]["descId"]]["spellDescId"] in self._handSpellDescIdList):
                self._handSpellDescIdList.remove(db.companionList[self._companionList[companionId]["descId"]]["spellDescId"])
            if (db.companionList[self._companionList[companionId]["descId"]]["spellDescId"] in self._deckSpellDescIdList):
                self._deckSpellDescIdList.remove(db.companionList[self._companionList[companionId]["descId"]]["spellDescId"])

    def storeCompanion(self, companionId):
        self._companionList[companionId]["state"]      = "available"
        self._companionList[companionId]["entityId"]   = None

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
        if (len(self._handSpellDescIdList) < HAND_SPELLS):
            self._handSpellDescIdList.append(self._deckSpellDescIdList.pop(0))

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
        self._deckSpellDescIdList.append(self._handSpellDescIdList.pop(spellId))
        self._pa -= pa

    def addEntity(self, entityId):
        self._boardEntityIds.append(entityId)

    def removeEntity(self, entityId):
        self._boardEntityIds.remove(entityId)
        for companionId in range(0, len(self._companionList)):
            if (self._companionList[companionId]["entityId"] == entityId):
                self.removeCompanion(companionId)

    def display(self, printType="DEBUG"):
        printInfo(f"heroDescId              = {self._heroDescId}", printType)
        printInfo(f"race                    = {self._race}", printType)
        printInfo(f"team                    = {self._team}", printType)
        printInfo(f"pseudo                  = {self._pseudo}", printType)
        printInfo(f"pa                      = {self._pa}", printType)
        printInfo(f"paStock                 = {self._paStock}", printType)
        printInfo(f"gauges                  = {self._gauges}", printType)
        printInfo(f"handSpellDescIdList     = {self._handSpellDescIdList}", printType)
        printInfo(f"deckSpellDescIdList     = {self._deckSpellDescIdList}", printType)
        printInfo(f"companionList           = {self._companionList}", printType)
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
        dic["handSpellDescIdList"]      = self._handSpellDescIdList
        dic["companionList"]            = self._companionList
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