# À faire

État au 18/11/2026. Production Toolforge : **1.13.1**.

Une action réalisée est cochée (`[x]`) avec la version ou la date qui l'a faite ; les actions à faire restent en `[ ]`.

## 1. Réglages à faire soi-même

- [x] **Auteur des commits en session cloud** : définir `GIT_AUTHOR_NAME`/`GIT_AUTHOR_EMAIL` (et `GIT_COMMITTER_NAME`/`GIT_COMMITTER_EMAIL`) comme variables de l'environnement « W2B » (valeurs non secrètes), menu de l'environnement cloud, puis Edit. C'est la règle retenue (paramètres `release` du `CLAUDE.md`) : la session refuse d'écrire l'adresse e-mail. Fait le 18/11/2026 : vérifié dans une session cloud « W2B », les quatre variables sont définies et `git var GIT_AUTHOR_IDENT`/`GIT_COMMITTER_IDENT` les utilisent (elles passent avant le `user.name = Claude` de `/root/.gitconfig`).
- [x] **Secrets GitHub du déploiement** : le déploiement du 17/11/2026 n'a reçu que `WIKIPEDIA2BOOK_OAUTH_CLIENT_SECRET` ; définir aussi `WIKIPEDIA2BOOK_MONITOR_TOKEN` et `WIKIPEDIA2BOOK_OAUTH_CLIENT_ID` dans les secrets du dépôt (Settings, Secrets and variables, Actions), sinon le script lit le jeton dans les variables de l'outil. Fait le 18/11/2026 : les trois sont des secrets du dépôt (`gh secret list`), pas d'un environnement (le job `deploy` n'en déclare aucun) ; seront posés sur Toolforge au prochain déploiement.
- [ ] **Visibilité sur les wikis** : faire, à la main et en signalant le conflit d'intérêts, les ajouts proposés dans `communication/todo-mediawiki2latex-visibility.md` (pages d'aide, gadgets, Wikidata). Le 18/11/2026 : 17 publications faites (liste et diffs dans `communication/communication-brouillons.md`) ; action 5 (it.wikipedia) publiée le même jour depuis le compte CapitaineCanette ; action 15 (commentaire sur https://phabricator.wikimedia.org/T224922#12575282) publiée le même jour ; action 14 déposée (https://phabricator.wikimedia.org/T445303), billet Diff (action 19) soumis à relecture et présentations proposées à la WikiConvention francophone et à Wikimania 2027 (actions 20a, 20b), le même jour ; élément Wikidata créé le même jour (https://www.wikidata.org/wiki/Q142203097, déclarations remises une par une après un avertissement du filtre n° 11, ajouté à la fiche Toolhub) ; en.wikipedia Wikipedia:Books complété le 18/11/2026 (https://en.wikipedia.org/w/index.php?diff=1386351738&oldid=1383219292, conflit d'intérêts encore à signaler en page de discussion) ; restent Toolhub (connexion à faire), et les actions qui attendent une réponse.
- [x] **Connecteur GitHub du plugin** (`plugin:github:github`) : il échouait à la connexion (« Authorization header is badly formatted ») parce que la variable `GITHUB_PERSONAL_ACCESS_TOKEN`, lue par son en-tête `Authorization: Bearer …`, n'est pas définie. Désactivé le 18/11/2026 (`claude plugin disable github@synced --scope user`) : les outils `gh` suffisent. Pour le réactiver, définir la variable avec un jeton GitHub puis `claude plugin enable github@synced`.

## 2. Nouvelles fonctionnalités

- [x] Accepter les langues de Wikilivres (DE, IT, JA, ID, HI, HU, ZH, PL, EN), exemple d'erreur https://de.wikibooks.org/wiki/Tauchen_in_Hilfeleistungsunternehmen:_-Teil_D-_Tauchermedizin — déjà accepté : vérifié le 17/11/2026 sur Toolforge (1.12.4), dans le navigateur et par l'API, PDF généré.
- [x] Accepter les langues de Wikipédia, Wikiversité, Wikivoyage, Wikisource, Wikiquote, Wiktionnaire et Wikinews, exemple d'erreur https://fr.wikiversity.org/wiki/D%C3%A9veloppement_durable — déjà accepté : vérifié le 17/11/2026, même méthode.
- [x] Dresser la liste des pages de la planète Wikipédia qui citent mediawiki2latex dans `communication/todo-mediawiki2latex-visibility.md` — fait le 17/11/2026 (recherche sur 19 wikis).
- [x] Pour chaque ligne de `communication/todo-mediawiki2latex-visibility.md`, regarder comment ajouter une information sur Wikipedia2Book — fait le 17/11/2026 ; les modifications des wikis restent à faire à la main (section 1).
- [x] Garder, en plus du journal, le JSON de la demande de génération, téléchargeable à côté du journal — 1.12.5.
- [x] Garder un tableau des adresses refusées par Wikipedia2Book — 1.12.5 (page d'admin).
- [x] Proposer dans l'interface des couleurs pour la première et la dernière page, et le logo Wikipédia sur ces deux pages — 1.12.5.
- [x] Intégrer n'importe quelle page HTML, convertie en PDF par le serveur et intégrée comme un PDF — étape Organisation, champ d'adresse (1.13.0).
- [x] Pouvoir renommer une photo ou un document importé, pour ne pas voir le nom du fichier à l'impression — titre modifiable à l'étape Organisation (1.13.0).
- [x] Accepter les compilations de Wikilivres (`Wikilivres:Compilations/…`) et lire comme un livre toute page faite de lignes `: [[…]]` (1.13.0).
- [x] Logo de la licence à fond transparent (fichiers d'origine gardés), dernière page sans numéro, logo Wikipédia en bas à droite (1.13.0) ; le logo Wikipedia2Book sur la couverture et la dernière page, ajouté en 1.13.0, est retiré à la demande.

## 3. Améliorations possibles

- [x] **Caractères chinois rares dans le PDF officiel de Wikisource** : signalé à Wikimédia le 18/11/2026, https://phabricator.wikimedia.org/T445303 (étiquettes Proton et All-and-every-Wikisource) ; suivre la réponse (section 18 des spécifications).

## 4. Probleme and bug 

- [x] creéer un type d'issues BUG dans github avec comme champs : platform, gravity, JSON file, text with a screenshot. (formulaire `.github/ISSUE_TEMPLATE/bug.yml`, 20/11/2026)
- [x] regarder les issues dans github et chercher la les corriger. Le 20/11/2026 : #2 (PDF d'une page renommée : redirection suivie), #3 (spécification technique numérotée à partir de 1), #4 (page web convertie : second rendu sans styles, erreur qui nomme le document) ; correctifs à publier dans une version, issues à fermer après le déploiement.
- [ ] faire une homepage épuré au site. elle doit comporter le logo, un diagramme simple sur les fonctionnalités en trois étapes étape une les différentes sources rentrent dans la machine. les sources sont des pages wikipédia des boucs wikipédia des textes des images des PDF des pages Web. l'état de l'organisation des PDF il faut reprendre un peu un logo avec les cartes que l'on déplace de haut en bas l'étape 3 c'est la génération du PDF avec quelques réglages. un gros bouton de lien pour dire créer gratuitement votre premier Pdf. un peu en dessous un lien vers la FAQ qu'il faut créer.
dans la FAQ il faut répondre aux questions combien ça coûte, est-ce que je peux garder mon PDF. peut-être toi claudz,tu as d'autres idées 
