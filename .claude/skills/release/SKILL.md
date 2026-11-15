---
name: release
description: Publier une version de Wikipedia2Book — choisir le niveau (patch/minor/major) avec l'utilisateur, incrémenter app/main.py, ajouter la ligne d'historique FR et EN, regrouper les commits, tagger et pousser sur main. À utiliser dès qu'un commit touche l'application déployée, ou quand l'utilisateur demande une version, un tag ou une release.
---

# Publier une version

La version de l'application est dans `app/main.py` : `FastAPI(title="Wikipedia2Book", version="x.y.z")`.

## 1. Faut-il une version ?

Regarder ce qui change par rapport à `origin/main` (`git diff --stat origin/main`) :

- Fichiers de l'application déployée (`app/`, `requirements.txt`, `Dockerfile`, `Procfile`, `Aptfile`, `.python-version`, `toolforge-fonts.conf`) : oui, poser la question (étape 2).
- Documentation seule (`docs/`, `README.md`, `CLAUDE.md`), outils annexes (`scripts/`, `.github/workflows/`, `tests/`) : en principe pas de version. Committer et pousser sans tag, sans poser la question.

## 2. Choisir le niveau avec l'utilisateur

Ne jamais incrémenter d'office. Poser la question (AskUserQuestion) au moment de committer, en recommandant un niveau :

- Patch (x.y.**Z**) : corrections, nettoyage, petits ajustements.
- Minor (x.**Y**.0) : nouvelle fonctionnalité ou changement de comportement visible.
- Major (**X**.0.0) : rupture de compatibilité (format JSON exporté, API publique).

Le niveau se juge du point de vue de l'utilisateur du service PDF : une évolution technique sans effet visible pour lui (statistiques, outillage, endpoint de suivi comme `GET /api/stats/hourly`) est un patch, même si elle ajoute un endpoint. Proposer aussi « pas de changement ».

Appliquer le bump seulement après la réponse.

## 3. Préparer le commit de version

1. `app/main.py` : nouvelle version.
2. Section 19 de `docs/SPECIFICATIONS.fr.md` (« Historique des versions ») et de `docs/SPECIFICATIONS.en.md` (« Version history ») : une ligne juste après la dernière, même format, date du jour, auteur `GMoulard`, résumé court (anglais dans la version anglaise) :

   ```
   | 1.7.2   | 2026-11-15 | GMoulard  | Résumé court des modifications. |
   ```

   Dans le même commit que le bump, jamais après coup.
3. Lancer toute la suite de tests : `python3 -m unittest discover -s tests` (Linux, sessions cloud ; `pip install -r requirements.txt` si `fastapi`/`httpx` manquent) ou `.venv/Scripts/python.exe -m unittest discover -s tests -v` (poste Windows). Ne pas continuer si un test échoue.

## 4. Un seul commit par version

Regrouper en un seul commit tous les commits locaux de cette version pas encore poussés :

```bash
git fetch origin main
git log --oneline origin/main..HEAD        # ce qui sera regroupé
git reset --soft origin/main
git commit --author="gmoulard <gmoulard@gmail.com>" -m "X.Y.Z : résumé"
```

Ne jamais squasher ni réécrire ce qui est déjà poussé (`main`, tags, `production-toolforge`). Si `origin/main` a avancé entre-temps, rebaser d'abord (`git rebase origin/main`), puis regrouper.

## 5. Tag et push

```bash
git tag -a vX.Y.Z -m "Wikipedia2Book X.Y.Z"
git push origin main vX.Y.Z
```

- Un commit sans changement de version ne reçoit pas de tag. Ne jamais déplacer ni supprimer un tag déjà poussé.
- En session cloud (Claude Code sur le web), le proxy git n'autorise que certaines branches : pousser avec `git push origin HEAD:main` (et la branche de travail de la session) ; le push du tag est refusé (HTTP 403). Le signaler et donner à l'utilisateur la commande à lancer depuis sa machine :

  ```bash
  git fetch origin && git tag -a vX.Y.Z <sha> -m "Wikipedia2Book X.Y.Z" && git push origin vX.Y.Z
  ```

## 6. Après le push

- Vérifier que le commit est sur `origin/main` (`git ls-remote origin refs/heads/main`) et que le workflow « Tests and Toolforge deploy » passe sur ce commit.
- Railway et Northflank redéploient `main` d'eux-mêmes. Toolforge non : proposer le déploiement en production (skill `deploy-toolforge`), ne jamais le faire sans demande explicite.
- Rapporter : version, commit, tag (poussé ou commande à lancer), état des tests.
