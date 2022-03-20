# TODO List

- Gérer les deconnexions (Inactive start time ne se déclenche pas)
- Gérer organic / mecanic correctement
- Gérer les sorts qui cible le compagnon
- Joueur avec le deck le plus lourd commence
- Mécaniques à dev : 
  - Respawn de compagnon
  - Inciblable
  - Passif Bouvaloir
  - Effet par personnage trvaersé
  - Attirance
  - Echange
  - Maitre de l'agonie
  - Rembobinage
  - Déclenchement d'un mécanisme
  - Transformation de mécanisme
  - Destruction de mechanisme quand on reconstruit le même 
  - Dépahasage

Bugs non reproduits : 
- Deconnexion non détectée
File "/home/gautitho/workspace/Wouven/server/GameManager.py", line 68, in run
  gameCmdList = self._nextGameList[self._gameIdx].run(cmdDict)
IndexError: list index out of range