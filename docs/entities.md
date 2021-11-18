## Entity keys

| Key | Description |
|-----|-----------------|
| name | String | Name of the entity |
| spritePath | String  | Path of the board sprite (from root of the project) |
| descSpritePath | String | Path of the description of the entity picture (from root of the project) |
| types | List of String | Types of the entity |
| pv | Int |  |
| armor | Int |  |
| atk | Int |  |
| pm | Int |  |
| aura | Dict | Dictonary with aura type and number |
| states | List of Dict | List of state of the entity |
| abilities | List of Dict | List of abilities of the entity |

### Available states

The following states are available : elelyAtk (permanent), bodyguard (permanent), bodyguarded(permanent), shield, disarmed, locked, frozen, petrified