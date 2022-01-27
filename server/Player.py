import copy
import random
from functions import *
from Database import *
from GameException import *
from Spell import *

class Player:

    def __init__(self, deck, team, pseudo):
        #self.checkDeck(deck)
        self._heroDescId                = deck["heroDescId"]
        self._race                      = db.heroes[self._heroDescId]["race"]
        self._team                      = team
        self._pseudo                    = pseudo
        self._pa                        = 6
        self._paStock                   = 0
        self._gauges                    = {"fire" : 0, "water" : 0, "earth" : 0, "air" : 0, "neutral" : 0}
        self._handSpellList             = []
        if TEST_ENABLE:
            random.seed(0) #ONLY FOR DEBUG
        self._deckSpellDescIdList       = random.sample(deck["spellDescIdList"], len(deck["spellDescIdList"]))
        self._companionList             = []
        for companionDescId in deck["companionDescIdList"]:
            self._companionList.append({"descId" : companionDescId, "state" : "available", "entityId" : None})
        self._playedCompanionDescIds    = []
        self._boardEntityIds            = []
        self._heroEntityId              = None
        self._spellsPlayedDuringTurn    = 0

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
    def handSpellList(self):
        return list(self._handSpellList)

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

    @property
    def spellsPlayedDuringTurn(self):
        return self._spellsPlayedDuringTurn

    def setHeroEntityId(self, heroEntityId):
        self._heroEntityId = heroEntityId

    def summonCompanion(self, companionId, entityId):
        self._companionList[companionId]["state"]      = "alive"
        self._companionList[companionId]["entityId"]   = entityId
        if (db.companions[self._companionList[companionId]["descId"]]["spellDescId"]):
            companionSpellDescId = db.companions[self._companionList[companionId]["descId"]]["spellDescId"]
            if (len(self._handSpellList) < HAND_SPELLS):
                self._handSpellList.append(Spell(companionSpellDescId))
            else:
                self._deckSpellDescIdList.append(companionSpellDescId)

    def removeCompanion(self, companionId):
        self._companionList[companionId]["state"]      = "dead"
        self._companionList[companionId]["entityId"]   = None
        if (db.companions[self._companionList[companionId]["descId"]]["spellDescId"]):
            companionSpellDescId = db.companions[self._companionList[companionId]["descId"]]["spellDescId"]
            for handSpellIdx in range(0, len(self._handSpellList)):
                if (self._handSpellList[handSpellIdx].descId == companionSpellDescId):
                    del self._handSpellList[handSpellIdx]
                    break
            if (companionSpellDescId in self._deckSpellDescIdList):
                self._deckSpellDescIdList.remove(companionSpellDescId)

    def storeCompanion(self, companionId):
        self._companionList[companionId]["state"]      = "available"
        self._companionList[companionId]["entityId"]   = None

    def startTurn(self):
        self._pa = 6
        self._spellsPlayedDuringTurn = 0
     
    def endTurn(self):
        self.draw(1)

    def modifyPaStock(self, value):
        self._paStock = max(min(self._paStock + value, 9), 0)

    def useReserve(self):
        self._pa += self._paStock
        self._paStock = 0

    def draw(self, nb, type=""):
        for i in range(nb):
            if (len(self._handSpellList) < HAND_SPELLS):
                for spellIdx in range(len(self._deckSpellDescIdList)):
                    if (type == ""):
                        spellDescId = self._deckSpellDescIdList.pop(spellIdx)
                        self._handSpellList.append(Spell(spellDescId))
                        break
                    else:
                        if ("typeList" in db.spells[self._deckSpellDescIdList[spellIdx]] and type in db.spells[self._deckSpellDescIdList[spellIdx]]["typeList"]):
                            spellDescId = self._deckSpellDescIdList.pop(spellIdx)
                            self._handSpellList.append(Spell(spellDescId))
                            break
            else:
                spellDescId = self._deckSpellDescIdList.pop(0)
                self._deckSpellDescIdList.append(spellDescId)

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

    def playSpell(self, spellId):
        spell = self._handSpellList.pop(spellId)
        self._deckSpellDescIdList.append(spell.descId)
        self._pa -= spell.cost
        self._spellsPlayedDuringTurn += 1

    def modifySpellCost(self, spellId, value):
        self._handSpellList[spellId].modifyCost(value)

    def addEntity(self, entityId):
        self._boardEntityIds.append(entityId)

    def removeEntity(self, entityId):
        self._boardEntityIds.remove(entityId)
        for companionId in range(0, len(self._companionList)):
            if (self._companionList[companionId]["entityId"] == entityId):
                self.removeCompanion(companionId)

    def toString(self):
        s = ""
        s += f"  heroDescId              = {self._heroDescId}\n"
        s += f"  race                    = {self._race}\n"
        s += f"  team                    = {self._team}\n"
        s += f"  pseudo                  = {self._pseudo}\n"
        s += f"  pa                      = {self._pa}\n"
        s += f"  paStock                 = {self._paStock}\n"
        s += f"  gauges                  = {self._gauges}\n"
        s += f"  handSpellList           = {[spell.getDict() for spell in self._handSpellList]}\n"
        s += f"  deckSpellDescIdList     = {self._deckSpellDescIdList}\n"
        s += f"  companionList           = {self._companionList}\n"
        s += f"  playedCompanionDescIds  = {self._playedCompanionDescIds}\n"
        s += f"  boardEntityIds          = {self._boardEntityIds}\n"
        s += f"  heroEntityId            = {self._heroEntityId}\n"
        return s

    def getMyStatusDict(self):
        dic = {}
        dic["team"]                 = self._team
        dic["pseudo"]               = self._pseudo
        dic["pa"]                   = self._pa
        dic["paStock"]              = self._paStock
        dic["gauges"]               = self._gauges
        dic["handSpellList"]        = [spell.getDict() for spell in self._handSpellList]
        dic["companionList"]        = [{"descSpritePath" : db.entities[db.companions[companion["descId"]]["entityDescId"]]["descSpritePath"], "state" : companion["state"]} for companion in self._companionList]
        dic["heroEntityId"]         = self._heroEntityId
        dic["boardEntityIds"]       = self._boardEntityIds
        return dic

    def getOpStatusDict(self):
        dic = {}
        dic["team"]                 = self._team
        dic["pseudo"]               = self._pseudo
        dic["pa"]                   = self._pa
        dic["paStock"]              = self._paStock
        dic["gauges"]               = self._gauges
        dic["heroEntityId"]         = self._heroEntityId
        dic["boardEntityIds"]       = self._boardEntityIds
        return dic