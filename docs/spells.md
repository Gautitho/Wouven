## Spells keys

| Key | Description |
|-----|-----------------|
| name | Name of the spell |
| spritePath | Path of the hand sprite (from root of the project) |
| descSpritePath | Path of the description of the spell picture (from root of the project) |
| race | Race of the spell (who is allowed to use it) |
| elem | Element of the spell |
| cost | Cost of the spell |
| allowedTargetList | Type of target expected for the spell. For multi target spells, each element of the list match with a target |
| abilities | List of abilities of the spell |

## Available values

### allowedTargetList

| Key | Description |
|-----|-----------------|
| all | All tile of the board |
| emptyTile | |
| allEntity | All entity on the board |
| allOrganic | All entity which are not mechanism |
| allMechanism | All mechanisms on the board |
| myEntity | All of the current player entity on the board |
| myOrganic | All of the current player entity which are not mechanism |
| myMechanism | All of the current player mechanisms |
| mySinistro | All of the current player sinistros |
| opEntity | All of the opponent of the current player entity on the board |
| opOrganic | All of the opponent of the current player entity which are not mechanism |
| opMechanism | All of the opponent of the current player mechanisms |
| self | Entity specified in 'race' field |
| myHero | Hero entity of the current player |
| opHero | Hero entity of the opponent of the current player |
| allAlignedOrganic | All entity, not mechanism, aligned with the caster |
| allFirstAlignedEntity | All entity aligned with the caster and with no entity between the caster and the target |
| allFirstAlignedOrganic | All entity, not mechanism, aligned with the caster and with no entity between the caster and the target |
| heroAdjacentTile | All adjacent tiles of the hero |
| firstTargetAdjacentTile | All adjacent tiles of the first target or first target |