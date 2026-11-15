# À faire

État au 15/11/2026. Production Toolforge et `main` : **1.8.2**, tags `v1.7.2` à `v1.8.2` poussés.

Une action réalisée est retirée de cette liste (pas cochée) : l'historique Git garde la trace de ce qui a été fait.

## 1. Autorisations manquantes dans l'environnement Claude Code cloud (« W2B »)

À régler dans les paramètres de l'environnement : menu de l'environnement cloud dans la barre de titre de la session, puis Edit, puis Network access (doc : https://code.claude.com/docs/en/cloud-environments#network-access). Ajouter les domaines sous « Allowed domains » en laissant cochée la case des gestionnaires de paquets.

- [ ] **Git** : le proxy de la session ne laisse pousser que `main` et la branche de travail de la session. Les **tags** et la **suppression de branche** sont refusés (HTTP 403). Pas de réglage connu côté environnement : continuer à pousser les tags depuis sa machine.
- [ ] **Auteur des commits** : définir soi-même `GIT_AUTHOR_NAME`/`GIT_AUTHOR_EMAIL` (et `GIT_COMMITTER_NAME`/`GIT_COMMITTER_EMAIL`) comme variables de l'environnement « W2B » (valeurs non secrètes). C'est la règle retenue (paramètres `release` du `CLAUDE.md`) : la session refuse d'écrire l'adresse e-mail, et le commit 1.7.4 (`a8144df`) est resté à l'identité de la session.
- [ ] **Connecteur GitHub du plugin** (`plugin:github:github`) : il échoue à la connexion (« Proxy refused to open a tunnel: 403 »). Les outils GitHub intégrés suffisent ; reconnecter GitHub sur https://claude.ai/connect-github si un outil manque.
- Hors réglages (pour mémoire) : le service PDF de Wikimédia répond HTTP 429 à presque toutes les requêtes venant des sessions cloud. Ce n'est pas une autorisation à ajouter ; l'atelier de performance tourne pour cela sur GitHub Actions.

## 2. Mise en production

- [ ] **Atelier de performance non joué** depuis la 1.7.5 (assemblage sur disque en 1.7.7, fusion par qpdf en 1.7.9) : `gh` n'est pas connecté sur le poste local, et le workflow ne se lance que depuis GitHub. À jouer au niveau `min`, puis refaire la référence (section 3).
- [ ] **Test aux limites sur Toolforge en 1.7.10** (`scripts/limit_check.py --steps 300,400`, section 13.12 des spécifications) : 200 articles passent depuis la 1.7.7, 300 faisaient encore redémarrer le serveur en 1.7.9. Le jouer hors des heures d'usage : un échec fait redémarrer la production.
- [ ] **Mémoire de Toolforge à 300 articles** : cause trouvée le 15/11/2026 dans les données Grafana (https://grafana.wmcloud.org/d/TJuKfnt4z/tool-dashboard?var-namespace=tool-wikipedia2book, interface à ouvrir dans son navigateur ; données lisibles aussi par l'API de Grafana sans connexion). Le conteneur `webservice` est limité à **2 Gio de mémoire et 1 CPU** (quota de l'outil : 8 Gio), sans limite d'espace temporaire ; le pod 1.7.10 a redémarré deux fois, dernier arrêt **`OOMKilled`**. Mémoire du programme (RSS) jusqu'à 1 958 Mo en 1.7.9 et 1 338 Mo en 1.7.10, cache de fichiers sous 500 Mo : ce ne sont pas les fichiers temporaires. En local, la mesure ne donne que 262 Mo pour 300 articles, mais WeasyPrint y est remplacé par un bouchon : **suspect principal, le rendu WeasyPrint des pages générées** (table des matières et page de licence de plusieurs centaines d'entrées). À confirmer avec le mode `--stub` dans Docker (section 4), ou en suivant `https://wikipedia2book.toolforge.org/api/health/details` pendant un test aux limites.
- [ ] **Ligne « en direct » sous le graphique horaire de `stats.html`** : pas encore regardée.

## 3. Décisions en attente

- [ ] **Référence sur 9 générations** (3 lancements `min`) : reste à faire, demande de lancer le workflow sur GitHub.
- [ ] **Refaire la référence de performance après la 1.7.4** : avec 2 téléchargements au lieu de 4, la phase Wikipédia sera plus longue (le verdict, calculé sur le temps de l'application, ne devrait pas bouger).

## 4. Améliorations possibles

- [ ] **Mode `--stub` pour `scripts/limit_check.py`** : générer en local, dans le même processus, avec un faux client Wikipédia qui fabrique des PDF d'articles synthétiques (environ 1,8 Mo chacun), et mesurer la mémoire au pic, la durée et l'espace temporaire par palier. Le jouer aussi dans GitHub Actions, dans l'image Docker de production limitée en mémoire et en espace temporaire, pour trouver la limite sans télécharger depuis Wikipédia ni faire redémarrer Toolforge.
- [ ] **Limite par déploiement** : le plafond de 2 téléchargements vaut pour un processus. Northflank a donc le sien ; Toolforge n'en a pas.
- [ ] **Mermaid 11.17.2** : un graphique dessiné après un `await` reste en texte, sans erreur. Contourné dans `docs/_includes/head-custom.html` (rendu d'abord, mise à jour ensuite), mais la cause n'est pas comprise.
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
  - [ ] **Autres wikis Wikimédia** : tous les projets `<langue>.<projet>.org` sont acceptés (`SITES` dans `app/wikipedia_api.py`). Reste :
    - **Wikilivres** ★★★ : importer un livre entier depuis sa page de sommaire (sous-pages `Livre/Chapitre` dans l'ordre, avec chapitres), comme une page de livre Wikipédia.
    - Possibles mais peu utiles (domaine unique, sans langue) : Commons, Meta-Wiki, MediaWiki.org (un manuel technique, à la rigueur), Wikispecies. Sans intérêt : Wikidata.
  - [ ] **Liste des figures** (incertain : dépend de ce qu'on peut extraire des PDF ou de l'API).
  - [ ] **Renvois internes** : un lien vers un autre article du livre renverrait à sa page plutôt qu'au web (incertain chez mediawiki2latex ; faisable sur le modèle des liens de la table des matières).
- Contraires au principe actuel (il faudrait reconstruire le contenu) : à ne faire que si l'on change de principe.
  - [ ] Autres **formats de sortie** : EPUB, ODT, sources LaTeX.
  - [ ] **Mise en page homogène** : une seule typographie, coupure des mots, formats natifs (A5, B5…) au lieu d'une mise à l'échelle.
  - [ ] **Qualité des images réglable** (résolution, compression, SVG vectoriels).
  - [ ] **Formules mathématiques** composées par LaTeX.
  - [ ] **Choix de l'expansion des modèles** (de mémoire).
- [ ] Ces ajouts feraient de nouveaux appels à l'API MediaWiki : relire d'abord les règles de la politique robots qui s'y appliquent (section 3).
