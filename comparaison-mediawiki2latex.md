# Wikipedia2Book et mediawiki2latex : comparaison

État au 15/11/2026.

- **Wikipedia2Book 1.7.5** : version de `main` (`app/version.py`), décrite par `docs/SPECIFICATIONS.fr.md`.
- **mediawiki2latex** : version du service web `mediawiki2latex.wmcloud.org` et du manuel de l'auteur (Dirk Hünniger, page Wikibooks modifiée en dernier le 9 juillet 2025). Le service n'affiche pas de numéro de version. La dernière version publiée sur Hackage est la 7.33 (janvier 2019) ; Debian sid propose un paquet 8.7, non vérifié ici (site Debian injoignable).

## 1. Principe

| | Wikipedia2Book | mediawiki2latex |
|---|---|---|
| Approche | Assemble les **PDF officiels de Wikipédia** (`/api/rest_v1/page/pdf/…`) sans en reconstruire le contenu, et y ajoute couverture, table des matières, chapitres, licence et conclusion | **Reconvertit** le wikitexte ou le HTML de MediaWiki en LaTeX, puis compile ce LaTeX |
| Fidélité au rendu Wikipédia | Exacte : texte, images et références sont ceux du PDF de Wikipédia | Recomposé : rendu LaTeX homogène, mais les modèles (templates) inconnus sont mal ou pas rendus |
| Typographie | Celle de chaque PDF Wikipédia, plus celle des pages générées par WeasyPrint | Une seule typographie LaTeX pour tout le livre, avec coupure des mots |
| Technologie | Python (FastAPI, WeasyPrint, pypdf, reportlab), interface JavaScript sans framework | Haskell, TeX Live, ImageMagick, LibreOffice, calibre, Chromium |
| Licence du logiciel | AGPL-3.0 | GPL |

## 2. Sources acceptées

| | Wikipedia2Book | mediawiki2latex |
|---|---|---|
| Article seul | Oui (URL, titre, ou recherche avec propositions au fil de la frappe) | Oui (URL) |
| Page de livre Wikipédia (`Livre:`, `Utilisateur:…/Livres/…`) | Oui : ordre de la page conservé, chapitres `;`, sous-titre `===` | Oui (modes « Book / Collection » et « Book Contents Page ») |
| Liste libre de pages (une par ligne, `[[…]]`, Markdown, `nl:Titre`) | Oui, multilingue dans un même livre | Non |
| Exploration des articles liés | Oui : liens d'un article dans l'ordre de la page, ajout à la main | Indirecte : le mode « Book / Collection » suit tous les liens de la première page, sur un niveau, sans choix |
| Autres wikis (Wikibooks, Wikiversité, wikis MediaWiki hors Wikimédia) | Non : Wikipédia seulement | Oui, tout wiki en wikitexte |
| Documents personnels (images, PDF) | Oui, jusqu'à 15 Mo par fichier, organisés comme des articles | Non |
| Version précise d'un article (`oldid`) | Non : toujours la version actuelle | Non documenté |

## 3. Organisation du livre

| | Wikipedia2Book | mediawiki2latex |
|---|---|---|
| Ordre des articles et chapitres | Glisser-déposer dans l'interface | Défini uniquement par la page de livre source |
| Position de la table des matières | Au choix (début, fin, avant n'importe quel élément), ou retirée | Fixe, celle du gabarit LaTeX |
| Couverture, introduction, conclusion | Oui, saisies dans l'interface (introduction et auteur proposés d'après le premier article) | Non |
| Sauvegarde et reprise d'un livre | Export puis import d'un fichier JSON | Non : chaque conversion repart de la page source |

## 4. Mise en page

| | Wikipedia2Book | mediawiki2latex |
|---|---|---|
| Formats de papier | A0 à A6, Letter, Legal, personnalisé (mm) | A4, A5, B5, Letter, Legal, Executive |
| Orientation | Portrait ou paysage | Pas de choix proposé |
| Marges | 4 préréglages ou réglage au millimètre, marge de reliure | Celles du gabarit LaTeX (modifiables en local) |
| Adaptation au format | Pages Wikipédia mises à l'échelle et centrées ; natives en A4, Letter et Legal | Composition native dans le format choisi |
| Numérotation des pages | Oui, continue sur tout le livre, désactivable | Oui (LaTeX) |
| Tableaux | Ceux du PDF Wikipédia | Composés par Chromium ou par LaTeX, au choix |
| Images | Celles du PDF Wikipédia | Résolution plafonnée (300 dpi par défaut, réglable en ligne de commande), SVG rastérisés ou gardés vectoriels |
| Formules mathématiques | Celles du PDF Wikipédia | Composées par LaTeX |

## 5. Navigation, licences et crédits

| | Wikipedia2Book | mediawiki2latex |
|---|---|---|
| Signets PDF | Couverture, table des matières, chapitres, articles, licence, conclusion | Ceux produits par LaTeX (sections) |
| Liens de la table des matières | Liens internes cliquables | Oui (LaTeX) |
| Renvois entre articles du livre | Non : les liens des articles pointent vers le web | Non documenté |
| Page de licence | Oui : CC BY-SA 4.0, URL et historique de chaque article, traduite dans la langue de l'interface | Contributeurs de chaque article |
| Crédits des images | Ceux imprimés par Wikipédia dans chaque PDF | Liste des figures en annexe, avec auteur et licence lus sur la page de chaque fichier (modèle `Information`) |

## 6. Formats de sortie

| | Wikipedia2Book | mediawiki2latex |
|---|---|---|
| PDF | Oui | Oui |
| Sources LaTeX (zip) | Non | Oui |
| EPUB | Non | Oui (EPUB2) |
| ODT (traitement de texte) | Non | Oui |

## 7. Utilisation

| | Wikipedia2Book | mediawiki2latex |
|---|---|---|
| Service en ligne | `wikipedia2book.toolforge.org` (Toolforge), aussi Railway et Northflank | `mediawiki2latex.wmcloud.org` (Wikimedia Cloud VPS) |
| Interface | Application en 3 étapes (Sources, Organisation, Édition), 12 langues dont l'arabe et le persan en écriture de droite à gauche, thème clair et sombre, smartphone | Formulaire unique en anglais : URL, format de sortie, expansion des modèles, papier, tableaux, graphiques vectoriels |
| Durée d'une génération | Le temps de télécharger les PDF Wikipédia et de les assembler, avec une fenêtre de progression étape par étape | Environ une minute pour un article (LaTeX compilé plusieurs fois), plusieurs heures pour un gros livre |
| Limites du service | Au plus 200 articles par page de livre ; pas de limite de durée | 4 heures (environ 2 000 pages) et 4 conversions simultanées ; un service « gros livres » à 12 heures (environ 8 000 pages) ; « Not enough resources » si tout est occupé |
| Installation locale | Docker | Paquet Debian/Ubuntu, binaires Linux et Windows ; pas de limite de durée |
| Ligne de commande ou API | API HTTP (`/api/pdf`, `/api/books/generate`, `/api/books/generate-from-wikipedia-book`…) | Ligne de commande complète (`-u`, `-o`, `-p`, `-r`, `-g`, `-b`, `-d`, `-z`…) et mode serveur (`-s`) |
| Personnalisation avancée | Non | Fichiers de correspondance des modèles, en-têtes LaTeX personnalisés, copie de l'arbre LaTeX pour le retoucher |
| Données conservées par le serveur | Aucune (le livre reste dans le navigateur) | Fichiers de conversion côté serveur, non documenté |

## 8. En résumé

- **Wikipedia2Book** est plus rapide et plus fidèle au rendu de Wikipédia, et donne plus de contrôle sur la composition du livre : choix des articles, ordre, chapitres, couverture, documents personnels, format et marges, interface traduite. Il ne produit que du PDF, ne sait pas lire d'autres wikis et ne reprend pas les crédits des images.
- **mediawiki2latex** produit un livre typographiquement homogène, dans plusieurs formats (PDF, LaTeX, EPUB, ODT), à partir de n'importe quel wiki MediaWiki, avec la liste des figures et de leurs auteurs. Il est en revanche lent, dépend de la bonne conversion des modèles, et ne permet pas d'organiser le livre en dehors de la page source.

Les écarts que Wikipedia2Book pourrait combler sans renoncer au PDF officiel sont suivis en section 5 de `todo.md`.

## Sources

- [Manuel de mediawiki2latex (Wikibooks, Dirk Hünniger)](https://de.wikibooks.org/wiki/Benutzer:Dirk_Huenniger/wb2pdf/manual)
- [Service web mediawiki2latex](https://mediawiki2latex.wmcloud.org/)
- [mediawiki2latex sur Hackage](https://hackage.haskell.org/package/mediawiki2latex)
- [PDF export (mediawiki.org)](https://www.mediawiki.org/wiki/PDF_export)
- `docs/SPECIFICATIONS.fr.md` (Wikipedia2Book 1.7.5)
