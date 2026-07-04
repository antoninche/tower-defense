"""Constantes et configuration globale du jeu.

Regroupe au même endroit toutes les valeurs qui pilotent l'équilibrage et
l'affichage. Modifier le gameplay se fait ici, sans toucher à la logique.
"""

from pathlib import Path

# --- Fenêtre & rendu -------------------------------------------------------
# La zone de jeu reste en 128x128 (taille de l'image de la carte).
# Un panneau d'interface (HUD) est ajouté à droite.
ZONE_JEU = 128            # largeur et hauteur de l'aire de jeu (carrée)
LARGEUR_PANNEAU = 48      # largeur du panneau HUD à droite
LARGEUR = ZONE_JEU + LARGEUR_PANNEAU
HAUTEUR = ZONE_JEU
TAILLE_CASE = 16          # les tours s'alignent sur une grille de 16 px
FPS = 30
TITRE = "Tower Defense"

# --- Ressources ------------------------------------------------------------
RACINE = Path(__file__).resolve().parent.parent
CHEMIN_RESSOURCES = str(RACINE / "assets" / "theme.pyxres")

# --- Carte & chemin --------------------------------------------------------
# Points de passage suivis par les ennemis (du départ vers la base).
CHEMIN = [(127, 111), (104, 12), (104, 16), (72, 16),
          (72, 112), (40, 112), (40, 64), (0, 64)]
COULEUR_CHEMIN = 12       # couleur du chemin dans l'image de la carte

# --- Économie & progression -----------------------------------------------
ARGENT_DEPART = 80
VIES_DEPART = 20
VAGUE_VICTOIRE = 15       # survivre à cette vague déclenche la victoire

# --- Palette (indices de la palette Pyxel) ---------------------------------
C_TEXTE = 7
C_TEXTE_ATTENUE = 13
C_OR = 10
C_VIE = 8
C_VALIDE = 11
C_INVALIDE = 8
C_FOND_PANNEAU = 1
C_BORDURE = 5

# --- Tours -----------------------------------------------------------------
# Chaque tour : coordonnées du sprite (image 1), stats et libellé HUD.
# "contact" = tour de zone qui détruit au contact (mine), sans projectile.
COORDONNEES_TOURS = [(0, 0), (16, 0), (32, 0), (48, 0)]
STATS_TOURS = [
    {"nom": "Archer",  "cout": 20, "degats": 1, "recharge": 16,
     "portee": 56, "couleur": 10, "contact": False},
    {"nom": "Canon",   "cout": 35, "degats": 2, "recharge": 24,
     "portee": 64, "couleur": 9,  "contact": False},
    {"nom": "Mortier", "cout": 55, "degats": 4, "recharge": 36,
     "portee": 80, "couleur": 8,  "contact": False},
    {"nom": "Mine",    "cout": 80, "degats": 0, "recharge": 1,
     "portee": 0,  "couleur": 11, "contact": True},
]
TOUCHES_TOURS = ("1", "2", "3", "4")

# --- Ennemis ---------------------------------------------------------------
SPRITES_ENNEMIS = [(0, 0), (8, 0), (16, 0), (24, 0), (32, 0), (40, 0)]
SPRITES_COSTAUDS = [(24, 0), (32, 0), (40, 0)]
VITESSE_PROJECTILE = 3.5
