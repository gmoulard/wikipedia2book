# Wikipedia2Book

Wikipédia to Book est un projet d'application web qui permettra de composer un livre PDF imprimable à partir d'articles Wikipédia. L'utilisateur pourra choisir les articles, explorer les liens associés, organiser le contenu et configurer la mise en page avant l'export.

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

Le dépôt contient actuellement les spécifications et le `Dockerfile`. L'application, `requirements.txt` et `docker-compose.yml` restent à créer. Le conteneur ne peut donc pas encore être construit ni lancé. Le `Dockerfile` attend un module ASGI `app.main:app` et un fichier `requirements.txt` à la racine.

## Démarrage prévu

Une fois l'application et le fichier Compose ajoutés, le lancement visé est :

```bash
docker compose up -d --build
```

L'interface sera alors accessible à l'adresse indiquée par la configuration Compose, prévue par défaut sur `http://localhost:8000`. Le fichier Compose devra monter les données des projets dans un volume persistant pour les conserver après l'arrêt des conteneurs.