"""Boucle de jeu, machine à états et interface (HUD)."""

import pyxel

from . import audio
from .entities import (
    Curseur, Ennemi, Tour, est_sur_chemin, rectangles_se_chevauchent,
)
from .settings import (
    ARGENT_DEPART, C_BORDURE, C_FOND_PANNEAU, C_INVALIDE, C_OR, C_TEXTE,
    C_TEXTE_ATTENUE, C_VALIDE, C_VIE, CHEMIN_RESSOURCES, FPS, HAUTEUR, LARGEUR,
    STATS_TOURS, TAILLE_CASE, TITRE, TOUCHES_TOURS, VAGUE_VICTOIRE,
    VIES_DEPART, ZONE_JEU,
)

# États de la machine à états.
MENU, JEU, PAUSE, GAME_OVER, VICTOIRE = range(5)

_TOUCHES_NUM = (pyxel.KEY_1, pyxel.KEY_2, pyxel.KEY_3, pyxel.KEY_4)


class Jeu:
    """Point d'entrée : initialise Pyxel puis lance la boucle."""

    def __init__(self):
        pyxel.init(LARGEUR, HAUTEUR, title=TITRE, fps=FPS, quit_key=pyxel.KEY_NONE)
        pyxel.load(CHEMIN_RESSOURCES)
        audio.configurer()
        self.etat = MENU
        self.reinitialiser()

    def demarrer(self):
        """Lance la boucle de jeu Pyxel (bloquant)."""
        pyxel.run(self.update, self.draw)

    # -- Cycle de vie -------------------------------------------------------
    def reinitialiser(self):
        self.curseur = Curseur()
        self.tours = []
        self.ennemis = []
        self.projectiles = []
        self.effets = []
        self.argent = ARGENT_DEPART
        self.vies = VIES_DEPART
        self.vague = 1
        self.type_selectionne = 0
        self.compteur_spawn = 0
        self.nombre_spawn = 0
        self.nombre_a_spawn = self._effectif_vague()
        self.pause_vague = 0
        self.banniere_vague = FPS  # durée d'affichage de l'annonce de vague

    def _effectif_vague(self) -> int:
        return 10 + self.vague * 4

    def recompenser(self, ennemi):
        """Crédite l'argent gagné en éliminant un ennemi."""
        self.argent += 2 + ennemi.vie_max // 4

    # -- Boucle principale --------------------------------------------------
    def update(self):
        if self.etat == MENU:
            if _valider():
                self.etat = JEU
        elif self.etat == JEU:
            self._update_jeu()
        elif self.etat == PAUSE:
            if pyxel.btnp(pyxel.KEY_P) or _valider():
                self.etat = JEU
        elif self.etat in (GAME_OVER, VICTOIRE):
            if pyxel.btnp(pyxel.KEY_R):
                self.reinitialiser()
                self.etat = JEU

        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()

    def _update_jeu(self):
        if pyxel.btnp(pyxel.KEY_P):
            self.etat = PAUSE
            return

        self.curseur.update()

        for i, touche in enumerate(_TOUCHES_NUM):
            if pyxel.btnp(touche):
                self.type_selectionne = i
        if _valider():
            self.poser_tour(self.type_selectionne)

        self._gerer_vagues()

        for ennemi in self.ennemis[:]:
            ennemi.update()
            if ennemi.atteint_base:
                self._subir_breche()
        for tour in self.tours:
            tour.update()
        for projectile in self.projectiles[:]:
            if projectile.update():
                self.projectiles.remove(projectile)
        for effet in self.effets[:]:
            if effet.update():
                self.effets.remove(effet)

        self.ennemis[:] = [e for e in self.ennemis if not e.mort]
        if self.banniere_vague > 0:
            self.banniere_vague -= 1

    def _gerer_vagues(self):
        if self.nombre_spawn < self.nombre_a_spawn:
            self.compteur_spawn += 1
            delai = max(10, 45 - self.vague * 2)
            if self.compteur_spawn >= delai:
                self.ennemis.append(Ennemi(self))
                self.nombre_spawn += 1
                self.compteur_spawn = 0
        elif not self.ennemis:
            self.pause_vague += 1
            if self.pause_vague > 60:
                self._vague_suivante()

    def _vague_suivante(self):
        if self.vague >= VAGUE_VICTOIRE:
            self.etat = VICTOIRE
            audio.jouer(audio.VICTOIRE)
            return
        self.vague += 1
        self.nombre_spawn = 0
        self.nombre_a_spawn = self._effectif_vague()
        self.compteur_spawn = 0
        self.pause_vague = 0
        self.banniere_vague = FPS
        audio.jouer(audio.VAGUE)

    def _subir_breche(self):
        self.vies -= 1
        audio.jouer(audio.BRECHE)
        if self.vies <= 0:
            self.vies = 0
            self.etat = GAME_OVER
            audio.jouer(audio.GAME_OVER)

    def poser_tour(self, type_tour):
        x, y = self.curseur.case
        x = min(x, ZONE_JEU - 16)
        y = min(y, ZONE_JEU - 16)
        if not self._placement_valide(type_tour, x, y):
            return
        self.tours.append(Tour(self, x, y, type_tour))
        self.argent -= STATS_TOURS[type_tour]["cout"]
        audio.jouer(audio.POSE)

    def _placement_valide(self, type_tour, x, y) -> bool:
        if self.argent < STATS_TOURS[type_tour]["cout"]:
            return False
        if type_tour != 3 and est_sur_chemin(x, y):
            return False
        for tour in self.tours:
            if rectangles_se_chevauchent(x, y, 16, 16, tour.x, tour.y, 16, 16):
                return False
        return True

    # -- Rendu --------------------------------------------------------------
    def draw(self):
        pyxel.cls(0)
        if self.etat == MENU:
            self._draw_menu()
            return

        pyxel.clip(0, 0, ZONE_JEU, ZONE_JEU)
        pyxel.blt(0, 0, 0, 0, 0, ZONE_JEU, ZONE_JEU, 0)
        for tour in self.tours:
            tour.draw()
        for ennemi in self.ennemis:
            ennemi.draw()
        for projectile in self.projectiles:
            projectile.draw()
        for effet in self.effets:
            effet.draw()
        if self.etat == JEU:
            self._draw_curseur()
            if self.banniere_vague > 0:
                self._draw_banniere()
        pyxel.clip()

        self._draw_panneau()
        if self.etat == PAUSE:
            self._draw_overlay("PAUSE", "P / ESPACE : reprendre", C_OR)
        elif self.etat == GAME_OVER:
            self._draw_overlay("DEFAITE", "R : rejouer", C_INVALIDE)
        elif self.etat == VICTOIRE:
            self._draw_overlay("VICTOIRE !", "R : rejouer", C_VALIDE)

    def _draw_curseur(self):
        x, y = self.curseur.case
        x = min(x, ZONE_JEU - 16)
        y = min(y, ZONE_JEU - 16)
        valide = self._placement_valide(self.type_selectionne, x, y)
        couleur = C_VALIDE if valide else C_INVALIDE
        # Aperçu de la portée de la tour sélectionnée.
        portee = STATS_TOURS[self.type_selectionne]["portee"]
        if portee > 0:
            pyxel.circb(x + 8, y + 8, portee, C_TEXTE_ATTENUE)
        pyxel.rectb(x, y, TAILLE_CASE, TAILLE_CASE, couleur)
        pyxel.rectb(x + 1, y + 1, TAILLE_CASE - 2, TAILLE_CASE - 2, 7)

    def _draw_banniere(self):
        texte = f"VAGUE {self.vague}"
        largeur = len(texte) * 4
        x = (ZONE_JEU - largeur) // 2
        pyxel.rect(x - 4, 58, largeur + 8, 11, 0)
        pyxel.text(x, 61, texte, C_OR)

    def _draw_panneau(self):
        px = ZONE_JEU
        pyxel.rect(px, 0, LARGEUR - px, HAUTEUR, C_FOND_PANNEAU)
        pyxel.line(px, 0, px, HAUTEUR, C_BORDURE)

        pyxel.text(px + 4, 4, "VAGUE", C_TEXTE_ATTENUE)
        pyxel.text(px + 4, 11, f"{self.vague}/{VAGUE_VICTOIRE}", C_TEXTE)

        pyxel.text(px + 4, 22, "OR", C_TEXTE_ATTENUE)
        pyxel.text(px + 4, 29, f"{self.argent}", C_OR)

        pyxel.text(px + 4, 40, "VIES", C_TEXTE_ATTENUE)
        pyxel.text(px + 4, 47, f"{self.vies}", C_VIE)

        pyxel.line(px + 3, 58, LARGEUR - 3, 58, C_BORDURE)
        pyxel.text(px + 4, 61, "TOURS", C_TEXTE_ATTENUE)
        y = 68
        for i, stats in enumerate(STATS_TOURS):
            accessible = self.argent >= stats["cout"]
            if i == self.type_selectionne:
                pyxel.rect(px + 2, y - 1, LARGEUR - px - 4, 12, C_BORDURE)
            couleur = C_TEXTE if accessible else C_TEXTE_ATTENUE
            pyxel.text(px + 4, y, f"{TOUCHES_TOURS[i]} {stats['nom']}", couleur)
            pyxel.text(px + 8, y + 6, f"{stats['cout']} or",
                       C_OR if accessible else C_TEXTE_ATTENUE)
            y += 13

        pyxel.text(px + 4, HAUTEUR - 7, "P pause", C_TEXTE_ATTENUE)

    def _draw_overlay(self, titre, sous_titre, couleur):
        pyxel.rect(0, 50, ZONE_JEU, 30, 0)
        tx = (ZONE_JEU - len(titre) * 4) // 2
        pyxel.text(tx, 56, titre, couleur)
        sx = (ZONE_JEU - len(sous_titre) * 4) // 2
        pyxel.text(sx, 68, sous_titre, C_TEXTE)

    def _draw_menu(self):
        titre = "TOWER DEFENSE"
        tx = (LARGEUR - len(titre) * 4) // 2
        pyxel.text(tx, 34, titre, C_OR)
        pyxel.text(tx, 35, titre, C_OR)  # léger effet gras
        lignes = [
            ("Defendez la base", C_TEXTE),
            ("", C_TEXTE),
            ("Fleches/WASD : deplacer", C_TEXTE_ATTENUE),
            ("1-4 : choisir une tour", C_TEXTE_ATTENUE),
            ("ESPACE : poser  |  P : pause", C_TEXTE_ATTENUE),
            ("", C_TEXTE),
            ("ESPACE pour commencer", C_VALIDE),
        ]
        y = 54
        for texte, couleur in lignes:
            x = (LARGEUR - len(texte) * 4) // 2
            pyxel.text(x, y, texte, couleur)
            y += 9


def _valider() -> bool:
    """Touches communes de validation (poser / commencer)."""
    return pyxel.btnp(pyxel.KEY_SPACE) or pyxel.btnp(pyxel.KEY_RETURN)


def lancer():
    """Démarre le jeu."""
    Jeu().demarrer()
