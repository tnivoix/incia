# IDÉES
- Pouvoir choisir ce qu'on souhaite comparer sur les graphes.
- Graphes de 6 pour un dossier ou plusieurs avec les mêmes conditions.
- Possibilité d'uniformiser à 0.
- Graphes points et un vecteur ou pas de points et plusieurs vecteurs.
- Comparer automatiquement la stimulation à toutes les racines

DONE :
Choix des graphes (toujours les 6 graphes : 2 côtés et 3 racines) :
- Un sujet dans une condition
- Un sujet dans plusieurs conditions
- Plusieurs sujets dans une même condition

TECHNIQUE :
- Déplacement des évents sur le graphe
- Affichage ou non des graphes
- Buttons et inputs sur les graphes

TODO :
- Gérer les liens de fichiers de l'analyse
- Affiner l'algo de détection de burst
- Faire l'algo des starts de la stim

Scripts Spike2 :
- Artefact Suppressor
- Burst Analysis
- Event Counter [OK]
- Integration (auto/manual)
- MultiPhase
- Overdraw
- Phase Relationship
- Sled-PSTH

Derniere phase


Trame scénaristique :
La manip sort des fichiers smr avec la date, le spécimen et l'incrémentation suivant le nombre d'expérience.
Import des fichiers smr dans python pour une première détection automatique de burst (début et fin).
Affinage à la main par l'utilisateur des starts et ends.
Calculs des phases et analyses des bursts (starts, end, période, évenement à l'intérieur des bursts)
Export du fichier modifié dans python.

Choix des comparaisons des graphes.
Calculs des autres scripts dans python.