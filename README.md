# Wikipedia2Book

Wikipedia2Book est un projet d'application web qui permettra de composer un livre PDF imprimable à partir d'articles Wikipédia. L'utilisateur pourra choisir les articles, explorer les liens associés, organiser le contenu et configurer la mise en page avant l'export.

## Fonctionnalités prévues

- Créer et gérer plusieurs projets dans la session du navigateur.
- Importer un fichier JSON existant et télécharger l'espace de travail en JSON.
- Ajouter plusieurs articles par titre, URL ou recherche; le contenu complet n'est récupéré qu'à la génération.
- Importer la liste des articles depuis l'URL d'une page de livre Wikipédia.
- Explorer les liens internes de Wikipédia en réglant la profondeur et les limites.
- Sélectionner manuellement les articles à inclure; les articles découverts ne sont jamais ajoutés automatiquement.
- Organiser les articles et configurer le format du livre.
- Générer un livre en assemblant les PDFs complets officiels téléchargés depuis Wikipédia.

## Architecture

- Python et FastAPI pour le backend.
- HTML, CSS et JavaScript pour l'interface web.
- API officielle MediaWiki pour la recherche et l'exploration; endpoint PDF officiel pour récupérer les articles complets à l'export.
- JSON échangé avec l'API, sans persistance des projets sur le serveur.
- WeasyPrint pour le frontispice et pypdf pour fusionner les PDFs en mémoire.
- Docker et Docker Compose pour le déploiement.

Les détails fonctionnels et techniques sont décrits dans [SPECIFICATIONS.md](SPECIFICATIONS.md).

## État du projet

Le dépôt contient le backend FastAPI et une interface web d'atelier éditorial. Elle permet de gérer les projets en mémoire dans le navigateur, rechercher ou ajouter des références sans télécharger le contenu complet, explorer les liens Wikipédia, contrôler la sélection, organiser les chapitres et régler le frontispice. À la génération, les PDFs complets des articles sélectionnés sont récupérés depuis Wikipédia et fusionnés en mémoire. Le serveur ne conserve pas les projets ni les PDF : l'utilisateur importe et télécharge explicitement un fichier JSON depuis l'interface.

## Démarrer l'application

Avec Python 3.12 et les dépendances système nécessaires à WeasyPrint installées :

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

L'interface web est disponible sur `http://localhost:8000` et la documentation interactive de l'API sur `http://localhost:8000/docs`.

Le conteneur peut être lancé directement :

```bash
docker build -t wikipedia2book .
docker run --rm -p 8000:8000 wikipedia2book
```

L'application est accessible sur `http://localhost:8000`.

La documentation de l'API en production est disponible sur [Railway](https://wikipedia2book-production.up.railway.app/docs).
