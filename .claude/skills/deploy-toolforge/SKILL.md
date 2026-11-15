---
name: deploy-toolforge
description: Déployer Wikipedia2Book en production sur Toolforge (wikipedia2book.toolforge.org) en poussant main vers la branche production-toolforge, puis suivre et vérifier le déploiement ; aussi republier une ancienne version. À utiliser uniquement quand l'utilisateur demande explicitement un déploiement ou une mise en production Toolforge.
---

# Déployer sur Toolforge

Toolforge suit la branche `production-toolforge` ; un push sur `main` ne déploie jamais Toolforge (Railway et Northflank, eux, suivent `main`). Ne pousser vers `production-toolforge` que sur demande explicite de l'utilisateur, pour ce déploiement-là. Description complète : `docs/SPECIFICATIONS.fr.md`, sections 13.6 et 13.7.

## 1. Avant de pousser

1. `git fetch origin` puis montrer ce qui va partir en production :

   ```bash
   git log --oneline origin/production-toolforge..origin/main
   ```

   Rien à déployer : le dire et s'arrêter.
2. Vérifier que le workflow « Tests and Toolforge deploy » est vert sur `origin/main` pour ce commit (GitHub Actions). Rouge : ne pas déployer, le signaler.
3. Si `app/` a changé depuis le dernier déploiement sans nouvelle version, le signaler (skill `release`) avant de continuer.

## 2. Pousser

```bash
git push origin origin/main:production-toolforge
```

Avance rapide uniquement : jamais de `--force`, sauf pour republier une version antérieure à la demande explicite de l'utilisateur :

```bash
git push --force origin vX.Y.Z^{}:production-toolforge
```

En session cloud, le proxy git peut refuser ce push (HTTP 403, branches limitées) : le dire et donner la commande à lancer depuis sa machine, ou proposer de relancer le workflow sur `production-toolforge` depuis l'onglet Actions si le code est déjà sur la branche.

## 3. Suivre le workflow

Le push déclenche « Tests and Toolforge deploy » sur `production-toolforge` :

- job `test` : toute la suite `unittest` ;
- job `deploy` (après `test`) :
  1. « Hourly statistics before restart » : relève les hits par heure avant que le redémarrage n'efface les journaux, et les committe sur `main` (`scripts/update-stats.sh deploy`). En `continue-on-error` : un échec donne un avertissement, jamais un blocage. Le signaler s'il échoue.
  2. « Build and restart on Toolforge » : `scripts/toolforge-deploy.sh` par SSH (build, variables d'environnement, redémarrage, puis attente jusqu'à 200 s que `/api/version` renvoie le commit construit).

Suivre l'exécution (actions_list / get_job_logs) jusqu'à la fin ; ne pas annoncer de succès avant.

## 4. Vérifier

- Le job `deploy` affiche `déployé : <commit>` : c'est la vérification de référence (le script compare `/api/version` au commit construit).
- Si le réseau de la session le permet : `curl -s https://wikipedia2book.toolforge.org/api/version` (version et commit attendus) et `curl -s https://wikipedia2book.toolforge.org/api/stats/hourly` (répond, compteur reparti de zéro).
- Le site GitHub Pages se reconstruit tout seul après le workflow (relevé horaire d'avant déploiement).

## 5. En cas d'échec

- Build en échec : les 60 dernières lignes du journal de build sont dans le job `deploy`.
- Le webservice ne sert pas le nouveau commit : les 50 dernières lignes de `toolforge webservice logs` sont dans le job.
- Diagnostic à la main, dans le compte de l'outil (`ssh <login>@login.toolforge.org`, puis `become wikipedia2book`) : `toolforge webservice status`, `toolforge webservice logs -f`, `toolforge build list`, `toolforge build logs <identifiant>`, `toolforge envvars list`.
- Revenir à la version précédente : republier son tag (section 2), seulement si l'utilisateur le demande.

## 6. Rapport

Commit et version déployés, résultat des deux étapes du job `deploy` (relevé horaire compris), et tout avertissement.
