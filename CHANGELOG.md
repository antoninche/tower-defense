# Changelog

Toutes les évolutions notables du projet sont documentées ici.
Le format s'inspire de [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/).

## [1.0.0] — 2026-07-04

### Ajouté
- Panneau d'interface (HUD) dédié à droite de l'aire de jeu : vague, or, vies et sélecteur de tours.
- Système de **vies** : perdre une vie à chaque ennemi atteignant la base, défaite à zéro.
- Condition de **victoire** après avoir survécu à 15 vagues.
- **Machine à états** : menu titre, jeu, pause, écran de défaite et de victoire.
- **Effets sonores** générés par code (tir, impact, pose de tour, brèche, vague, fin de partie).
- **Aperçu de portée** et indicateur de placement valide/invalide au curseur.
- **Barres de vie** au-dessus des ennemis et **effets d'explosion** à leur mort.
- Bannière d'annonce de vague.
- Contrôles étendus : sélection de tour (1-4), pose à l'Espace, pause (P), rejouer (R), WASD.
- **Exécutables autonomes** Windows (`.exe`) et macOS (`.app`) via PyInstaller, construits et publiés automatiquement par un workflow GitHub Actions.

### Modifié
- Réorganisation du code monolithique en un **package modulaire** (`settings`, `audio`, `entities`, `game`).
- Nommage des tours et centralisation de l'équilibrage dans `settings.py`.
- Fenêtre élargie (176×128) pour séparer l'aire de jeu de l'interface.

### Corrigé
- Remplacement de l'appel déprécié `pyxel.image()` par `pyxel.images[]`.

## [0.1.0] — Nuit du Code

### Ajouté
- Version initiale : carte, chemin, 4 tours, ennemis en vagues, projectiles, économie.
