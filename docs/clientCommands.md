# Commands from client to server

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

### **AUTH**
When two clients have sent AUTH command, the game is launched
| Argument | Type | Description |
|----------|------|-------------|
| playerId | String | ID of the client who sent this command |

<br>

### **ENDTURN**
| Argument | Type | Description |
|----------|------|-------------|
| playerId | String | ID of the client who sent this command |

<br>

### **MOVE**
| Argument | Type | Description |
|----------|------|-------------|
| playerId | String | ID of the client who sent this command |
| entityId | String | Instance ID of the entity to move |
| path | List of Dict | Sequence of positions ({"x" : posX, "y" : posY}) excluding starting position |