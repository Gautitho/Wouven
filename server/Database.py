import json

HEROES_FILE_PATH_LIST       = ["data/heroes/iop.json", "data/heroes/xelor.json", "data/heroes/cra.json", "data/heroes/sacrieur.json"]
COMPANIONS_FILE_PATH_LIST   = ["data/companions/air.json", "data/companions/water.json", "data/companions/fire.json", "data/companions/earth.json", "data/companions/multi.json"]
ENTITIES_FILE_PATH_LIST     = ["data/entities/air.json", "data/entities/water.json", "data/entities/fire.json", "data/entities/earth.json", "data/entities/iop.json", "data/entities/xelor.json", "data/entities/cra.json", "data/entities/sacrieur.json"]
SPELLS_FILE_PATH_LIST       = ["data/spells/air.json", "data/spells/water.json", "data/spells/fire.json", "data/spells/earth.json", "data/spells/iop.json", "data/spells/xelor.json", "data/spells/cra.json", "data/spells/sacrieur.json", "data/spells/misc.json"]
AURAS_FILE_PATH_LIST        = ["data/auras.json"]

TEST_ENABLE = True

BOARD_ROWS      = 7
BOARD_COLS      = 7
HAND_SPELLS     = 7
DECK_SPELLS     = 9
DECK_COMPANIONS = 4
ACTION_LIST_LEN = 5

class DataBase:

    def __init__(self):
        self._heroes = {}
        for filePath in HEROES_FILE_PATH_LIST:
            heroesFile = open(filePath, "r")
            self._heroes.update(json.load(heroesFile))
            heroesFile.close()

        self._companions = {}
        for filePath in COMPANIONS_FILE_PATH_LIST:
            companionsFile = open(filePath, "r")
            self._companions.update(json.load(companionsFile))
            companionsFile.close()

        self._entities = {}
        for filePath in ENTITIES_FILE_PATH_LIST:
            entitiesFile = open(filePath, "r")
            self._entities.update(json.load(entitiesFile))
            entitiesFile.close()

        self._spells = {}
        for filePath in SPELLS_FILE_PATH_LIST:
            spellsFile = open(filePath, "r")
            self._spells.update(json.load(spellsFile))
            spellsFile.close()

        self._auras = {}
        for filePath in AURAS_FILE_PATH_LIST:
            aurasFile = open(filePath, "r")
            self._auras.update(json.load(aurasFile))
            aurasFile.close() 

    @property
    def heroes(self):
        return self._heroes

    @property
    def companions(self):
        return self._companions

    @property
    def entities(self):
        return self._entities

    @property
    def spells(self):
        return self._spells

    @property
    def auras(self):
        return self._auras

db = DataBase()