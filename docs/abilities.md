# Ability keys

| Key | Type | Description |
|-----|------|-------------|
| trigger | String | Determine on which event the effect occur |
| target | Dict | Target on which the effect is applied |
| conditionList | List of Dict | All the conditions must be true to trigger the effect |
| break | Boolean | If true, prevent the spell to be casted |
| feature | Str | Feature affected by the effect |
| value | Int, Str, Dict | Value of the effect |
| behavior | Str | Specific behavior |
| stopTrigger | Str | Optionnal. Indicates when the effect must disapear. If defined the ability is an ongoingAbility |

# Available values

## trigger

| Value | Description |
|-----|-------------|
| always | After each action of each player but before endAction |
| alwaysAfterEnd | After each action of each player but after endAction |
| attack | |
| attacked | |
| spellCast | |
| spawn | |
| move | |
| death | |
| startTurn | |
| endTurn | |

## target

Dict with the following keys (target must match with all keys : AND) :

### main

String

| Value | Description |
|-----|-------------|
| target | Entity or tile on which the effect is applied |
| self | Entity which apply the effect |
| player | |
| hero | |
| around | |
| adjacent | |
| aligned | |
| firstAligned | |
| alignedInDirection | |
| cross | |
| board | |
| highestPv | |
| currentSpell |  |
| hand | All spells in hand |

### team

String

| Value | Description |
|-----|-------------|
| my | |
| op | |
| all | |
| target | |

### targetIdx

Integer determining which target from allowedTargetList (client click) is affected by ability

### ref

String

| Value | Description |
|-----|-------------|
| self | |
| target | |
| myHero | |
| opHero | |

### refIdx

Integer determining which target from allowedTargetList (client click) is taken as ref by ability

### range

Integer

### typeList

List of type the targeted Entity must match

### noTypeList

List of type the targeted Entity must not match

## conditionList

Dict with the following keys (target must match with all keys : AND) :

### feature

String

| Value | Description |
|-------|-------------|
| elemState | |
| state | |
| elem | |
| paStock | |
| myCompanions | |
| range | |
| turn | |
| team | |
| type | |
| allowedTarget | |
| opsAroundRef | |
| spellsPlayedDuringTurn | |
| pv | |
| auraNb | |
| oneByturn | |
| behavior | |
| handSpells | |
| position | |

### operator

String

| Value | Description |
|-------|-------------|
| == | |
| != | |
| > | |
| < | |
| >= | |
| <= | |

### operator

String

| Value | Description |
|-------|-------------|
| == | |
| != | |
| > | |
| < | |
| >= | |
| <= | |

### target

String

| Value | Description |
|-------|-------------|
| abilityTarget | |
| spellTarget | |
| spellTargetPlayer | |
| self | |
| myPlayer | |
| opPlayer | |

### targetIdx

Integer determining which target is affected by condition

### ref

String

| Value | Description |
|-------|-------------|
| self | |
| myHero | |
| opHero | |
| abilityTarget | |

### refIdx

Integer determining which target is selected to be ref of the condition

### value

Integer or String

## feature

| Value | Description |
|-------|-------------|
| pv | |
| stealLife | Same as pv on the target but heal the caster |
| pm | |
| atk | |
| gauges | Value must be a dict |
| paStock | |
| position | Value is targetIdx of the destination among the spellTargetList / -1 is self entity |
| elemState | |
| cost | Target must be spell |
| "auraName" | Behavior must be addAura |
| "entityDesc" | Behavior must be invocation |

## value

| Type | Description |
|------|-------------|
| Integer | |
| String | Could be a feature as atk |
| Dict | If feature is at gauges |

## behavior

| Value | Description |
|-------|-------------|
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

## stopTrigger

| Value | Description |
|-------|-------------|
| always | The effect disapears when after each action |
| spellCast | The effect disapears when a spell is cast (after pa paid but before abilities execution) |
| noArmor | The effect disapears when the entity have no armor |