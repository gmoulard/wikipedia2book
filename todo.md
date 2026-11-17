# À faire

État au 16/11/2026. Production Toolforge : **1.11.0** et changements suivants (``). `` : ****, tag `` poussé.

Une action réalisée est retirée de cette liste (pas cochée) : l'historique Git garde la trace de ce qui a été fait.

## 1. Réglages à faire soi-même

-  **Auteur des commits en session cloud** : définir `GIT_AUTHOR_NAME`/`GIT_AUTHOR_EMAIL` (et `GIT_COMMITTER_NAME`/`GIT_COMMITTER_EMAIL`) comme variables de l'environnement « W2B » (valeurs non secrètes), menu de l'environnement cloud, puis Edit. C'est la règle retenue (paramètres `release` du `CLAUDE.md`) : la session refuse d'écrire l'adresse e-mail.
- **Connecteur GitHub du plugin** (`plugin:github:github`) : il échoue encore à la connexion (« Authorization header is badly formatted » le 16/11/2026). Les outils `gh` suffisent ; le reconnecter sur https://claude.ai/connect-github si un outil manque.

## 2. Nouvelle fonctionnalisées

- accepte les langues de wikibooks : DE, IT, JA, ID, HI, HU, ZH, PL, DE, EN exemple d'erreur https://de.wikibooks.org/wiki/Tauchen_in_Hilfeleistungsunternehmen:_-Teil_D-_Tauchermedizin
- Acccepte les langues de wikipedia, wikiversity, wikivoyage, Wikisource, Wikivoyage , Wikiversity , Wikiquote , Wiktionary,  Wikinews  
exemple d'erreur https://fr.wikiversity.org/wiki/D%C3%A9veloppement_durable
- dresse par rechereche sur internet une liste des pages dans la planette wikipedia ou est sité mediawiki2latex dans todo-mediawiki2latex-visibility.md
- pour chaque ligne dans todo-mediawiki2latex-visibility.md regarde comment ont peut ajouté une inforamtion sur wikipedia2book
- sauvegarde en plus de la logs sur le serveur le json de la demande de génération pour la mettre a disposition a coté du téléchargement de la log.

## 3. Améliorations possibles

- **Caractères chinois rares dans le PDF officiel de Wikisource** : signaler à Wikimédia (Phabricator, service PDF) les caractères des extensions CJK B et suivantes qui laissent un blanc (section 18 des spécifications).

