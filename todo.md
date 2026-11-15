# À faire

État au 15/11/2026. Production Toolforge : **1.7.1** (`production-toolforge` = `d25ebfb`). `main` : **1.7.4** (`a8144df`).

## 1. Actions à faire soi-même (bloquées dans les sessions cloud)

- [ ] **Convention d'auteur** : le commit 1.7.4 (`a8144df`) est à l'identité de la session, pas à `gmoulard`, car la protection de confidentialité refuse d'écrire l'adresse e-mail. Pour les prochaines versions en session cloud : lancer soi-même le `git commit --author=…` avec `!`, ou accepter l'identité de la session.
- [ ] **Pousser les tags** refusés par le proxy des sessions cloud (« Tag check » les vérifie à l'arrivée) :
  ```bash
  git fetch origin
  git tag -a v1.7.2 f086224 -m "Wikipedia2Book 1.7.2" && git push origin v1.7.2
  git tag -a v1.7.3 a281689 -m "Wikipedia2Book 1.7.3" && git push origin v1.7.3
  git tag -a v1.7.4 a8144df -m "Wikipedia2Book 1.7.4" && git push origin v1.7.4
  ```
- [ ] **Supprimer la branche `stats`**, devenue inutile (les statistiques sont sur `main`) : GitHub, Code → Branches, ou `git push origin --delete stats`.

## 1 bis. Autorisations manquantes dans l'environnement Claude Code cloud (« W2B »)

À régler dans les paramètres de l'environnement : menu de l'environnement cloud dans la barre de titre de la session, puis Edit, puis Network access (doc : https://code.claude.com/docs/en/cloud-environments#network-access). Ajouter les domaines sous « Allowed domains » en laissant cochée la case des gestionnaires de paquets.

- [ ] **Domaines refusés pendant les sessions** :
  - `wikitech.wikimedia.org` et `foundation.wikimedia.org` : relire la politique robots et la politique User-Agent de Wikimédia ;
  - `www.mediawiki.org` : documentation de mediawiki2latex (section 5) ;
  - `toolviews.toolforge.org` : vérifier les réponses de l'API Toolviews ;
  - `wikipedia2book.toolforge.org` : vérifier la production (`/api/version`, `/api/stats/hourly`) après un déploiement ;
  - `wikipedia2book-production.up.railway.app` : site Railway, pour le skill `debug-frontend` et les vérifications ;
  - `gmoulard.github.io` : voir le site de documentation et `stats.html` publiés ;
  - `cdn.jsdelivr.net` : charger Mermaid comme le fait le site (aujourd'hui contourné en installant Mermaid depuis npm).
- [ ] **Git** : le proxy de la session ne laisse pousser que `main` et la branche de travail de la session. Les **tags** et la **suppression de branche** sont refusés (HTTP 403). Pas de réglage connu côté environnement : continuer à pousser les tags depuis sa machine.
- [ ] **Confidentialité** : la session refuse d'écrire l'adresse e-mail de l'auteur (commits de version à `gmoulard <…>`). Option : définir soi-même `GIT_AUTHOR_NAME`/`GIT_AUTHOR_EMAIL` comme variables d'environnement de l'environnement « W2B » (valeurs non secrètes), pour que les commits de version aient le bon auteur sans que Claude écrive l'adresse.
- [ ] **Connecteur GitHub du plugin** (`plugin:github:github`) : il échoue à la connexion (« Proxy refused to open a tunnel: 403 »). Les outils GitHub intégrés suffisent ; reconnecter GitHub sur https://claude.ai/connect-github si un outil manque.
- Hors réglages (pour mémoire) : le service PDF de Wikimédia répond HTTP 429 à presque toutes les requêtes venant des sessions cloud. Ce n'est pas une autorisation à ajouter ; l'atelier de performance tourne pour cela sur GitHub Actions.

## 2. Mise en production

- [ ] **Déployer sur Toolforge** (skill `deploy-production`, seulement sur demande). Toolforge est en 1.7.1 et n'a pas encore :
  - 1.7.2 : compteur horaire et `GET /api/stats/hourly`. Sans lui, la page de statistiques affiche « heures en direct indisponibles » ;
  - 1.7.3 : nouvelles tentatives sur les refus 429/503 de Wikimédia ;
  - 1.7.4 : politique robots de Wikimédia (2 téléchargements simultanés, 25 Mbit/s) et User-Agent conforme ;
  - les scripts de déploiement déplacés dans `scripts/`, et le relevé horaire d'avant redémarrage. Ces deux points n'ont jamais été exécutés en conditions réelles.
- [ ] **Avant ce déploiement : jouer l'atelier de performance** (workflow « Performance check », niveau `min`).
- [ ] **Après ce déploiement : vérifier** `https://wikipedia2book.toolforge.org/api/version` (1.7.4), `/api/stats/hourly`, et la ligne « en direct » sous le graphique horaire de `stats.html`.

## 3. Décisions en attente

- [ ] **Recalibrer l'atelier de performance.** Relancé sur le même code, « 200 pages » est sorti en « à surveiller » (+41 %) : c'est la variabilité des machines GitHub. Proposition :
  - seuils : « à surveiller » au-delà de +50 %, « régression » au-delà de +100 % ;
  - référence : médiane de 9 générations, soit 3 lancements `min`.
- [ ] **Refaire la référence de performance après la 1.7.4** : avec 2 téléchargements au lieu de 4, la phase Wikipédia sera plus longue (le verdict, calculé sur le temps de l'application, ne devrait pas bouger).
- [ ] **Relire les politiques Wikimédia**, que je n'ai pas pu lire depuis les sessions cloud (`wikitech.wikimedia.org` et `foundation.wikimedia.org` non autorisés) :
  - https://wikitech.wikimedia.org/wiki/Robot_policy : les règles de l'API MediaWiki (recherche, liens, introduction), auxquelles le plafond de 2 n'est pas appliqué aujourd'hui ;
  - le service PDF (`/api/rest_v1/page/pdf/…`) relève-t-il bien des « Media API rules » ? Le plafond lui est appliqué par prudence ;
  - https://foundation.wikimedia.org/wiki/Policy:Wikimedia_Foundation_User-Agent_Policy : le contact actuel est fait d'URL (Toolforge, GitHub), sans adresse e-mail. Est-ce suffisant ?

## 4. Améliorations possibles

- [ ] **Signaler l'attente dans la fenêtre de statut** pendant les pauses dues aux refus 429/503 : aujourd'hui, l'étape de téléchargement reste affichée sans explication.
- [ ] **Limite par déploiement** : le plafond de 2 téléchargements vaut pour un processus. Toolforge, Railway et Northflank ont donc chacun le leur.
- [ ] **Mermaid 11.17.2** : un graphique dessiné après un `await` reste en texte, sans erreur. Contourné dans `docs/_includes/head-custom.html` (rendu d'abord, mise à jour ensuite), mais la cause n'est pas comprise.
- [ ] **GitHub Actions** : avertissement « Node.js 20 is deprecated » sur `actions/checkout@v4`, `actions/setup-python@v5`, `actions/upload-artifact@v4`, `actions/configure-pages@v5`. Passer aux versions majeures suivantes.
- [ ] **GitHub Pages** publie aussi les fichiers bruts (`SPECIFICATIONS.*.md`, `stats.md`, `index.md`, `toolviews.csv`) à côté des pages HTML. C'est sans gravité ; les exclure si on le souhaite.
- [ ] **Toolviews** ne compte plus les visiteurs distincts (compteur inactif pour tous les outils Toolforge) : à réintégrer s'il est rétabli.
- [ ] **Pluralisation** des chaînes avec compteur (« 1 Seiten » en allemand) : limitation connue, acceptée.
- [ ] **Évolutions déjà listées en section 18 des spécifications** : limitation préventive du débit vers l'API Wikipédia, journalisation structurée des erreurs, quotas sur la taille des PDF téléchargés, couverture de tests plus large (rendu WeasyPrint réel).

## 5. Fonctionnalités manquantes par rapport à mediawiki2latex

Première liste, dressée de mémoire : la documentation de mediawiki2latex n'était pas accessible depuis la session cloud.

- [ ] **Compléter et vérifier cette liste** contre la documentation réelle de mediawiki2latex (page MediaWiki de l'outil, options de l'interface web et de la ligne de commande). Confirmer ou retirer les points marqués « incertain », puis décider pour chaque écart : à faire, hors principe, ou sans objet.
- Compatibles avec le principe « PDF officiel conservé » :
  - [ ] Liste des **contributeurs** de chaque article sur la page de licence (API MediaWiki `prop=contributors`).
  - [ ] Page de **crédits des images** : images de chaque article (`prop=images`), auteur et licence (`prop=imageinfo&iiprop=extmetadata`).
  - [ ] **Autres wikis Wikimédia** (Wikibooks, Wikiversité…), s'ils exposent le même service PDF (à vérifier).
  - [ ] **Liste des figures** (incertain : dépend de ce qu'on peut extraire des PDF ou de l'API).
  - [ ] **Renvois internes** : un lien vers un autre article du livre renverrait à sa page plutôt qu'au web (incertain chez mediawiki2latex ; faisable sur le modèle des liens de la table des matières).
- Contraires au principe actuel (il faudrait reconstruire le contenu) : à ne faire que si l'on change de principe.
  - [ ] Autres **formats de sortie** : EPUB, ODT, sources LaTeX.
  - [ ] **Mise en page homogène** : une seule typographie, coupure des mots, formats natifs (A5, B5…) au lieu d'une mise à l'échelle.
  - [ ] **Qualité des images réglable** (résolution, compression, SVG vectoriels).
  - [ ] **Formules mathématiques** composées par LaTeX.
  - [ ] **Choix de l'expansion des modèles** (de mémoire).
- [ ] Ces ajouts feraient de nouveaux appels à l'API MediaWiki : relire d'abord les règles de la politique robots qui s'y appliquent (section 3).
