# Commands from server to client

## Commands format

The commands have the following json format :
```
{
    "cmd"   : "COMMAND_NAME",
    "arg0"  : "arg0Value",
    "arg1"  : "arg1Value"
}
```

## Commands list

### **WAIT_GAME_START**

<br>

### **GAME_START**

<br>

### **INIT**
Each player receive a diffrent INIT command at the start of the game
| Argument | Type | Description |
|----------|------|-------------|
| team | String | Team of the player who receive this command |

<br>

### **ERROR**
Return this command when a client command is not valid
| Argument | Type | Description |
|----------|------|-------------|
| msg | String | Error message |

<br>

### **STATUS**
Status of the game
| Argument | Type | Description |
|----------|------|-------------|
| turn | String | Team  whose turn it is |
| myPlayer | Dict | Status of the player who receive this cmd (Description below) |
| opPlayer | Dict | Status of the opponent of the player who receive this cmd (Description below) |
| entitiesList | List of Dict | Status of each entity on the board (Description below) |

<br>

### **END_GAME**
End of the game
| Argument | Type | Description |
|----------|------|-------------|
| result | String | 3 options : WIN, LOSS, DRAW |

<br>

#### MY_PLAYER
| Attribute | Type | Description |
|----------|------|-------------|
| heroDescId | String | Descriptor ID of the hero in data/heroes.json |
| team | String | Team of the entity  : red or blue |
| pseudo | String | Pseudo of the player |
| pa | Integer | Remaining PA of the player |
| paStock | Integer | PA in stock for this player |
| gauges | Dict(fire, water, earth, air, neutral) | Gauges of different elements |
| handSpellDescIds | List | Descriptor IDs of the spells in the player hand |
| handCompanionDescIds | List | Descriptor IDs of the companions in the player hand |
| handCompanionDescIds | List | Descriptor IDs of the companions already played by the player |
| boardEntityIds | List | Instance IDs of the entities owned by the player |
| heroEntityId | Integer|  |

<br>

#### OP_PLAYER
| Attribute | Type | Description |
|----------|------|-------------|
| heroDescId | String | Descriptor ID of the hero in data/heroes.json |
| team | String | Team of the entity  : red or blue |
| pseudo | String | Pseudo of the player |
| pa | Integer | Remaining PA of the player |
| paStock | Integer | PA in stock for this player |
| gauges | Dict(fire, water, earth, air, neutral) | Gauges of different elements |
| boardEntityIds | List | Instance IDs of the entities owned by the player |
| heroEntityId | Integer|  |

<br>

#### ENTITY_STATUS
| Attributes | Type | Description |
|----------|------|-------------|
| entityId | Integer | Instance ID of the entity |
| descId | String | Descriptor ID of the entity |
| team | String | Team of the entity  : red or blue |
| x | Integer | Position of the entity in X |
| y | Integer | Position of the entity in Y |
| pv | Integer | Hit points of the entity |
| armor | Integer | Armor of the entity |
| pm | Integer | Mouvement points of the entity |
| atk | Integer | Integer of the entity |
| elemState | String | Elemental state (fire, water, earth, air, "")|
| aura | Dict(type, nb) | Type and number of auras (only one) |
| states | List | Type of states (shield, stun, ...) |
| abilities | List of Dict(trigger, target, feature, value, effect) | Special abilities of the entity |
| canMove | Boolean |  |
| canAttack | Boolean |  |