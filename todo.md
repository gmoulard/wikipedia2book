# À faire

État au 18/11/2026. Production Toolforge : **1.13.0**.

Une action réalisée est cochée (`[x]`) avec la version ou la date qui l'a faite ; les actions à faire restent en `[ ]`.

## 1. Réglages à faire soi-même

- [ ] **Auteur des commits en session cloud** : définir `GIT_AUTHOR_NAME`/`GIT_AUTHOR_EMAIL` (et `GIT_COMMITTER_NAME`/`GIT_COMMITTER_EMAIL`) comme variables de l'environnement « W2B » (valeurs non secrètes), menu de l'environnement cloud, puis Edit. C'est la règle retenue (paramètres `release` du `CLAUDE.md`) : la session refuse d'écrire l'adresse e-mail.
- [ ] **Secrets GitHub du déploiement** : le déploiement du 17/11/2026 n'a reçu que `WIKIPEDIA2BOOK_OAUTH_CLIENT_SECRET` ; définir aussi `WIKIPEDIA2BOOK_MONITOR_TOKEN` et `WIKIPEDIA2BOOK_OAUTH_CLIENT_ID` dans les secrets du dépôt (Settings, Secrets and variables, Actions), sinon le script lit le jeton dans les variables de l'outil.
- [ ] **Visibilité sur les wikis** : faire, à la main et en signalant le conflit d'intérêts, les ajouts proposés dans `todo-mediawiki2latex-visibility.md` (pages d'aide, gadgets, Wikidata).
- [ ] **Connecteur GitHub du plugin** (`plugin:github:github`) : il échoue encore à la connexion (« Authorization header is badly formatted » le 16/11/2026). Les outils `gh` suffisent ; le reconnecter sur https://claude.ai/connect-github si un outil manque.

## 2. Nouvelles fonctionnalités

- [x] Accepter les langues de Wikilivres (DE, IT, JA, ID, HI, HU, ZH, PL, EN), exemple d'erreur https://de.wikibooks.org/wiki/Tauchen_in_Hilfeleistungsunternehmen:_-Teil_D-_Tauchermedizin — déjà accepté : vérifié le 17/11/2026 sur Toolforge (1.12.4), dans le navigateur et par l'API, PDF généré.
- [x] Accepter les langues de Wikipédia, Wikiversité, Wikivoyage, Wikisource, Wikiquote, Wiktionnaire et Wikinews, exemple d'erreur https://fr.wikiversity.org/wiki/D%C3%A9veloppement_durable — déjà accepté : vérifié le 17/11/2026, même méthode.
- [x] Dresser la liste des pages de la planète Wikipédia qui citent mediawiki2latex dans `todo-mediawiki2latex-visibility.md` — fait le 17/11/2026 (recherche sur 19 wikis).
- [x] Pour chaque ligne de `todo-mediawiki2latex-visibility.md`, regarder comment ajouter une information sur Wikipedia2Book — fait le 17/11/2026 ; les modifications des wikis restent à faire à la main (section 1).
- [x] Garder, en plus du journal, le JSON de la demande de génération, téléchargeable à côté du journal — 1.12.5.
- [x] Garder un tableau des adresses refusées par Wikipedia2Book — 1.12.5 (page d'admin).
- [x] Proposer dans l'interface des couleurs pour la première et la dernière page, et le logo Wikipédia sur ces deux pages — 1.12.5.
- [x] Intégrer n'importe quelle page HTML, convertie en PDF par le serveur et intégrée comme un PDF — étape Organisation, champ d'adresse (1.13.0).
- [x] Pouvoir renommer une photo ou un document importé, pour ne pas voir le nom du fichier à l'impression — titre modifiable à l'étape Organisation (1.13.0).
- [x] Accepter les compilations de Wikilivres (`Wikilivres:Compilations/…`) et lire comme un livre toute page faite de lignes `: [[…]]` (1.13.0).
- [x] Logo de la licence à fond transparent (fichiers d'origine gardés), dernière page sans numéro, logo Wikipédia en bas à droite (1.13.0) ; le logo Wikipedia2Book sur la couverture et la dernière page, ajouté en 1.13.0, est retiré à la demande.

## 3. Améliorations possibles

- [ ] **Caractères chinois rares dans le PDF officiel de Wikisource** : signaler à Wikimédia (Phabricator, service PDF) les caractères des extensions CJK B et suivantes qui laissent un blanc (section 18 des spécifications).

## 4. Communication
{| class="wikitable"
|[[File:Wikipedia2book Logo.png|left|thumb|70x70px]][https://wikipedia2book.toolforge.org/ Wikipedia2Book] is a web application that allows you to compile a book in a printable PDF format. Users can select a Wikipedia book or specific articles, explore related links, organize content into chapters and volumes, and configure the layout before exporting the final PDF file. Available for: Wikipedia, Wikisource, Wikibooks, Wikivoyage, Wikiversity, Wikiquote, Wiktionary, and Wikinews.
|}


