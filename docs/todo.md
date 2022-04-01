# TODO List

- Gérer les deconnexions (Inactive start time ne se déclenche pas)
- Gérer organic / mecanic correctement
- Gérer les sorts qui cible le compagnon
- Joueur avec le deck le plus lourd commence
- Ombraden : le passif doit proc aussi pendant le tour de l'adversaire mais pas sur une invocation de compagnon
- Charge de toxine trigger passif Bouvaloir
- Sorts de : Phaeris, Remington, Julith, Coqueline, Flopin
- Faire un ou pour le stop trigger : Championne périmée, Julith, ...
- Empecher de cliquer les sorts qui n'existent pas
- Perte Pm de Toxine pas bonne
- Gelé ne fonctionne pas
- Flèche crucifiante fait des dégats autour
- Si un joueur fait un mauvais formulaire, il se retrouve quand même en tant que waitingPlayer (peut être uniquement en testMode)
- Edition de deck à partir du code
- Mécaniques à dev : 
  - Respawn de compagnon
  - Inciblable
  - Passif Bouvaloir
  - Effet par personnage trvaersé
  - Attirance
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
- Lancement de game : 
Traceback (most recent call last):
  File "/home/gautitho/workspace/Wouven/server/GameManager.py", line 63, in run
    self.FindGame(clientId, playerId, cmdDict["deck"])
  File "/home/gautitho/workspace/Wouven/server/GameManager.py", line 237, in FindGame
    self.create(gameName)
  File "/home/gautitho/workspace/Wouven/server/GameManager.py", line 147, in create
    self._currGameList.append(copy.deepcopy(self._nextGameList[self._gameIdx]))
IndexError: list index out of range