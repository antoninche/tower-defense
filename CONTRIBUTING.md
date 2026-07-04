# Contribuer

Merci de votre intérêt pour ce projet ! Les contributions sont les bienvenues.

## Mettre en place l'environnement

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Lancez le jeu avec `python app.py`.

## Proposer une modification

1. **Forkez** le dépôt et créez une branche : `git checkout -b ma-fonctionnalite`.
2. Faites vos modifications en gardant le style existant (voir ci-dessous).
3. Vérifiez que le jeu se lance sans erreur et que le code compile :
   ```bash
   python -m py_compile app.py tower_defense/*.py
   ```
4. **Commitez** avec un message clair, puis ouvrez une **Pull Request** décrivant votre changement.

## Style de code

- Le code et les commentaires sont rédigés en **français**, comme le reste du projet.
- Suivez [PEP 8](https://peps.python.org/pep-0008/) (lignes ≤ 100 caractères).
- Toute valeur d'équilibrage (coûts, dégâts, vies, vagues…) va dans `tower_defense/settings.py`.
- Ajoutez une entrée dans [CHANGELOG.md](CHANGELOG.md) pour les changements notables.

## Idées de contributions

- Nouveaux types de tours ou d'ennemis
- Amélioration/vente de tours
- Sauvegarde du meilleur score
- Nouvelles cartes / chemins
- Musique de fond
