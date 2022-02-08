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
| target | Entity or tile on which the effect is applied |
| self | Entity which apply the effect |
| allOrganicAround | All entities, not mechanism, around |
| myOrganicAround | Current player entities, not mechanism, around |
| opOrganicAround | Opponent entities, not mechanism, around |
| allOrganicAligned | All entities, not mechanism, on a line |
| opOrganicAligned | Opponent entities, not mechanism, on a line |
| allOrganicCross:n | All entities, not mechanism, in a cross with an n-radius |
| myHero | Hero entity of the current player |
| opHero | Hero entity of the opponent of the current player |
| myPlayer | |
| opPlayer | |
| currentSpell |  |
| hand | All spells in hand |

### conditionList

This is an example : [{"feature" : "elemState", "value" : "oiled", "operator" : "="}]

| Key | Description |
|-----|-------------|
| elemState | |
| elem | |
| targetPv | |
| opAroundSelf | |
| turn | op, my |
| spellsPlayedDuringTurn | |
| oneByTurn | |
| auraNb | |
| targetPv | |
| myCompanions | |
| rangeFromHero | |
| rangeFromFirstTarget | |
| rangeFromSelf | Not implemented (ex : Bond de Goultard) |

### break

| Key | Description |
|-----|-------------|
| True | |
| False | |

### feature

| Key | Description |
|-----|-------------|
| pv | |
| stealLife | Same as pv on the target but heal the caster |
| pm | |
| atk | |
| gauges | Value must be a dict |
| paStock | |
| position | Value is targetIdx of the destination among the spellTargetList |
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
| addAuraWeak | Keep the current aura nb, add the new aura nb and keep the current type |
| addAuraStrong | Keep the current aura nb, add the new aura nb and replace them by the new type |
| addAuraReset | If current aura type is different than new aura type, remove current aura to replace by the new |
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


