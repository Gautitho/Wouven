import copy
from functions import *
from Database import *
from GameException import *

class Spell:

    def __init__(self, descId):
        self._descId                = descId
        self._name                  = db.spells[self._descId]["name"]
        self._race                  = db.spells[self._descId]["race"]
        self._cost                  = db.spells[self._descId]["cost"]
        self._elem                  = db.spells[self._descId]["elem"]
        self._spritePath            = db.spells[self._descId]["spritePath"]
        self._descSpritePath        = db.spells[self._descId]["descSpritePath"]
        self._allowedTargetList     = db.spells[self._descId]["allowedTargetList"]
        self._abilities             = db.spells[self._descId]["abilities"]
        self._costModifierList      = []

    @property
    def descId(self):
        return self._descId

    @property
    def name(self):
        return self._name

    @property
    def race(self):
        return self._race

    @property
    def cost(self):
        return self._cost

    @property
    def elem(self):
        return self._elem

    @property
    def spritePath(self):
        return self._spritePath

    @property
    def descSpritePath(self):
        return self._descSpritePath

    @property
    def allowedTargetList(self):
        return copy.deepcopy(self._allowedTargetList)

    @property
    def abilities(self):
        return copy.deepcopy(self._abilities)

    @property
    def costModifierList(self):
        return copy.deepcopy(self._costModifierList)

    def getDict(self):
        dic = {}
        dic["name"]                 = self.name
        dic["race"]                 = self.race
        dic["cost"]                 = self.cost
        dic["elem"]                 = self.elem
        dic["spritePath"]           = self.spritePath
        dic["descSpritePath"]       = self.descSpritePath
        dic["allowedTargetList"]    = self.allowedTargetList
        dic["abilities"]            = self.abilities
        return dic