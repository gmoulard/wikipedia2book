# Tests manuels du champ « Construire le livre »

Ce document liste tout ce que Wikipedia2Book accepte, avec pour chaque cas un exemple à essayer **dans le navigateur** et le même cas **par l'API**, le résultat attendu et la version qui l'a introduit. Il sert de recette à dérouler à la main avant une mise en production. Pour les utilisateurs, la [page d'aide](helpSearch.fr.md) explique les mêmes possibilités sans les détails techniques, dans les 12 langues de l'interface.

Le comportement de référence est décrit dans la [spécification fonctionnelle](FunctionalSpec.fr.md) (section 3.1 pour les sources) et la [spécification technique](TechnicalSpec.fr.md) (section 13.3 pour l'API).

## Comment s'en servir

- **Navigateur** : ouvrir https://wikipedia2book.toolforge.org/, coller l'exemple dans le champ de l'étape « Construire le livre », puis cliquer sur « Ajouter ». Une adresse commençant par `https://wikipedia2book.toolforge.org/?` s'ouvre telle quelle.
- **API** : ouvrir l'adresse dans le navigateur (le PDF se télécharge) ou la passer à `curl -OJ`. Les appels `POST` sont donnés en `curl`.
- **Version** : version de l'application à partir de laquelle le cas fonctionne. Vérifier la version en service avec https://wikipedia2book.toolforge.org/api/version. « À venir » : écrit sur `main`, pas encore publié.
- La colonne « Version » vaut pour le navigateur. Côté API, `GET /api/pdf/from-source` (sections 1 à 4) et le paramètre `?source=` de la page existent depuis la 1.12.0 (en production dès le 16 novembre 2026 au soir, avant de recevoir ce numéro) : avec une version plus ancienne, envoyer le livre en JSON à `POST /api/pdf` (9.3), après avoir reconnu chaque saisie avec `POST /api/sources/resolve` (9.1).
- Les exemples ont été vérifiés le 17 novembre 2026 contre les wikis réels, par le code de reconnaissance des sources ; une page renommée ou supprimée depuis peut changer le résultat.

Abréviations : **T** = https://wikipedia2book.toolforge.org. Dans les adresses d'API, `language` est la langue des titres générés dans le PDF (couverture, table des matières, licence) et `wiki` la langue des titres sans préfixe.

## 1. Une page seule

| N° | Cas | Navigateur : à saisir | API | Résultat attendu | Version |
|---|---|---|---|---|---|
| 1.1 | URL d'un article Wikipédia | `https://fr.wikipedia.org/wiki/Épaves_de_la_rade_de_Saint-Pierre` | `T/api/pdf/from-source?source=https://fr.wikipedia.org/wiki/%C3%89paves_de_la_rade_de_Saint-Pierre` | L'article est ajouté ; introduction et auteur proposés au premier article | ≤ 1.9.7 |
| 1.2 | Titre exact | `Montagne Pelée` (langue FR à côté du champ) | `T/api/pdf/from-source?source=Montagne%20Pel%C3%A9e&wiki=fr` | L'article « Montagne Pelée » est ajouté | ≤ 1.9.7 |
| 1.3 | Titre redirigé | `Napoléon Bonaparte` | `T/api/pdf/from-source?source=Napol%C3%A9on%20Bonaparte&wiki=fr` | La redirection est suivie : « Napoléon Ier » est ajouté | ≤ 1.9.7 |
| 1.4 | Titre sans page exacte | `volcan martinique` | `T/api/sources/resolve` en `POST` (voir 9.1) : `kind` = `search` | Des résultats de recherche s'affichent sous le champ, à ajouter d'un clic ; l'API de génération répond 404 avec le texte en cause | ≤ 1.9.7 |
| 1.5 | Recherche au fil de la frappe | Taper `Saint-Pie` sans valider | `T/api/search?query=Saint-Pie&language=fr` | Suggestions sous le champ | ≤ 1.9.7 |
| 1.6 | Titre dans une autre langue | `nl:Rotterdam` | `T/api/pdf/from-source?source=nl:Rotterdam` | L'article néerlandais est ajouté, marqué « NL » | 1.7.0 |
| 1.7 | Toutes les langues | `Paris`, avec « Toutes » choisi à côté du champ | `T/api/search?query=Paris&language=all&limit=3` | Des résultats dans chaque langue de la liste, chacun marqué de sa langue ; l'article choisi garde la sienne | 1.12.4 |

## 2. Autres projets Wikimédia

| N° | Cas | Navigateur : à saisir | API | Résultat attendu | Version |
|---|---|---|---|---|---|
| 2.1 | Page de Wikivoyage | `https://fr.wikivoyage.org/wiki/Lyon` | `T/api/pdf/from-source?source=https://fr.wikivoyage.org/wiki/Lyon` | Page ajoutée, carte marquée « Wikivoyage » | 1.8.0 |
| 2.2 | Préfixe de projet et de langue | `[[voy:en:Lyon]]` | `T/api/pdf/from-source?source=voy:en:Lyon` | Page anglaise de Wikivoyage ajoutée | 1.8.0 |
| 2.3 | Wikiversité | `https://fr.wikiversity.org/wiki/Python` | `T/api/pdf/from-source?source=v:Python&wiki=fr` | Page ajoutée, marquée « Wikiversité » | 1.8.0 |
| 2.4 | Wikiquote | `https://fr.wikiquote.org/wiki/Victor_Hugo` | `T/api/pdf/from-source?source=q:Victor%20Hugo&wiki=fr` | Page ajoutée, marquée « Wikiquote » | 1.8.0 |
| 2.5 | Wiktionnaire, préfixes dans l'autre ordre | `fr:wikt:chat` | `T/api/pdf/from-source?source=fr:wikt:chat` | Page ajoutée, marquée « Wiktionnaire » | 1.8.0 |
| 2.6 | Wikinews | `https://fr.wikinews.org/wiki/Accueil` | `T/api/pdf/from-source?source=https://fr.wikinews.org/wiki/Accueil` | Page ajoutée, marquée « Wikinews » | 1.8.0 |
| 2.7 | Texte de Wikisource (une page) | `https://zh.wikisource.org/wiki/論語/學而第一` | `T/api/pdf/from-source?source=https://zh.wikisource.org/wiki/%E8%AB%96%E8%AA%9E/%E5%AD%B8%E8%80%8C%E7%AC%AC%E4%B8%80` | Page ajoutée ; titres en chinois lisibles dans le PDF | 1.7.8 |
| 2.8 | Page d'auteur de Wikisource | `https://fr.wikisource.org/wiki/Auteur:François_Rabelais` | `T/api/pdf/from-source?source=https://fr.wikisource.org/wiki/Auteur:Fran%C3%A7ois_Rabelais` | Page ajoutée telle quelle (biographie et liste des œuvres) | 1.8.1 |

## 3. Livres

| N° | Cas | Navigateur : à saisir | API | Résultat attendu | Version |
|---|---|---|---|---|---|
| 3.1 | Page de livre Wikipédia par URL | `https://fr.wikipedia.org/wiki/Utilisateur:Alexbzh972/Livres/Martinique` | `T/api/books/generate-from-wikipedia-book?url=https://fr.wikipedia.org/wiki/Utilisateur:Alexbzh972/Livres/Martinique` | 113 articles dans l'ordre de la page, chapitres `;`, sous-titre `===` ; titre « Martinique » | 1.3.0 |
| 3.2 | Page de livre par son nom | `Utilisateur:Alexbzh972/Livres/Martinique` | `T/api/pdf/from-source?source=Utilisateur:Alexbzh972/Livres/Martinique` | Même résultat que 3.1 | 1.3.0 |
| 3.3 | Sommaire d'un livre de Wikilivres | `https://fr.wikibooks.org/wiki/Cosmologie` | `T/api/pdf/from-source?source=b:Cosmologie&wiki=fr` | Fenêtre « Le livre entier / Le livre entier et son sommaire / Seulement cette page / Annuler » ; « Le livre entier » donne 27 pages en chapitres | 1.10.0 |
| 3.4 | Livre entier et son sommaire | Comme 3.3, choisir « Le livre entier et son sommaire » | `T/api/pdf/from-source?source=b:Cosmologie&wiki=fr&summary=1` | Le sommaire en premier, avant le premier chapitre | 1.10.0 |
| 3.5 | Seulement la page de sommaire | Comme 3.3, choisir « Seulement cette page » | `POST /api/pdf` avec la seule page de sommaire (voir 9.3) | La page de sommaire seule | 1.10.0 |
| 3.6 | Œuvre de Wikisource | `s:Les Misérables` (langue FR) | `T/api/pdf/from-source?source=s:Les%20Mis%C3%A9rables&wiki=fr` | Fenêtre de choix ; « Le livre entier » donne 365 chapitres en 5 parties, sans « Texte entier » | 1.11.0 |
| 3.7 | Version imprimable écrite à la main (adresse) | `https://fr.wikibooks.org/wiki/Hélices_de_navires_à_déplacement/Version_imprimable` | `T/api/pdf/from-source?source=https://fr.wikibooks.org/wiki/H%C3%A9lices_de_navires_%C3%A0_d%C3%A9placement/Version_imprimable` | 13 pages, un chapitre par titre `= … =`, couverture écartée, titre « Hélices de navires à déplacement » | 1.12.0 |
| 3.8 | Version imprimable par `{{imprimable}}` (adresse) | `https://fr.wikibooks.org/wiki/Programmation_C/Version_imprimable` | `T/api/pdf/from-source?source=https://fr.wikibooks.org/wiki/Programmation_C/Version_imprimable` | La fenêtre de choix du sommaire « Programmation C » (21 pages) | 1.12.0 |
| 3.9 | Compilation de Wikilivres | `https://fr.wikibooks.org/wiki/Wikilivres:Compilations/Programmation_C` | `T/api/pdf/from-source?source=https://fr.wikibooks.org/wiki/Wikilivres:Compilations/Programmation_C` | Les pages de la compilation dans l'ordre de la liste, titre « Programmation C » ; une discussion (`Wikilivres:Le_Bistro`) reste refusée (422) | 1.13.0 |

## 4. Listes de pages (plusieurs lignes)

Coller toutes les lignes d'un coup dans le champ (ou les séparer par Maj+Entrée). Côté API, répéter `source=` (50 au plus).

| N° | Cas | Ligne à saisir | Résultat attendu | Version |
|---|---|---|---|---|
| 4.1 | Lien wiki | `[[Brest]]` | « Brest » ajouté | 1.7.0 |
| 4.2 | Lien wiki avec langue | `[[nl:Amsterdam]]` | Article néerlandais ajouté | 1.7.0 |
| 4.3 | Lien wiki avec libellé | `[[Frégate (bateau)\|Frégate]]` | « Frégate (bateau) » ajouté | 1.7.0 |
| 4.4 | Lien Markdown, parenthèses dans l'URL | `[Suchet](https://fr.wikipedia.org/wiki/Suchet_(navire))` | « Suchet (navire) » ajouté | 1.7.0 |
| 4.5 | Numéro en début de ligne | `1. Lorient` | « Lorient » ajouté | 1.7.0 |
| 4.6 | Puce en début de ligne | `* Concarneau` (aussi `-`, `•`, `#`) | « Concarneau » ajouté | 1.7.0 |
| 4.7 | Ligne introuvable | `Xyzzy inexistant` | La ligne reste dans le champ, le message final la compte « introuvable » | 1.7.0 |
| 4.8 | Sommaire dans une liste | `b:Programmation Python` | La fenêtre de choix s'ouvre pour ce sommaire ; ses chapitres ne sont pas repris | 1.10.0 |

Liste complète à coller dans le navigateur :

```
[[Brest]]
[[nl:Amsterdam]]
[Suchet](https://fr.wikipedia.org/wiki/Suchet_(navire))
1. Lorient
* Concarneau
[[voy:en:Lyon]]
fr:wikt:chat
```

Résultat attendu : « 7 page(s) ajoutée(s), 0 déjà dans le livre, 0 introuvable(s) ».

API, même liste : `T/api/pdf/from-source?source=[[Brest]]&source=[[nl:Amsterdam]]&source=1.%20Lorient&source=*%20Concarneau&source=[[voy:en:Lyon]]&source=fr:wikt:chat&wiki=fr`

## 5. Texte de livre collé

| N° | Cas | Texte à coller | API | Résultat attendu | Version |
|---|---|---|---|---|---|
| 5.1 | Syntaxe « Livre: » de Wikipédia | Bloc 5.1 ci-dessous | `curl` 5.1 ci-dessous | Titre « Ports bretons », sous-titre « Guide des ports », chapitres « Finistère » et « Morbihan », « Brest » en tête sans chapitre | 1.12.0 |
| 5.2 | Version imprimable de Wikilivres | Bloc 5.2 ci-dessous | `curl` 5.2 ci-dessous | 3 pages de Wikilivres en 3 chapitres, licence écartée | 1.12.0 |

Bloc 5.1 :

```
== Ports bretons ==
=== Guide des ports ===
:[[Brest]]
;Finistère
:[[Concarneau]]
:[[Douarnenez]]
;Morbihan
:[[Lorient]]
```

```bash
curl -OJ -X POST 'https://wikipedia2book.toolforge.org/api/pdf/from-wikitext?language=fr' \
	-H 'Content-Type: application/json' \
	--data '{"wikitext":"== Ports bretons ==\n=== Guide des ports ===\n:[[Brest]]\n;Finistère\n:[[Concarneau]]\n:[[Douarnenez]]\n;Morbihan\n:[[Lorient]]","language":"fr"}'
```

Bloc 5.2 :

```
= Le paradoxe d'Olbers =
{{:Cosmologie/Le paradoxe d'Olbers}}
= L'expansion de l'univers =
{{:Cosmologie/L'expansion de l'univers}}
= Le facteur de Hubble =
{{:Cosmologie/Le facteur de Hubble}}
{{:Licence de documentation libre GNU}}
```

```bash
curl -OJ -X POST 'https://wikipedia2book.toolforge.org/api/pdf/from-wikitext?language=fr' \
	-H 'Content-Type: application/json' \
	--data "{\"wikitext\":\"= Le paradoxe d'Olbers =\n{{:Cosmologie/Le paradoxe d'Olbers}}\n= L'expansion de l'univers =\n{{:Cosmologie/L'expansion de l'univers}}\n= Le facteur de Hubble =\n{{:Cosmologie/Le facteur de Hubble}}\n{{:Licence de documentation libre GNU}}\",\"language\":\"fr\"}"
```

Pour lire seulement la structure, sans PDF : même corps sur `POST /api/books/from-wikitext`.

## 6. Ouvrir un livre enregistré (JSON)

| N° | Cas | Navigateur | API | Résultat attendu | Version |
|---|---|---|---|---|---|
| 6.1 | Livre JSON par adresse | `T/?json=https://gmoulard.github.io/wikipedia2book/static/Wrecks-of-Saint-Pierre-harbor.json` | `T/api/pdf/from-json?url=https://gmoulard.github.io/wikipedia2book/static/Wrecks-of-Saint-Pierre-harbor.json&language=en` | Le livre s'ouvre (« Livre importé. ») avec ses images de fond et son document | 1.9.6 |
| 6.2 | Livre Wikilivres en JSON | `T/?json=https://gmoulard.github.io/wikipedia2book/static/Cosmologie.json` | `T/api/pdf/from-json?url=https://gmoulard.github.io/wikipedia2book/static/Cosmologie.json` | 27 pages en 8 chapitres | 1.9.6 |
| 6.3 | Fichier JSON local | Bouton « Ouvrir », choisir un fichier exporté par « Enregistrer » | `curl -OJ -X POST 'T/api/pdf/from-json' -H 'Content-Type: application/json' --data @livre.json` | Le livre s'ouvre / le PDF est produit | ≤ 1.9.7 (navigateur), 1.12.0 (API) |
| 6.4 | JSON puis sources en plus | `T/?json=https://gmoulard.github.io/wikipedia2book/static/Cosmologie.json&source=b:Programmation%20Python` | — | Le livre JSON s'ouvre, puis la fenêtre de choix du sommaire ajouté | 1.12.0 |
| 6.5 | Sources dans l'adresse de la page | `T/?source=https://fr.wikibooks.org/wiki/Cosmologie&source=Montagne%20Pel%C3%A9e&wiki=fr` | Voir 3.3 et 1.2 | Chaque source est ajoutée comme si elle avait été saisie, question comprise | 1.12.0 |
| 6.6 | Adresse refusée | `T/?json=http://example.com/livre.json` | `T/api/pdf/from-json?url=http://example.com/livre.json` | Message d'erreur, rien n'est importé ; l'API répond 422 « doit commencer par https:// » | 1.9.6 |

## 7. Documents et images de fond

| N° | Cas | Navigateur | API (champ du livre JSON) | Résultat attendu | Version |
|---|---|---|---|---|---|
| 7.1 | Image ou PDF depuis l'ordinateur | Étape Organisation, « Choisir un fichier + » | `uploaded_documents[]` avec `data_base64` | Document placé dans le livre comme un article, 15 Mo au plus | ≤ 1.9.7 |
| 7.2 | Document par adresse | Étape Organisation, champ d'adresse : `https://upload.wikimedia.org/wikipedia/commons/1/16/La_Pel%C3%A9e_vue_du_Carbet.jpg` | `uploaded_documents[]` avec `"url": "https://upload.wikimedia.org/…"` | Seule l'adresse est enregistrée ; le serveur télécharge l'image à chaque génération | 1.10.0 |
| 7.3 | Document par page de fichier Commons | `https://commons.wikimedia.org/wiki/File:La_Pelée_vue_du_Carbet.jpg` | `"url": "https://commons.wikimedia.org/wiki/File:La_Pel%C3%A9e_vue_du_Carbet.jpg"` | L'image (vignette de 2 000 px) est utilisée ; pour un PDF, l'original | 1.10.0 (navigateur), 1.12.0 (API) |
| 7.4 | PDF par page de fichier | `https://commons.wikimedia.org/wiki/File:Interpersonal_communication_and_coordination_in_Wikipedia_Working_Paper_30_June_2020.pdf` | Même adresse dans `uploaded_documents[].url` | Le PDF original est intégré, pages recomposées au format du livre | 1.10.0 (navigateur), 1.12.0 (API) |
| 7.5 | Image de fond de couverture | Étape Édition, « Image de fond de la couverture », fichier ou adresse (7.2 ou 7.3) | `cover_image` : `{"title": "…", "url": "…"}` ou `data_base64` | Fond de la couverture, sans déformation | 1.9.6 |
| 7.6 | Image de dernière page | Étape Édition, « Image de fond de la dernière page » | `back_image` | Page à part après la licence | 1.9.6 |
| 7.7 | Adresse inaccessible | Document `https://example.org/inexistant.png` | Même adresse | Génération arrêtée, l'adresse en cause est nommée ; 502 par l'API | 1.10.0 |
| 7.8 | Titre d'un document | Étape Organisation, champ de titre du document importé | `uploaded_documents[].title` | Le titre saisi remplace le nom du fichier dans la table des matières, les signets et la licence ; à l'import, nom du fichier sans extension | 1.13.0 |
| 7.9 | Page web | Étape Organisation, champ d'adresse : `https://www.gnu.org/licenses/agpl-3.0.html` | `uploaded_documents[]` avec `"kind": "html"` et `"url"` | Document « Page web convertie en PDF », texte et images de la page, sans scripts ; une page Wikimédia est renvoyée vers le champ Sources | 1.13.0 |

## 8. Organisation et mise en page

| N° | Cas | Navigateur | API (livre JSON envoyé à `POST /api/pdf`) | Résultat attendu | Version |
|---|---|---|---|---|---|
| 8.1 | Articles liés | Bouton « Articles liés » d'un article | `POST /api/explore` | Liens de l'article proposés, dans l'ordre de la page | ≤ 1.9.7 |
| 8.2 | Chapitres et ordre | Étape Organisation, « Créer un chapitre », glisser-déposer | `chapters`, `article_order`, `unassigned_first` | Le PDF suit l'ordre affiché | ≤ 1.9.7 |
| 8.3 | Table des matières | Étape Édition : aucune, début, fin | `table_of_contents`, `toc_position` (`start`, `end`, `before:<clé>`) | Table placée au bon endroit, liens cliquables | 1.9.6 |
| 8.4 | Format, orientation, marges | Étape Édition | `page_format`, `orientation`, `margin_*_mm`, `custom_width_mm` | Toutes les pages au format choisi | ≤ 1.9.7 |
| 8.5 | Numérotation | « Numéroter les pages » | `page_numbers` | Numéros en bas de page, sauf la couverture | ≤ 1.9.7 |
| 8.6 | Langue des titres du PDF | Sélecteur de langue en haut | Paramètre `language` (12 langues) | Couverture, table, licence dans la langue choisie | ≤ 1.9.7 |
| 8.7 | Coupure de volume manuelle | Étape Organisation, « Nouveau volume » | `volume_breaks` : `["before:<clé>"]`, puis `?volume=N` | Un PDF par volume, numérotation repartant de 1 | 1.9.2 (navigateur), 1.12.0 (API) |
| 8.8 | Plus de 300 articles | Livre 3.1 + d'autres pages jusqu'à plus de 300 | `POST /api/books/volumes` pour le plan, puis `POST /api/pdf?volume=1`, `?volume=2`… | Découpage automatique entre chapitres, « Tome 1/2 »… ; sans `volume`, refus 413 avec le nombre de volumes | 1.9.0 (navigateur), 1.12.0 (API) |

## 9. Appels d'API sans PDF

| N° | Cas | Appel | Résultat attendu |
|---|---|---|---|
| 9.1 | Reconnaître une saisie | `curl -X POST 'T/api/sources/resolve' -H 'Content-Type: application/json' --data '{"input":"volcan martinique","language":"fr"}'` | `kind` : `article`, `book`, `subpages` ou `search` |
| 9.2 | Structure d'une page de livre | `curl -X POST 'T/api/books/structure' -H 'Content-Type: application/json' --data '{"url":"https://fr.wikipedia.org/wiki/Utilisateur:Alexbzh972/Livres/Martinique"}'` | Articles, sous-titre, chapitres |
| 9.3 | PDF d'un livre décrit en JSON | `curl -OJ -X POST 'T/api/pdf?language=fr' -H 'Content-Type: application/json' --data '{"name":"Test","main_articles":[{"title":"Cosmologie","language":"fr","site":"wikibooks","url":"https://fr.wikibooks.org/wiki/Cosmologie","selected":true}]}'` | PDF d'une seule page de sommaire |
| 9.4 | Suivre la génération | Même corps sur `POST /api/pdf/stream` | Lignes NDJSON `progress`, `wait`, puis `done` et le PDF |
| 9.5 | Introduction et auteur proposés | `T/api/articles/intro?title=Montagne%20Pel%C3%A9e&language=fr` | Premier paragraphe et créateur de la page |
| 9.6 | Version en service | `T/api/version` | Version, commit, limite d'articles |

## 10. Saisies refusées

Les messages d'erreur viennent du serveur et restent en français, quelle que soit la langue de l'interface.

| N° | Saisie | Résultat attendu |
|---|---|---|
| 10.1 | `https://example.com/wiki/Chat` | « L'URL doit pointer vers une page HTTPS d'un projet Wikimédia… » ; 422 |
| 10.2 | `https://fr.wikibooks.org/wiki/Wikilivres:Le_Bistro` | « Seules les pages de contenu de fr.wikibooks.org… » ; 422 |
| 10.3 | `https://commons.wikimedia.org/wiki/File:La_Pelée_vue_du_Carbet.jpg` dans le champ Sources | Refusée comme source (Commons n'a pas d'adresse `<langue>.<projet>.org`) ; acceptée comme document ou image de fond (7.3) |
| 10.4 | `https://fr.wikipedia.org/wiki/Page_qui_n_existe_pas` | « La page … est introuvable » ; 404 |
| 10.5 | Champ vide | « Saisissez … » ; 422 |
| 10.6 | Livre sans aucun article sélectionné, puis « Générer le PDF » | Message « Sélectionnez au moins un article » ; 400 |
