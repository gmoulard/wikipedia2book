# Wikipedia2Book

Wikipedia2Book est un projet d'application web qui permettra de composer un livre PDF imprimable à partir d'articles Wikipédia. L'utilisateur pourra choisir les articles, explorer les liens associés, organiser le contenu et configurer la mise en page avant l'export.

## Fonctionnalités prévues

- Créer et gérer plusieurs projets avec sauvegarde persistante.
- Ajouter plusieurs articles par titre, URL ou recherche.
- Explorer les liens internes de Wikipédia en réglant la profondeur et les limites.
- Sélectionner manuellement les articles à inclure; les articles découverts ne sont jamais ajoutés automatiquement.
- Organiser les articles et configurer le format du livre.
- Générer un PDF imprimable en préservant les références et les informations de licence disponibles.

## Architecture

- Python et FastAPI pour le backend.
- HTML, CSS et JavaScript pour l'interface web.
- API officielle MediaWiki pour rechercher et récupérer les contenus.
- SQLite ou JSON pour le stockage des projets.
- WeasyPrint ou une solution équivalente pour générer les PDF.
- Docker et Docker Compose pour le déploiement.

Les détails fonctionnels et techniques sont décrits dans [SPECIFICATIONS.md](SPECIFICATIONS.md).

## État du projet

Le dépôt contient les premiers modules du backend FastAPI, le `Dockerfile` et `requirements.txt`. L'interface web et `docker-compose.yml` restent à créer. L'API fournit déjà la gestion des projets, la recherche et l'ajout d'articles, l'exploration des liens, la sélection et la génération PDF.

## Démarrer l'API

Avec Python 3.12 et les dépendances système nécessaires à WeasyPrint installées :

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

La documentation interactive de l'API est disponible sur `http://localhost:8000/docs`.

Le conteneur peut être lancé directement, avec des volumes nommés pour conserver projets et PDF :

```bash
docker build -t wikipedia2book .
docker run --rm -p 8000:8000 \
	-v wikipedia2book-data:/app/data \
	-v wikipedia2book-output:/app/output \
	wikipedia2book
```

test it : https://wikipedia2book-production.up.railway.app/
