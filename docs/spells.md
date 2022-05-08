# Spell keys

| Key | Type | Description |
|-----|------|-------------|
| name | String | Name of the spell |
| spritePath | String | Path of the hand sprite (from root of the project) |
| descSpritePath | String | Path of the description of the spell picture (from root of the project) |
| race | String | Race of the spell (who is allowed to use it) |
| elem | String | Element of the spell |
| cost | Int | Cost of the spell |
| allowedTargetList | List of Dict |  Type of target expected for the spell. For multi target spells, each element of the list match with a target |
| abilities | List of Dict | List of abilities of the spell, Ability type is described in abilities.md |

# Available values

## allowedTargetList

List of dictonnary with the following keys (target must match with all keys : AND) :

### entity

Boolean indicating if the target must be an entity.
True : Target is an entity.
False : Target is a tile.

### empty

Boolean indicating if the target must be an empty tile. Useless if entity key true.

### main

String

| Value | Description |
|-------|-------------|
| adjacent | |
| aligned | |
| firstAligned | |
| hero | |
| self | |

### ref

String

| Value | Description |
|-------|-------------|
| self | |
| firstTarget | |

### team

String

| Value | Description |
|-------|-------------|
| all | No team check |
| my | |
| op | |

### typeList

List of type the targeted Entity must match

### noTypeList

List of type the targeted Entity must not match