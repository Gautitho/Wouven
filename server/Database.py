import json

HEROES_FILE_PATH        = "data/heroes.json"
COMPANIONS_FILE_PATH    = "data/companions.json"
ENTITIES_FILE_PATH      = "data/entities.json"
SPELLS_FILE_PATH        = "data/spells.json"

BOARD_ROWS  = 7
BOARD_COLS  = 7
HAND_SPELLS = 7

class DataBase:

    def __init__(self):
        heroesFile          = open(HEROES_FILE_PATH, "r")
        self._heroes        = json.load(heroesFile)
        heroesFile.close()

        companionsFile      = open(COMPANIONS_FILE_PATH, "r")
        self._companions    = json.load(companionsFile)
        companionsFile.close()

        entitiesFile        = open(ENTITIES_FILE_PATH, "r")
        self._entities      = json.load(entitiesFile)
        entitiesFile.close()

        spellsFile          = open(SPELLS_FILE_PATH, "r")
        self._spells        = json.load(spellsFile)
        spellsFile.close()

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

db = DataBase()