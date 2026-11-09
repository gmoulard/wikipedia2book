# CLAUDE.md

Instructions pour Claude Code (ou tout agent) travaillant sur ce dépôt.

## Le projet

Wikipedia2Book crée directement un livre PDF imprimable à partir d'articles Wikipédia — il n'y a pas de notion de « projet » dans l'UI ni dans la doc produit (un seul livre, en mémoire, dès l'ouverture de la page). Le comportement de référence est documenté dans [SPECIFICATIONS.md](SPECIFICATIONS.md) : le lire avant toute modification fonctionnelle, et le mettre à jour dans le même changement si le comportement bouge. Ne jamais laisser la spec décrire une fonctionnalité qui n'existe pas dans le code, ni l'inverse.

## Principes de conception à préserver

- **Pas de gestion multi-projets.** Un seul livre à la fois, créé automatiquement en mémoire navigateur. Ne jamais réintroduire un écran de création/liste/suppression de « projets ».
- **Serveur sans état.** Aucune persistance disque côté serveur (pas de DB, pas de fichier projet, pas de PDF stocké). La sauvegarde est entièrement à la charge de l'utilisateur via export/import JSON depuis le navigateur.
- **Les articles ne sont jamais reconstruits.** Chaque article sélectionné est intégré tel quel via le PDF officiel Wikipédia (`/api/rest_v1/page/pdf/{titre}`). Ne pas réintroduire de parsing/reconstruction HTML du corps d'un article — c'était du code mort (`article_parser.py`) et a été supprimé pour cette raison.

## Style de code — « vibe coding »

Personne ne lit ce code. En conséquence :

- Pas de commentaires, pas de docstrings, pas de code mort ou « au cas où » (paramètre toujours appelé avec la même valeur, branche jamais atteinte, champ de modèle jamais lu/écrit). Supprimer plutôt que garder.
- Avant de supprimer un symbole (fonction, champ Pydantic, id HTML, classe CSS), `grep` tout le dépôt (`app/`, `app/static/`) pour confirmer qu'il n'est référencé nulle part — y compris côté JS/HTML pour du code backend et inversement.
- La robustesse fonctionnelle reste non négociable malgré l'absence de lecture humaine : gestion des erreurs réseau Wikipédia, validation des entrées, pas d'échec silencieux. « Personne ne lit le code » ne veut pas dire « la fiabilité n'importe pas ».

## Documentation à garder synchronisée

- `SPECIFICATIONS.md` : reflète le comportement réel, pas un objectif futur. Les évolutions non implémentées vont en section 18, pas dans le corps du document.
- `README.md` : doit rester cohérent avec `SPECIFICATIONS.md` (pas de doublon contradictoire, même terminologie).

## Repères d'architecture

- `app/main.py` — endpoints FastAPI, sans état.
- `app/models.py` — modèle Pydantic `Project` = l'état complet du livre. Le nom `Project` (et le format JSON exporté `{"format": "wikipedia2book-workspace", "version": 1, "projects": [...]}`) est un détail d'implémentation conservé pour la compatibilité des fichiers déjà exportés par des utilisateurs : ne pas renommer sans gérer une migration.
- `app/wikipedia_api.py` — unique point de contact avec MediaWiki (recherche, liens, PDF officiel). Toute nouvelle requête Wikipédia passe par `MediaWikiClient`, avec le même `User-Agent` et les mêmes bornes de timeout.
- `app/book_builder.py` — génère uniquement couverture, pages de chapitre et conclusion (WeasyPrint). Les pages d'articles ne sont jamais générées par l'app : toujours le PDF officiel Wikipédia tel quel, fusionné par `pypdf`.
- `app/explorer.py` — BFS sur les liens internes, bornes `max_depth ≤ 3`, `max_articles ≤ 200`.
- `app/static/app.js` — toute la logique front, un seul fichier, pas de framework. L'état vit dans `state.project`.

## Déploiement

Pas de `docker-compose.yml` dans ce dépôt : build/run via `Dockerfile` + `docker-build.sh` (injecte commit/date/auteur git pour le pied de page). Ne pas réintroduire Compose sans raison explicite de l'utilisateur.

## Versionnement

Chaque génération/modification de code par un agent doit incrémenter le numéro de version de l'application, dans `app/main.py` (`FastAPI(version="x.y.z")`) :

- Patch (x.y.**Z**) : corrections, nettoyage, petits ajustements.
- Minor (x.**Y**.0) : nouvelle fonctionnalité ou changement de comportement visible.
- Major (**X**.0.0) : rupture de compatibilité (ex. format JSON exporté, API publique).

Ne jamais terminer une génération de code sans ce bump, même minime.

## Vérification avant de considérer une tâche terminée

Un test automatisé existe : `tests/test_syntax.py` (stdlib `unittest`, aucune dépendance supplémentaire) — il vérifie que tous les fichiers `.py` sous `app/` parsent sans erreur de syntaxe. Le lancer pour la version courante avant de conclure une tâche touchant au backend :

```bash
.venv/Scripts/python.exe -m unittest discover -s tests -v
```

Au-delà de ce test de syntaxe, reste un angle mort : rien ne vérifie le comportement (gap connu, section 18 de la spec).

- `python`/`py` dans le PATH par défaut pointent vers l'alias cassé du Microsoft Store. Le vrai interpréteur est `C:\Users\<utilisateur>\AppData\Local\Programs\Python\Python312\python.exe`.
- Un virtualenv `.venv/` existe à la racine (ignoré par git) avec `requirements.txt` déjà installé : `.venv/Scripts/python.exe`.
- `import app.main` échoue nativement sur cette machine Windows : WeasyPrint a besoin des libs GTK/Pango/Cairo (`libgobject-2.0-0`, etc.) que seul le conteneur Docker installe (via `apt-get`, voir `Dockerfile`). Ce n'est pas un bug du code — ne pas essayer de « corriger » ça côté app. Pour vérifier le code qui ne dépend pas de `pdf_generator`/WeasyPrint (`models`, `book_builder`, `wikipedia_api`, `explorer`), importer ces modules directement, ils fonctionnent dans ce `.venv`.
- Pour tester la génération PDF de bout en bout (WeasyPrint inclus), il faut lancer l'app dans le conteneur Docker (`sh docker-build.sh && docker run --rm -p 8000:8000 wikipedia2book`) et dérouler le flux Sources → Organisation → Édition → export PDF.
