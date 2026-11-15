---
name: release
description: Publier une version — choisir le niveau (patch/minor/major) avec l'utilisateur, incrémenter le numéro de version, compléter l'historique des versions, regrouper les commits, tagger et pousser. À utiliser dès qu'un commit touche l'application déployée, ou quand l'utilisateur demande une version, un tag ou une release.
---

# Publier une version

Les paramètres propres au dépôt (fichier qui porte la version, fichiers d'historique, auteur des commits de version, format du tag, branche principale, commande de tests, chemins qui relèvent de l'application) sont dans la section « Paramètres des skills » du `CLAUDE.md` du dépôt. Les lire avant de commencer ; s'il en manque un, le demander à l'utilisateur plutôt que de le deviner.

## 0. Partir d'un état propre

```bash
git fetch -q origin --tags
git status --short | grep -v '^??'
```

La seconde commande ne doit rien afficher en dehors des fichiers de cette version : une modification laissée par une autre session ne doit pas partir dans la version. Sinon, s'arrêter et demander à l'utilisateur.

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
2. Ajouter la version dans chaque fichier d'historique : une ligne juste après la dernière, même format, date du jour, auteur et résumé court (dans la langue de chaque fichier). Dans le même commit que le bump, jamais après coup. Écrire le résumé à partir de la liste réelle des changements depuis la dernière version, pas de mémoire :

   ```bash
   last=$(git tag -l 'v*' --sort=-v:refname | head -1)
   git log --oneline "$last"..HEAD
   ```

   Ne retenir que ce que voit l'utilisateur du service : un commit qui ne touche que l'outillage, la CI ou la documentation n'y figure pas.
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

Juste avant de taguer, vérifier que le fichier de version porte bien le numéro du tag (commande d'extraction dans `CLAUDE.md`) : les deux doivent être identiques.

```bash
git tag -a vX.Y.Z -m "<message de tag>"
git push origin <branche> vX.Y.Z
```

Si le dépôt a un workflow de contrôle des tags (voir `CLAUDE.md`), il échoue quand le tag et le fichier de version divergent : un tel échec ne se corrige jamais en déplaçant le tag, mais par une nouvelle version.

- Un commit sans changement de version ne reçoit pas de tag. Ne jamais déplacer ni supprimer un tag déjà poussé.
- En session cloud (Claude Code sur le web), le proxy git peut n'autoriser que certaines branches : pousser avec `git push origin HEAD:<branche>` ; si le push du tag est refusé (HTTP 403), le signaler et donner à l'utilisateur la commande à lancer depuis sa machine :

  ```bash
  git fetch origin && git tag -a vX.Y.Z <sha> -m "<message de tag>" && git push origin vX.Y.Z
  ```

## 6. Après le push

- Vérifier que le commit est sur la branche distante (`git ls-remote origin refs/heads/<branche>`).
- Suivre l'intégration continue sur ce commit jusqu'à la fin (et le contrôle du tag s'il a été poussé). Politique d'échec :
  - erreur réseau passagère (HTTP 5xx, téléchargement d'une dépendance, registre indisponible) : relancer le job **une seule fois** ;
  - toute autre erreur : lire le journal du job, le rapporter, ne pas relancer en boucle, ne jamais reposer ni déplacer le tag.
- Si la production se déploie à part (skill `deploy-production`), le proposer, ne jamais le faire sans demande explicite.

## 7. Rapport

- version, commit, tag (poussé, ou commande à lancer par l'utilisateur) ;
- résultat des tests locaux et de l'intégration continue ;
- résumé des changements retenus pour l'historique ;
- **ce qui n'a pas été vérifié** (liste des angles morts du dépôt dans `CLAUDE.md`, plus tout ce qui n'a pas pu être fait dans cette session, par exemple un tag non poussé ou une production pas encore déployée).
