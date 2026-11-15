---
name: deploy-toolforge
description: Déployer un outil en production sur Toolforge en poussant la branche principale vers sa branche de production, puis suivre et vérifier le déploiement ; aussi republier une ancienne version. À utiliser uniquement quand l'utilisateur demande explicitement un déploiement ou une mise en production Toolforge.
---

# Déployer sur Toolforge

Les paramètres propres au dépôt (nom de l'outil, branche principale, branche de production, workflow et jobs de déploiement, adresse de vérification, étapes particulières du job) sont dans la section « Paramètres des skills » du `CLAUDE.md` du dépôt. Les lire avant de commencer ; s'il en manque un, le demander à l'utilisateur.

Toolforge suit la branche de production : un push sur la branche principale ne déploie jamais Toolforge. Ne pousser vers la branche de production que sur demande explicite de l'utilisateur, pour ce déploiement-là.

## 1. Avant de pousser

1. `git fetch origin` puis montrer ce qui va partir en production :

   ```bash
   git log --oneline origin/<production>..origin/<principale>
   ```

   Rien à déployer : le dire et s'arrêter.
2. Vérifier que l'intégration continue est verte sur ce commit de la branche principale. Rouge : ne pas déployer, le signaler.
3. Si l'application a changé depuis le dernier déploiement sans nouvelle version, le signaler (skill `release`) avant de continuer.

## 2. Pousser

```bash
git push origin origin/<principale>:<production>
```

Avance rapide uniquement : jamais de `--force`, sauf pour republier une version antérieure à la demande explicite de l'utilisateur :

```bash
git push --force origin vX.Y.Z^{}:<production>
```

En session cloud, le proxy git peut refuser ce push (HTTP 403, branches limitées) : le dire et donner la commande à lancer depuis sa machine, ou proposer de relancer le workflow sur la branche de production depuis l'onglet Actions si le code y est déjà.

## 3. Suivre le workflow

Le push déclenche le workflow de déploiement sur la branche de production. Suivre chaque job jusqu'à la fin (actions_list / get_job_logs) ; ne pas annoncer de succès avant. Une étape marquée `continue-on-error` qui échoue n'empêche pas le déploiement mais doit être signalée.

## 4. Vérifier

- La vérification de référence est celle du job de déploiement (le commit servi est le commit construit), si le workflow en fait une.
- Si le réseau de la session le permet, interroger l'adresse de vérification de l'outil (version et commit attendus).

## 5. En cas d'échec

- Lire le journal du job en échec : build, redémarrage ou vérification.
- Diagnostic à la main, dans le compte de l'outil (`ssh <login>@login.toolforge.org`, puis `become <outil>`) : `toolforge webservice status`, `toolforge webservice logs -f`, `toolforge build list`, `toolforge build logs <identifiant>`, `toolforge envvars list`.
- Revenir à la version précédente : republier son tag (section 2), seulement si l'utilisateur le demande.

## 6. Rapport

Commit et version déployés, résultat de chaque job et de chaque étape particulière, et tout avertissement.
