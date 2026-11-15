---
name: release
description: Publier une version — choisir le niveau (patch/minor/major) avec l'utilisateur, incrémenter le numéro de version, compléter l'historique des versions, regrouper les commits, tagger et pousser. À utiliser dès qu'un commit touche l'application déployée, ou quand l'utilisateur demande une version, un tag ou une release.
---

# Publier une version

Les paramètres propres au dépôt (fichier qui porte la version, fichiers d'historique, auteur des commits de version, format du tag, branche principale, commande de tests, chemins qui relèvent de l'application) sont dans la section « Paramètres des skills » du `CLAUDE.md` du dépôt. Les lire avant de commencer ; s'il en manque un, le demander à l'utilisateur plutôt que de le deviner.

## 1. Faut-il une version ?

Regarder ce qui change par rapport à la branche principale distante (`git diff --stat origin/<branche>`) :

- Fichiers de l'application déployée : oui, poser la question (étape 2).
- Documentation seule, outillage annexe, tests, workflows : en principe pas de version. Committer et pousser sans tag, sans poser la question.

## 2. Choisir le niveau avec l'utilisateur

Ne jamais incrémenter d'office. Poser la question (AskUserQuestion) au moment de committer, en recommandant un niveau :

- Patch (x.y.**Z**) : corrections, nettoyage, petits ajustements.
- Minor (x.**Y**.0) : nouvelle fonctionnalité ou changement de comportement visible.
- Major (**X**.0.0) : rupture de compatibilité (format de fichier, API publique).

Le niveau se juge du point de vue de l'utilisateur du service : une évolution technique sans effet visible pour lui (statistiques, outillage, endpoint de suivi) est un patch, même si elle ajoute un endpoint. Proposer aussi « pas de changement ».

Appliquer le bump seulement après la réponse.

## 3. Préparer le commit de version

1. Mettre le nouveau numéro dans le fichier de version.
2. Ajouter la version dans chaque fichier d'historique : une ligne juste après la dernière, même format, date du jour, auteur et résumé court (dans la langue de chaque fichier). Dans le même commit que le bump, jamais après coup.
3. Lancer toute la suite de tests. Ne pas continuer si un test échoue.

## 4. Un seul commit par version

Regrouper en un seul commit tous les commits locaux de cette version pas encore poussés :

```bash
git fetch origin <branche>
git log --oneline origin/<branche>..HEAD        # ce qui sera regroupé
git reset --soft origin/<branche>
git commit --author="<auteur>" -m "X.Y.Z : résumé"
```

Ne jamais squasher ni réécrire ce qui est déjà poussé (branches, tags). Si la branche distante a avancé entre-temps, rebaser d'abord (`git rebase origin/<branche>`), puis regrouper.

## 5. Tag et push

```bash
git tag -a vX.Y.Z -m "<message de tag>"
git push origin <branche> vX.Y.Z
```

- Un commit sans changement de version ne reçoit pas de tag. Ne jamais déplacer ni supprimer un tag déjà poussé.
- En session cloud (Claude Code sur le web), le proxy git peut n'autoriser que certaines branches : pousser avec `git push origin HEAD:<branche>` ; si le push du tag est refusé (HTTP 403), le signaler et donner à l'utilisateur la commande à lancer depuis sa machine :

  ```bash
  git fetch origin && git tag -a vX.Y.Z <sha> -m "<message de tag>" && git push origin vX.Y.Z
  ```

## 6. Après le push

- Vérifier que le commit est sur la branche distante (`git ls-remote origin refs/heads/<branche>`) et que l'intégration continue passe sur ce commit.
- Si la production se déploie à part (skill `deploy-production`), le proposer, ne jamais le faire sans demande explicite.
- Rapporter : version, commit, tag (poussé ou commande à lancer), état des tests.
