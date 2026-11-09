# Wikipedia2Book

Wikipedia2Book est une application web qui permet de composer directement un livre PDF imprimable à partir d'articles Wikipédia, sans étape de création de « projet » : un livre est prêt dès l'ouverture de la page. L'utilisateur choisit les articles, explore les liens associés, organise le contenu en chapitres et configure la mise en page avant l'export.

## Fonctionnalités

- Un livre unique, construit en mémoire dans le navigateur; export/import de son état sous forme de fichier JSON.
- Ajout d'articles par titre, URL ou recherche; le contenu complet n'est récupéré qu'à la génération.
- Import de la liste des articles depuis l'URL d'une page de livre Wikipédia.
- Exploration des liens internes de Wikipédia avec profondeur et nombre d'articles paramétrables.
- Sélection manuelle des articles à inclure; les articles découverts ne sont jamais ajoutés automatiquement.
- Organisation des articles en chapitres, réordonnables par glisser-déposer, et configuration du format du livre.
- Génération d'un livre en assemblant les PDFs complets officiels téléchargés depuis Wikipédia, avec signets de navigation.

## Architecture

- Python et FastAPI pour le backend.
- HTML, CSS et JavaScript pour l'interface web (page unique, sans framework).
- API officielle MediaWiki pour la recherche et l'exploration; endpoint PDF officiel pour récupérer les articles complets à l'export.
- JSON échangé avec l'API, sans persistance sur le serveur.
- WeasyPrint pour la couverture, les pages de chapitre et la conclusion; pypdf pour fusionner les PDFs en mémoire.
- Docker pour le déploiement.

Les détails fonctionnels et techniques sont décrits dans [SPECIFICATIONS.md](SPECIFICATIONS.md).

## État du projet

Le dépôt contient le backend FastAPI et l'interface web correspondante. Elle permet de construire le livre en mémoire dans le navigateur, rechercher ou ajouter des références sans télécharger le contenu complet, explorer les liens Wikipédia, contrôler la sélection, organiser les chapitres et régler la couverture. À la génération, les PDFs complets des articles sélectionnés sont récupérés depuis Wikipédia et fusionnés en mémoire. Le serveur ne conserve ni le livre ni les PDF : l'utilisateur importe et télécharge explicitement un fichier JSON depuis l'interface.

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
sh docker-build.sh
docker run --rm -p 8000:8000 wikipedia2book
```

Le script `docker-build.sh` injecte automatiquement le commit, la date et l'auteur git dans l'image via `--build-arg`, ce qui permet au pied de page d'afficher la version correcte.

L'application est accessible sur `http://localhost:8000`.


Le déployement  [Railway](https://wikipedia2book-production.up.railway.app/).
La documentation de l'API en production est disponible sur [Railway](https://wikipedia2book-production.up.railway.app/docs).
