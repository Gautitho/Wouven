## Ability keys

| Key | Description |
|-----|-------------|
| trigger | Determine on which event the effect occur |
| target | Target on which the effect is applied |
| conditionList | All the conditions must be true to trigger the effect |
| break | If true, prevent the spell to be casted |
| feature | Feature affected by the effect |
| value | Value of the effect |
| behavior | Specific behavior |
| targetIdx | Optionnal. When several targets, indicates which is targeted |
| stopTrigger | Optionnal. Indicates when the effect must disapear. If defined the ability is an ongoingAbility |

## Available values

### trigger

| Key | Description |
|-----|-------------|
| always | At each action of all players |
| attack | |
| attacked | |
| spellCast | |
| spawn | |
| move | |

### target

| Key | Description |
|-----|-------------|
| target | Entity on which the effect is applied |
| self | Entity which apply the effect |
| allOrganicAround | All entity, not mechanism, around |
| myOrganicAround | Current player entities, not mechanism, around |
| opOrganicAround | Opponent entities, not mechanism, around |
| allOrganicAligned | All entity, not mechanism, on a line |
| allOrganicCross:n | All entity, not mechanism, in a cross with an n-radius |
| myPlayer | Player who own the entity which apply the effect |
| opPlayer | |
| tile | |
| currentSpell |  |
| hand | All spells in hand |

### conditionList

This is an example : [{"feature" : "elemState", "value" : "oiled", "operator" : "="}]

| Key | Description |
|-----|-------------|
| elemState | |
| targetPv | |
| opAroundSelf | |

### break

| Key | Description |
|-----|-------------|
| True | |
| False | |

### feature

| Key | Description |
|-----|-------------|
| pv | |
| pm | |
| atk | |
| gauges | Value must be a dict |
| paStock | |
| position | |
| elemState | |
| cost | Target must be spell |
| "auraName" | Behavior must be addAura |
| "entityDesc" | Behavior must be invocation |

### value

| Key | Description |
|-----|-------------|
| Integer | |
| String | Could be a feature |
| Dict | If feature is at gauges |

### behavior

| Key | Description |
|-----|-------------|
| addAura |  |
| addState |  |
| explosion |  |
| charge |  |
| permanentState |  |
| melee |  |
| auraNb |  |
| opAffected |  |
| invocation |  |
| freeAura |  |
| bounce |  |
| push |  |
| pushBack |  |
| attackAgain |  |
| distance |  |

### stopTrigger

| Key | Description |
|-----|-------------|
| always | The effect disapears when after each action |
| spellCast | The effect disapears when a spell is cast (after pa paid but before abilities execution) |
| noArmor | The effect disapears when the entity have no armor |


