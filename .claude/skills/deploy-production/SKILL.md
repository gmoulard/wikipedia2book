---
name: deploy-production
description: Mettre en production en poussant la branche principale vers une branche de production dédiée, puis suivre le déploiement automatique et le vérifier ; aussi republier une ancienne version. À utiliser uniquement quand l'utilisateur demande explicitement un déploiement ou une mise en production.
---

# Déployer via une branche de production

Stratégie : la production suit une branche dédiée, distincte de la branche principale. Un push sur la branche principale ne déploie donc jamais la production ; c'est le push vers la branche de production qui déclenche le workflow de déploiement.

Les valeurs propres au dépôt (plateforme d'hébergement, branche principale, branche de production, workflow et jobs, étapes particulières, adresse de vérification, commandes de diagnostic sur la plateforme) sont dans la section « Paramètres des skills » du `CLAUDE.md` du dépôt. Les lire avant de commencer ; s'il en manque une, la demander à l'utilisateur.

Ne pousser vers la branche de production que sur demande explicite de l'utilisateur, pour ce déploiement-là.

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

Suivre chaque job du workflow de déploiement jusqu'à la fin (actions_list / get_job_logs) ; ne pas annoncer de succès avant. Une étape marquée `continue-on-error` qui échoue n'empêche pas le déploiement mais doit être signalée.

## 4. Vérifier

- La vérification de référence est celle du job de déploiement (le commit servi est le commit construit), si le workflow en fait une.
- Si le réseau de la session le permet, interroger l'adresse de vérification (version et commit attendus).

## 5. En cas d'échec

- Lire le journal du job en échec : build, redémarrage ou vérification.
- Diagnostiquer avec les commandes de la plateforme indiquées dans `CLAUDE.md`.
- Revenir à la version précédente : republier son tag (section 2), seulement si l'utilisateur le demande.

## 6. Rapport

Commit et version déployés, résultat de chaque job et de chaque étape particulière, et tout avertissement.
