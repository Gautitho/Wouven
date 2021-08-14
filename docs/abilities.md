## Ability keys

| Key | Description |
|-----|-----------------|
| trigger | Determine on which event the effect occur |
| target | Target on which the effect is applied |
| conditionList | All the conditions must be true to trigger the effect |
| break | If true, prevent the spell to be casted |
| feature | Feature affected by the effect |
| value | Value of the effect |
| behavior | Specific behavior |

## Available values

### trigger

| Key | Description |
|-----|-----------------|
| always | At each action of all players |
| attack | |
| attacked | |
| spellCast | |
| spawn | |
| move | |

### target

| Key | Description |
|-----|-----------------|
| target | Entity on which the effect is applied |
| self | Entity which apply the effect |
| opAround | Opponents around |
| myPlayer | Player who own the entity which apply the effect |
| opPlayer |  |
| tile | |

### conditionList

This is an example : [{"feature" : "elemState", "value" : "oiled"}]

### break

| Key | Description |
|-----|-----------------|
| True | |
| False | |

### feature

| Key | Description |
|-----|-----------------|
| pv | |
| pm | |
| atk | |
| gauges | Value must be a dict |
| paStock | |
| position | |
| elemState | |
| "auraName" | Behavior must be addAura |

### value

| Key | Description |
|-----|-----------------|
| Integer | |
| String | Could be a feature |
| Dict | If feature is at gauges |

### behavior

| Key | Description |
|-----|-----------------|
| addAura |  |
| explosion |  |
| charge |  |
| state |  |

