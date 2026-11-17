# À faire

État au 17/11/2026. Production Toolforge : **1.12.4** et changements suivants (`a81bd4b`).

Une action réalisée est retirée de cette liste (pas cochée) : l'historique Git garde la trace de ce qui a été fait.

## 1. Réglages à faire soi-même

-  **Auteur des commits en session cloud** : définir `GIT_AUTHOR_NAME`/`GIT_AUTHOR_EMAIL` (et `GIT_COMMITTER_NAME`/`GIT_COMMITTER_EMAIL`) comme variables de l'environnement « W2B » (valeurs non secrètes), menu de l'environnement cloud, puis Edit. C'est la règle retenue (paramètres `release` du `CLAUDE.md`) : la session refuse d'écrire l'adresse e-mail.
- **Secrets GitHub du déploiement** : le déploiement du 17/11/2026 n'a reçu que `WIKIPEDIA2BOOK_OAUTH_CLIENT_SECRET` ; définir aussi `WIKIPEDIA2BOOK_MONITOR_TOKEN` et `WIKIPEDIA2BOOK_OAUTH_CLIENT_ID` dans les secrets du dépôt (Settings, Secrets and variables, Actions), sinon le script lit le jeton dans les variables de l'outil.
- **Visibilité sur les wikis** : faire, à la main et en signalant le conflit d'intérêts, les ajouts proposés dans `todo-mediawiki2latex-visibility.md` (pages d'aide, gadgets, Wikidata).
- **Connecteur GitHub du plugin** (`plugin:github:github`) : il échoue encore à la connexion (« Authorization header is badly formatted » le 16/11/2026). Les outils `gh` suffisent ; le reconnecter sur https://claude.ai/connect-github si un outil manque.

## 2. Améliorations possibles

- **Caractères chinois rares dans le PDF officiel de Wikisource** : signaler à Wikimédia (Phabricator, service PDF) les caractères des extensions CJK B et suivantes qui laissent un blanc (section 18 des spécifications).

