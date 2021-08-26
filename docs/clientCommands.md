# Commands from client to server

## Commands format

The commands have the following json format :
```
{
    "cmd"       : "COMMAND_NAME",
    "playerId"  : "<ID of the client who sent this command>",
    "arg0"      : "arg0Value",
    "arg1"      : "arg1Value"
}
```

## Commands list

### **CREATE_GAME**
When two clients have sent AUTH command, the game is launched
| Argument | Type | Description |
|----------|------|-------------|
| gameName | String | Name of the game to create |

<br>

### **JOIN_GAME**
When two clients have sent AUTH command, the game is launched
| Argument | Type | Description |
|----------|------|-------------|
| gameName | String | Name of the game to join |

<br>

### **ENDTURN**
| Argument | Type | Description |
|----------|------|-------------|
||||

<br>

### **MOVE**
| Argument | Type | Description |
|----------|------|-------------|
| entityId | Integer | Instance ID of the entity to move |
| path | List of Dict | Sequence of positions ({"x" : posX, "y" : posY}) excluding starting position |

<br>

### **SPELL**
| Argument | Type | Description |
|----------|------|-------------|
| spellId | Integer | Instance ID of the spell in the player hand |
| targetPositionList | List of Dict{x, y} | Position of the targets |

<br>

### **SUMMON**
| Argument | Type | Description |
|----------|------|-------------|
| companionId | Integer | Instance ID of the companion in the player hand |
| summonPositionList | List of Dict{x, y} | Position where the companion will be summoned (if length > 1, trigger error) |