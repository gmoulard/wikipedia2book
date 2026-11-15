# À faire

État au 15/11/2026. Production Toolforge : **1.7.1** (`production-toolforge` = `d25ebfb`). `main` : 1.7.3 publiée, 1.7.4 prête mais pas encore committée.

## 1. Actions à faire soi-même (bloquées dans les sessions cloud)

- [ ] **Committer la 1.7.4** à l'auteur `gmoulard` : les fichiers sont indexés, mais la protection de confidentialité de la session refuse d'écrire l'adresse e-mail. Ensuite, poser le tag `v1.7.4` et pousser sur `main` (skill `release`).
- [ ] **Pousser les tags** refusés par le proxy des sessions cloud (« Tag check » les vérifie à l'arrivée) :
  ```bash
  git fetch origin
  git tag -a v1.7.2 f086224 -m "Wikipedia2Book 1.7.2" && git push origin v1.7.2
  git tag -a v1.7.3 a281689 -m "Wikipedia2Book 1.7.3" && git push origin v1.7.3
  # puis v1.7.4 sur son commit, une fois créé
  ```
- [ ] **Supprimer la branche `stats`**, devenue inutile (les statistiques sont sur `main`) : GitHub, Code → Branches, ou `git push origin --delete stats`.

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
