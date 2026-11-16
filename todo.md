# À faire

État au 16/11/2026. Production Toolforge : **1.9.7** et changements suivants (`5f0942c`). `main` : **1.10.0**, tag `v1.10.0` poussé.

Une action réalisée est retirée de cette liste (pas cochée) : l'historique Git garde la trace de ce qui a été fait.

## 1. Réglages à faire soi-même

- [ ] **Auteur des commits en session cloud** : définir `GIT_AUTHOR_NAME`/`GIT_AUTHOR_EMAIL` (et `GIT_COMMITTER_NAME`/`GIT_COMMITTER_EMAIL`) comme variables de l'environnement « W2B » (valeurs non secrètes), menu de l'environnement cloud, puis Edit. C'est la règle retenue (paramètres `release` du `CLAUDE.md`) : la session refuse d'écrire l'adresse e-mail.
- [ ] **Connecteur GitHub du plugin** (`plugin:github:github`) : il échoue encore à la connexion (« Authorization header is badly formatted » le 16/11/2026). Les outils `gh` suffisent ; le reconnecter sur https://claude.ai/connect-github si un outil manque.

## 2. Suivi de la production

- [ ] **Ligne « en direct » sous le graphique horaire de `stats.html`** : pas encore regardée.
- [ ] **Référence de l'atelier de performance** : la refaire sur 9 générations (3 lancements `min`, option `save_reference`, sur `main`), ce qui donnera aussi une première référence au scénario `livre-reference-images`.

## 3. Améliorations possibles

- [ ] **Mode `--stub` pour `scripts/limit_check.py`** : générer en local, dans le même processus, avec un faux client Wikipédia qui fabrique des PDF d'articles synthétiques (environ 1,8 Mo chacun), et mesurer la mémoire au pic, la durée et l'espace temporaire par palier. Le jouer aussi dans GitHub Actions, dans l'image Docker de production limitée en mémoire, pour trouver la limite sans télécharger depuis Wikipédia ni faire redémarrer Toolforge.
- [ ] **Mermaid 11.17.2** : un graphique dessiné après un `await` reste en texte, sans erreur. Contourné dans `docs/_includes/head-custom.html` (rendu d'abord, mise à jour ensuite), mais la cause n'est pas comprise.
- [ ] **GitHub Pages** publie aussi les fichiers bruts (`SPECIFICATIONS.*.md`, `stats.md`, `index.md`, `toolviews.csv`) à côté des pages HTML. C'est sans gravité ; les exclure si on le souhaite.
- [ ] **Caractères chinois rares dans le PDF officiel de Wikisource** : signaler à Wikimédia (Phabricator, service PDF) les caractères des extensions CJK B et suivantes qui laissent un blanc (section 18 des spécifications).

## 4. Fonctionnalités venues de mediawiki2latex

Toutes compatibles avec le principe « PDF officiel conservé ». Ces ajouts feraient de nouveaux appels à l'API MediaWiki : relire d'abord la politique robots de Wikimédia qui s'y applique.

- [ ] **Vérifier cette liste** contre la documentation réelle de mediawiki2latex (page MediaWiki de l'outil, options de l'interface web et de la ligne de commande), dressée de mémoire.
- [ ] Page de **crédits des images** : images de chaque article (`prop=images`), auteur et licence (`prop=imageinfo&iiprop=extmetadata`).
- [ ] **Renvois internes** : un lien vers un autre article du livre renverrait à sa page plutôt qu'au web, sur le modèle des liens de la table des matières.
