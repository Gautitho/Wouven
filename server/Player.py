import copy
import random
from functions import *
from Database import *

class Player:

    def __init__(self, deck, team, pseudo, heroEntityId):
        self.checkDeck(deck)
        self._heroDescId            = deck["heroDescId"]
        self._race                  = db.heroes[self._heroDescId]["race"]
        self._team                  = team
        self._pseudo                = pseudo
        self._pa                    = 6
        self._paStock               = 0
        self._gauges                = {"fire" : 0, "water" : 0, "earth" : 0, "air" : 0, "neutral" : 0}
        self._handSpellDescIds      = []
        self._deckSpellDescIds      = random.sample(deck["spells"], len(deck["spells"]))
        self._handCompanionDescIds  = deck["companions"]
        self._boardEntityIds        = []
        self._boardEntityIds.append(heroEntityId)
        self._heroEntityId          = heroEntityId

    def checkDeck(self, deck):
        # TODO: Check if deck is valid (spells from the good weapon, existing hero and companions, hero spell here, ...)
        if (len(deck["spells"]) != 9):
            exitOnError("You have to choose 9 spells !")
        if (len(deck["companions"]) != 4):
            exitOnError("You have to choose 4 companions !")

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
    def handCompanionDescIds(self):
        return list(self._handCompanionDescIds)

    @property
    def boardEntityIds(self):
        return list(self._boardEntityIds)

    @property
    def heroEntityId(self):
        return self._heroEntityId

    def modifyPaStock(self, value):
        self._paStock += value

    def draw(self):
        errorMsg = ""
        if (len(self._handSpellDescIds) < HAND_SPELLS):
            self._handSpellDescIds.append(self._deckSpellDescIds.pop(0))            

        return errorMsg

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
        printInfo(f"handCompanionDescIds    = {self._handCompanionDescIds}", printType)
        printInfo(f"boardEntityIds          = {self._boardEntityIds}", printType)
        printInfo(f"heroEntityId            = {self._heroEntityId}", printType)

    def getMyStatusDict(self):
        dic = {}
        dic["heroDescId"]           = self._heroDescId
        dic["team"]                 = self._team
        dic["pseudo"]               = self._pseudo
        dic["pa"]                   = self._pa
        dic["paStock"]              = self._paStock
        dic["gauges"]               = self._gauges
        dic["handSpellDescIds"]     = self._handSpellDescIds
        dic["handCompanionDescIds"] = self._handCompanionDescIds
        dic["boardEntityIds"]       = self._boardEntityIds
        dic["heroEntityId"]         = self._heroEntityId
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