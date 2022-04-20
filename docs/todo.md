# TODO List

- Gérer les deconnexions (Inactive start time ne se déclenche pas)
- Gérer organic / mecanic correctement
- Joueur avec le deck le plus lourd commence
- Ombraden : le passif doit proc aussi pendant le tour de l'adversaire mais pas sur une invocation de compagnon
- Charge de toxine trigger passif Bouvaloir
- Sorts de : Phaeris, Remington, Julith, Coqueline, Flopin, Kerubim
- Si un joueur fait un mauvais formulaire, il se retrouve quand même en tant que waitingPlayer (peut être uniquement en testMode)
- 2022_04_19_20_39_52 bug création de partie
- Code du deck en édition
- Inciblable
- Mécaniques à dev : 
  - Rembobinage
  - Déclenchement d'un mécanisme
  - Transformation de mécanisme
  - Destruction de mechanisme quand on reconstruit le même 
  - Dépahasage

Traceback (most recent call last):
  File "/home/gautitho/workspace/Wouven/server/GameManager.py", line 72, in run
    nextGame = copy.deepcopy(self._currGameList[self._gameIdx])
IndexError: list index out of range

<class 'IndexError'>