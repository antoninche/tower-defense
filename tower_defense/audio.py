"""Effets sonores générés par code (aucun son n'est stocké dans le .pyxres).

Les sons sont définis une seule fois après l'initialisation de Pyxel, puis
joués via :func:`jouer`. Chaque effet a un identifiant lisible.
"""

import pyxel

# Identifiants de sons -> emplacement dans la banque Pyxel.
TIR = 0
IMPACT = 1
POSE = 2
BRECHE = 3
VAGUE = 4
GAME_OVER = 5
VICTOIRE = 6

# Canal réservé aux effets courts pour éviter qu'ils se coupent entre eux.
_CANAL = 0


def configurer() -> None:
    """Définit tous les effets sonores. À appeler après ``pyxel.init``."""
    pyxel.sounds[TIR].set("c3", "s", "5", "n", 12)
    pyxel.sounds[IMPACT].set("f2c2", "n", "6", "f", 10)
    pyxel.sounds[POSE].set("c3e3g3", "t", "6", "n", 18)
    pyxel.sounds[BRECHE].set("f2c2f1", "s", "7", "f", 22)
    pyxel.sounds[VAGUE].set("c3g3c4", "t", "5", "n", 22)
    pyxel.sounds[GAME_OVER].set("c3g2c2g1c1", "s", "6", "s", 26)
    pyxel.sounds[VICTOIRE].set("c3e3g3c4e4g4", "t", "6", "s", 20)


def jouer(son: int, canal: int = _CANAL) -> None:
    """Joue un effet sonore."""
    pyxel.play(canal, son)
