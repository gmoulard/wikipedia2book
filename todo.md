# À faire

État au 15/11/2026. Production Toolforge : **1.7.5** (`1c249d3`). `main` : **1.7.9**, tags `v1.7.2` à `v1.7.9` poussés.

Une action réalisée est retirée de cette liste (pas cochée) : l'historique Git garde la trace de ce qui a été fait.

## 1. Actions à faire soi-même (bloquées dans les sessions cloud)

- [ ] **Convention d'auteur** : le commit 1.7.4 (`a8144df`) est à l'identité de la session, pas à `gmoulard`, car la protection de confidentialité refuse d'écrire l'adresse e-mail. Pour les prochaines versions en session cloud : lancer soi-même le `git commit --author=…` avec `!`, ou accepter l'identité de la session.

## 1 bis. Autorisations manquantes dans l'environnement Claude Code cloud (« W2B »)

À régler dans les paramètres de l'environnement : menu de l'environnement cloud dans la barre de titre de la session, puis Edit, puis Network access (doc : https://code.claude.com/docs/en/cloud-environments#network-access). Ajouter les domaines sous « Allowed domains » en laissant cochée la case des gestionnaires de paquets.

- [ ] **Git** : le proxy de la session ne laisse pousser que `main` et la branche de travail de la session. Les **tags** et la **suppression de branche** sont refusés (HTTP 403). Pas de réglage connu côté environnement : continuer à pousser les tags depuis sa machine.
- [ ] **Confidentialité** : la session refuse d'écrire l'adresse e-mail de l'auteur (commits de version à `gmoulard <…>`). Option : définir soi-même `GIT_AUTHOR_NAME`/`GIT_AUTHOR_EMAIL` comme variables d'environnement de l'environnement « W2B » (valeurs non secrètes), pour que les commits de version aient le bon auteur sans que Claude écrive l'adresse.
- [ ] **Connecteur GitHub du plugin** (`plugin:github:github`) : il échoue à la connexion (« Proxy refused to open a tunnel: 403 »). Les outils GitHub intégrés suffisent ; reconnecter GitHub sur https://claude.ai/connect-github si un outil manque.
- Hors réglages (pour mémoire) : le service PDF de Wikimédia répond HTTP 429 à presque toutes les requêtes venant des sessions cloud. Ce n'est pas une autorisation à ajouter ; l'atelier de performance tourne pour cela sur GitHub Actions.

## 2. Mise en production

- [ ] **Atelier de performance non joué** avant ce déploiement : `gh` n'est pas connecté sur le poste local, et le workflow ne se lance que depuis GitHub. À jouer au niveau `min`, puis refaire la référence (section 3).
- [ ] **Ligne « en direct » sous le graphique horaire de `stats.html`** : pas encore regardée.

## 3. Décisions en attente

- [ ] **Référence sur 9 générations** (3 lancements `min`) : reste à faire, demande de lancer le workflow sur GitHub.
- [ ] **Refaire la référence de performance après la 1.7.4** : avec 2 téléchargements au lieu de 4, la phase Wikipédia sera plus longue (le verdict, calculé sur le temps de l'application, ne devrait pas bouger).

## 4. Améliorations possibles

- [ ] **Limite par déploiement** : le plafond de 2 téléchargements vaut pour un processus. Railway et Northflank ont donc chacun le leur ; Toolforge n'en a pas.
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
