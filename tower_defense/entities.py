"""Entités du jeu : curseur, tours, ennemis, projectiles et effets.

Ces classes ne connaissent que l'objet ``jeu`` qui leur donne accès aux
listes partagées (tours, ennemis, projectiles) et à l'état (argent, vies).
"""

import math
import random

import pyxel

from . import audio
from .settings import (
    CHEMIN, COORDONNEES_TOURS, COULEUR_CHEMIN, SPRITES_COSTAUDS,
    SPRITES_ENNEMIS, STATS_TOURS, TAILLE_CASE, VITESSE_PROJECTILE, ZONE_JEU,
)


def arrondir(n: int) -> int:
    """Aligne une coordonnée sur la grille de placement des tours."""
    return (n // TAILLE_CASE) * TAILLE_CASE


def rectangles_se_chevauchent(x1, y1, l1, h1, x2, y2, l2, h2) -> bool:
    """Test de collision entre deux rectangles alignés sur les axes."""
    return not (x1 + l1 <= x2 or x2 + l2 <= x1 or y1 + h1 <= y2 or y2 + h2 <= y1)


def est_sur_chemin(x: int, y: int) -> bool:
    """Vrai si la case 16x16 en (x, y) recouvre le chemin des ennemis."""
    for dx, dy in [(2, 2), (8, 2), (13, 2), (2, 8), (8, 8), (13, 13)]:
        px, py = x + dx, y + dy
        if 0 <= px < ZONE_JEU and 0 <= py < ZONE_JEU:
            if pyxel.images[0].pget(px, py) == COULEUR_CHEMIN:
                return True
    return False


class Curseur:
    """Curseur piloté au clavier pour placer les tours."""

    def __init__(self):
        self.x = 16
        self.y = 16
        self.vitesse = 2

    def update(self):
        if pyxel.btn(pyxel.KEY_RIGHT) or pyxel.btn(pyxel.KEY_D):
            self.x += self.vitesse
        if pyxel.btn(pyxel.KEY_LEFT) or pyxel.btn(pyxel.KEY_A):
            self.x -= self.vitesse
        if pyxel.btn(pyxel.KEY_UP) or pyxel.btn(pyxel.KEY_W):
            self.y -= self.vitesse
        if pyxel.btn(pyxel.KEY_DOWN) or pyxel.btn(pyxel.KEY_S):
            self.y += self.vitesse
        self.x = max(0, min(self.x, ZONE_JEU - TAILLE_CASE))
        self.y = max(0, min(self.y, ZONE_JEU - TAILLE_CASE))

    @property
    def case(self):
        """Coin haut-gauche de la case visée, aligné sur la grille."""
        return arrondir(self.x), arrondir(self.y)


class Tour:
    """Tour défensive : tire des projectiles ou détruit au contact."""

    def __init__(self, jeu, x, y, type_tour):
        self.jeu = jeu
        self.x = x
        self.y = y
        self.type_tour = type_tour
        self.u, self.v = COORDONNEES_TOURS[type_tour]
        self.stats = STATS_TOURS[type_tour]
        self.compteur = 0
        self.flash = 0  # petit éclair visuel au moment du tir

    def update(self):
        if self.flash > 0:
            self.flash -= 1

        if self.stats["contact"]:
            self._attaquer_au_contact()
            return

        self.compteur += 1
        if self.compteur < self.stats["recharge"]:
            return

        cible = self._cible_la_plus_proche()
        if cible is not None:
            self.jeu.projectiles.append(
                Projectile(self.jeu, self.x + 8, self.y + 8, cible,
                           self.stats["degats"], self.stats["couleur"])
            )
            self.compteur = 0
            self.flash = 3
            audio.jouer(audio.TIR)

    def _attaquer_au_contact(self):
        for ennemi in self.jeu.ennemis[:]:
            if not ennemi.mort and rectangles_se_chevauchent(
                    self.x, self.y, 16, 16, ennemi.x, ennemi.y, 8, 8):
                ennemi.mort = True
                self.jeu.recompenser(ennemi)

    def _cible_la_plus_proche(self):
        cible = None
        distance_min = 10 ** 9
        cx, cy = self.x + 8, self.y + 8
        portee2 = self.stats["portee"] ** 2
        for ennemi in self.jeu.ennemis:
            if ennemi.mort:
                continue
            dx = (ennemi.x + 4) - cx
            dy = (ennemi.y + 4) - cy
            distance = dx * dx + dy * dy
            if distance < portee2 and distance < distance_min:
                distance_min = distance
                cible = ennemi
        return cible

    def draw(self):
        pyxel.blt(self.x, self.y, 1, self.u, self.v, 16, 16, 0)
        if self.flash > 0:
            pyxel.pset(self.x + 8, self.y + 8, 7)


class Ennemi:
    """Ennemi qui longe le chemin jusqu'à la base."""

    def __init__(self, jeu):
        self.jeu = jeu
        self.index_chemin = 0
        self.x, self.y = CHEMIN[0]
        self.vitesse = 1
        self.mort = False
        self.atteint_base = False

        disponibles = SPRITES_ENNEMIS[:min(jeu.vague, len(SPRITES_ENNEMIS))]
        self.u, self.v = random.choice(disponibles)

        if jeu.vague < 3:
            self.vie_max = random.choice([4, 5, 6]) + jeu.vague
        elif (self.u, self.v) in SPRITES_COSTAUDS:
            self.vie_max = random.choice([8, 9, 10, 11]) + jeu.vague
        else:
            self.vie_max = random.choice([5, 6, 7, 8]) + jeu.vague // 2
        self.vie = self.vie_max

    def update(self):
        if self.mort:
            return
        if self.index_chemin >= len(CHEMIN) - 1:
            self.mort = True
            self.atteint_base = True
            return

        tx, ty = CHEMIN[self.index_chemin + 1]
        if self.x < tx:
            self.x += self.vitesse
        elif self.x > tx:
            self.x -= self.vitesse
        elif self.y < ty:
            self.y += self.vitesse
        elif self.y > ty:
            self.y -= self.vitesse

        if self.x == tx and self.y == ty:
            self.index_chemin += 1

    def draw(self):
        pyxel.blt(self.x, self.y, 2, self.u, self.v, 8, 8, 0)
        # Barre de vie au-dessus de l'ennemi (uniquement si blessé).
        if self.vie < self.vie_max:
            ratio = max(0, self.vie) / self.vie_max
            pyxel.rect(self.x, self.y - 2, 8, 1, 0)
            couleur = 11 if ratio > 0.5 else (10 if ratio > 0.25 else 8)
            pyxel.rect(self.x, self.y - 2, round(8 * ratio), 1, couleur)


class Projectile:
    """Projectile qui poursuit une cible jusqu'à l'impact."""

    def __init__(self, jeu, x, y, cible, degats, couleur):
        self.jeu = jeu
        self.x = float(x)
        self.y = float(y)
        self.cible = cible
        self.degats = degats
        self.couleur = couleur
        dx = (cible.x + 4) - self.x
        dy = (cible.y + 4) - self.y
        distance = max(1.0, math.hypot(dx, dy))
        self.vx = dx / distance * VITESSE_PROJECTILE
        self.vy = dy / distance * VITESSE_PROJECTILE

    def update(self) -> bool:
        """Retourne True quand le projectile doit être retiré."""
        if self.cible not in self.jeu.ennemis:
            return True

        self.x += self.vx
        self.y += self.vy
        cx, cy = self.cible.x + 4, self.cible.y + 4

        if abs(self.x - cx) < 5 and abs(self.y - cy) < 5:
            if not self.cible.mort:
                self.cible.vie -= self.degats
                if self.cible.vie <= 0:
                    self.cible.mort = True
                    self.jeu.recompenser(self.cible)
                    self.jeu.effets.append(Explosion(cx, cy, self.couleur))
                    audio.jouer(audio.IMPACT)
            return True

        if not (-8 < self.x < ZONE_JEU + 8 and -8 < self.y < ZONE_JEU + 8):
            return True
        return False

    def draw(self):
        pyxel.circ(int(self.x), int(self.y), 2, self.couleur)


class Explosion:
    """Petite étincelle affichée à la mort d'un ennemi."""

    def __init__(self, x, y, couleur):
        self.x = x
        self.y = y
        self.couleur = couleur
        self.duree = 6

    def update(self) -> bool:
        self.duree -= 1
        return self.duree <= 0

    def draw(self):
        rayon = self.duree
        pyxel.circb(int(self.x), int(self.y), max(1, rayon), self.couleur)
        pyxel.circb(int(self.x), int(self.y), max(1, rayon - 2), 7)
