# Wikipedia2Book — Spécification fonctionnelle

<table border="0" ><tr><td>
<img src="https://gmoulard.github.io/wikipedia2book/static/Wikipedia2bookLogo.png" alt="Wikipedia2Book logo" width="100"  >
</td><td>
Traduction anglaise : [FunctionalSpec.en.md](https://gmoulard.github.io/wikipedia2book/FunctionalSpec.en.html). Ce document en français fait référence. La documentation est en trois parties : spécification fonctionnelle ([FunctionalSpec.fr.md](https://gmoulard.github.io/wikipedia2book/FunctionalSpec.fr.html)), spécification technique ([TechnicalSpec.fr.md](https://gmoulard.github.io/wikipedia2book/TechnicalSpec.fr.html)) et historique des versions ([CHANGELOG.fr.md](https://gmoulard.github.io/wikipedia2book/CHANGELOG.fr.html)) ; les numéros de section sont communs aux trois (« section 13.3 » renvoie à la spécification technique). Tous les documents : [docs.md](https://gmoulard.github.io/wikipedia2book/docs.html).
</td></tr></table>

---

## Table des matières

- [1. Présentation de Wikipedia2Book](#1-pr%C3%A9sentation-de-wikipedia2book)
	- [1.1 Objectif](#11-objectif)
	- [1.2 Principes fondamentaux](#12-principes-fondamentaux)
- [2. Le livre en mémoire et sa sauvegarde](#2-le-livre-en-m%C3%A9moire-et-sa-sauvegarde)
- [3. Ajout des articles](#3-ajout-des-articles)
	- [3.1 Méthodes d'ajout](#31-m%C3%A9thodes-dajout)
	- [3.2 Informations conservées par article](#32-informations-conserv%C3%A9es-par-article)
	- [3.3 Introduction et auteur proposés automatiquement](#33-introduction-et-auteur-propos%C3%A9s-automatiquement)
- [4. Exploration des articles liés](#4-exploration-des-articles-li%C3%A9s)
	- [4.1 Principe](#41-principe)
	- [4.2 Profondeur d'exploration](#42-profondeur-dexploration)
	- [4.3 Résultats de l'exploration](#43-r%C3%A9sultats-de-lexploration)
	- [4.4 Lancer l'exploration](#44-lancer-lexploration)
- [5. Sélection des articles](#5-s%C3%A9lection-des-articles)
- [6. Organisation du livre](#6-organisation-du-livre)
	- [6.1 Documents importés (images et PDF)](#61-documents-import%C3%A9s-images-et-pdf)
- [7. Récupération du contenu Wikipédia](#7-r%C3%A9cup%C3%A9ration-du-contenu-wikip%C3%A9dia)
- [8. Références, images et licences](#8-r%C3%A9f%C3%A9rences-images-et-licences)
- [9. Paramétrage du format du livre](#9-param%C3%A9trage-du-format-du-livre)
	- [9.1 Formats standards](#91-formats-standards)
	- [9.2 Format personnalisé](#92-format-personnalis%C3%A9)
	- [9.3 Orientation](#93-orientation)
	- [9.4 Marges](#94-marges)
- [10. Mise en page du livre](#10-mise-en-page-du-livre)
	- [10.1 Format et orientation, appliqués à toutes les pages](#101-format-et-orientation-appliqu%C3%A9s-%C3%A0-toutes-les-pages)
	- [10.2 Numérotation des pages](#102-num%C3%A9rotation-des-pages)
- [11. Génération du PDF](#11-g%C3%A9n%C3%A9ration-du-pdf)
	- [11.1 Déroulement](#111-d%C3%A9roulement)
	- [11.2 Résultat](#112-r%C3%A9sultat)
	- [11.3 Gestion des erreurs](#113-gestion-des-erreurs)
- [12. Interface utilisateur](#12-interface-utilisateur)
	- [12.1 Langues de l'interface](#121-langues-de-linterface)
	- [12.2 Page d'administration](#122-page-dadministration)
- [15. Respect des licences Wikipédia](#15-respect-des-licences-wikip%C3%A9dia)
- [16. Critères d'acceptation](#16-crit%C3%A8res-dacceptation)
- [18. État d'avancement et évolutions futures](#18-%C3%A9tat-davancement-et-%C3%A9volutions-futures)

## 1\. Présentation de Wikipedia2Book

### 1.1 Objectif

Wikipedia2Book est un logiciel qui permet de créer directement un livre au format PDF imprimable à partir d'articles Wikipédia. L'utilisateur commence immédiatement à construire son livre.

Dès l'ouverture de l'application, un livre vide est prêt à l'emploi. L'utilisateur ajoute un ou plusieurs articles principaux, explore les articles qui leur sont liés, choisit précisément les contenus à intégrer, organise les articles en chapitres et génère un document PDF structuré.

Le logiciel fonctionne sur toutes les plateformes grâce à une architecture Python conteneurisée avec Docker.

### 1.2 Principes fondamentaux

* Le logiciel n'est pas limité à un thème ou à une catégorie d'articles.

* Plusieurs articles principaux peuvent être ajoutés à un même livre.

* L'exploration des liens Wikipédia part d'un article choisi par l'utilisateur (profondeur et nombre maximal d'articles réglables par l'API).

* Aucun article découvert n'est ajouté automatiquement au livre.

* L'utilisateur garde le contrôle total sur la sélection des articles.

* Le format du livre est configurable (dimensions, orientation, marges).

* Le PDF produit est adapté à l'impression.

## 2\. Le livre en mémoire et sa sauvegarde

Le logiciel gère un seul livre à la fois, construit entièrement en mémoire dans le navigateur.

* À l'ouverture de l'application, un livre vide est créé automatiquement; l'utilisateur peut lui donner un nom et une description.

* Toutes les modifications (articles, sélection, organisation, mise en page) sont conservées en mémoire dans le navigateur pendant la session, et envoyées à l'API uniquement pour les opérations qui le nécessitent (recherche, exploration, génération du PDF).

* L'utilisateur peut télécharger explicitement l'état du livre sous forme de fichier JSON, nommé d'après le titre du livre (ou, si aucun titre n'est renseigné, le titre du premier article du livre).

* L'utilisateur peut importer un fichier JSON précédemment téléchargé pour reprendre un livre; l'import remplace le livre en cours.

* Un livre peut aussi s'ouvrir depuis l'adresse d'un fichier JSON publié en ligne, en la passant dans l'adresse de la page : `https://wikipedia2book.toolforge.org/?json=<url-du-fichier>` (exemple : [https://wikipedia2book.toolforge.org/?json=https://gmoulard.github.io/wikipedia2book/static/Wrecks-of-Saint-Pierre-harbor.json](https://wikipedia2book.toolforge.org/?json=https://gmoulard.github.io/wikipedia2book/static/Wrecks-of-Saint-Pierre-harbor.json), qui ouvre le livre d'exemple *Wrecks of Saint-Pierre harbor*). C'est le navigateur qui lit le fichier (`fetchWorkspaceText` dans `app.js`), comme un import : il faut que le site qui l'héberge l'autorise (CORS), ce que font GitHub Pages et raw.githubusercontent.com ; sinon, ou si le fichier n'est pas un livre valide, un message « Import JSON impossible : … » s'affiche et la page reste sur un livre vide. Le serveur, lui, ne voit pas cette adresse.

* Un livre peut aussi se construire depuis l'adresse de la page, avec un ou plusieurs paramètres `source=` (dans l'ordre, chacun lu comme une ligne du champ : URL, titre, `b:Titre`, `fr:Titre`, page de livre), et `wiki=<langue>` pour la langue des titres sans préfixe (par défaut celle choisie à côté du champ) : par exemple `https://wikipedia2book.toolforge.org/?source=https://fr.wikibooks.org/wiki/Cosmologie`. Chaque source est ajoutée comme si elle avait été saisie dans « Construire le livre » (`addSourcesFromAddress` dans `app.js`), y compris la question pour un sommaire de Wikilivres ou de Wikisource et la recherche quand aucune page exacte ne correspond ; avec `json=` en plus, le livre JSON est ouvert d'abord, puis les sources lui sont ajoutées.

* Le serveur ne persiste aucun livre ni fichier sur son disque : la persistance est entièrement à la charge de l'utilisateur, via le téléchargement puis l'import manuel du fichier JSON. Seuls des fichiers temporaires existent le temps d'une génération de PDF (section 11.1), supprimés dès qu'elle se termine, échoue ou est abandonnée.

Le livre contient notamment :

* Les articles principaux.

* Les articles découverts.

* La sélection des articles.

* La structure du livre (ordre, chapitres, présence et position de la table des matières).

* Les paramètres de mise en page.

* Les informations de couverture (titre, sous-titre, auteur, introduction, conclusion).

Le modèle de données complet et le format du fichier JSON sont décrits en section 13.9.

## 3\. Ajout des articles

### 3.1 Méthodes d'ajout

Un seul champ de saisie, dans l'étape Sources, sert à tous les moyens d'ajout : l'utilisateur n'indique pas le type de ce qu'il saisit, le logiciel le reconnaît en interrogeant Wikipédia (`POST /api/sources/resolve`, qui reçoit `input`, `language` et `site`) :

* une URL `https://<langue>.wikipedia.org/wiki/…` est lue avec la langue de l'URL; une URL d'un autre projet Wikimédia de la forme `https://<langue>.<projet>.org/wiki/…` aussi, sur ce projet (voir plus bas); sinon, le texte saisi est pris comme un titre de page, dans la langue de Wikipédia choisie à côté du champ. Ce sélecteur propose FR, EN, DE, ES, IT, PT et NL; à l'ouverture de l'application, il est positionné sur la langue du navigateur (partie principale du code, par exemple `pt` pour `pt-BR`, `no` pour `nb`), ajoutée à la liste si elle n'y figure pas (par exemple JA). Si la langue du navigateur est absente ou n'est pas un code valide, EN est sélectionné. Ce choix n'est enregistré ni dans le livre ni dans le navigateur;

* la page est recherchée sur Wikipédia, redirections suivies : une page de l'espace principal (un article) est ajoutée comme article; une page d'un autre espace de noms (`Utilisateur:…/Livres/…`, `Livre:…`, etc.) est importée comme page de livre;

* si aucune page ne porte exactement ce titre, les résultats de la recherche Wikipédia sont proposés sous le champ, à ajouter d'un clic; une URL vers une page inexistante est signalée comme introuvable.

* **Toutes les langues** : le choix « Toutes » (« All » en anglais), à la fin du sélecteur de langue, cherche un titre dans chaque langue du sélecteur (FR, EN, DE, ES, IT, PT, NL et la langue du navigateur si elle s'y ajoute) en même temps ; les résultats sont proposés sous le champ, regroupés par langue (trois au plus par langue pendant la frappe, cinq à l'ajout), chacun avec sa langue, et l'article ajouté d'un clic garde la sienne. Avec « Toutes », un titre n'est jamais ajouté directement : il faut choisir parmi les résultats ; une URL ou un préfixe de langue (`nl:Titre`) restent prioritaires, et un contenu de page de livre collé est lu dans la langue de l'interface si elle est dans le sélecteur, sinon en anglais. Une langue qui ne répond pas n'empêche pas les autres.

* **Aide** : sous le champ, le lien « Voir l'aide : tout ce que vous pouvez saisir, avec des exemples » ouvre, dans un nouvel onglet, la page d'aide du site de documentation dans la langue de l'interface ([français](helpSearch.fr.md), [anglais](helpSearch.en.md) et les dix autres langues), qui donne un exemple de chaque saisie possible ; les messages d'erreur du serveur y restent cités en français.

* **Autres projets Wikimédia** : une page de l'espace principal, ou d'un espace propre au projet, de Wikisource (`wikisource`), Wikilivres (`wikibooks`), Wikivoyage (`wikivoyage`), Wikiversité (`wikiversity`), Wikiquote (`wikiquote`), Wiktionnaire (`wiktionary`) ou Wikinews (`wikinews`) est ajoutée comme un article, avec le PDF officiel du projet (même service que Wikipédia, section 13.2), par exemple `https://zh.wikisource.org/wiki/論語/學而第一`, `https://fr.wikibooks.org/wiki/Programmation_Python` ou `https://fr.wikivoyage.org/wiki/Lyon`. Elle est donnée par son URL ou par un titre précédé d'un préfixe interwiki de projet (voir la liste plus bas) : la page est alors cherchée sur ce projet et, s'il n'y a pas de page exacte, les résultats de la recherche de ce projet sont proposés. Les pages de livre (`Livre:`) restent propres à Wikipédia ; sur Wikilivres, un livre se reconnaît à son sommaire : une page de l'espace principal qui contient au moins 2 liens vers ses propres sous-pages (`Livre/Chapitre`, liens rouges exclus) est proposée comme un livre (`kind` = `subpages`, `MediaWikiClient.get_subpage_book`, qui lit le HTML rendu par `action=parse` pour garder l'ordre du sommaire, 500 sous-pages au plus). Une fenêtre demande alors « « Programmation Python » est le sommaire d'un livre de Wikilivres (56 pages). Que voulez-vous ajouter ? » : « Le livre entier » (les sous-pages dans l'ordre du sommaire, le titre du livre repris du sommaire), « Le livre entier et son sommaire » (le sommaire en premier, avant le premier chapitre), « Seulement cette page » (comme avant) ou « Annuler » (rien n'est ajouté, comme avec Échap). Les sections du sommaire deviennent des chapitres du livre au premier niveau de titre qui en donne au moins deux contenant des sous-pages (par exemple les `h3` « Intro », « Basics »… sous un seul `h2` « Contents » de *Python Programming*) ; les sous-pages placées avant la première section restent sans chapitre, et un sommaire à une seule section (« Sommaire ») donne un livre sans chapitre. Les sous-pages « version imprimable » (Version imprimable, Print version, Druckversion, Versione stampabile, Versión para imprimir, Versão para impressão, Afdrukbare versie…, `FULL_TEXT_PAGES`), qui contiennent tout le livre, sont ignorées ; les autres pages annexes (Livre d'or…) se retirent par « × ». Il en va de même sur Wikisource pour une œuvre découpée en sous-pages (`Œuvre/Chapitre`, par exemple 史記 : 130 rouleaux en 5 chapitres 本紀, 表, 書, 世家, 列傳 ; Les Misérables : 365 chapitres en 5 parties) : les pages qui contiennent toute l'œuvre (« Texte entier », « 全覽 », « 全文 »…, même liste `FULL_TEXT_PAGES`) sont ignorées, et une page dont des sous-pages sont déjà dans le livre n'est qu'un sommaire intermédiaire (par exemple « Les Misérables/Tome 1/Livre 1 ») : elle est écartée sur Wikisource, gardée sur Wikilivres, où un chapitre a souvent son propre texte en plus de ses sous-pages. Dans une liste de plusieurs pages, la même question est posée pour chaque sommaire, et les chapitres ne sont pas repris, comme pour une page de livre Wikipédia. Les espaces propres au projet sont ceux que MediaWiki numérote à partir de 100, hors pages de discussion (numéros impairs) : par exemple la page d'auteur `https://fr.wikisource.org/wiki/Auteur:François_Rabelais` (espace 102 en français, 106 en espagnol), `Page:…` et `Livre:…` sur Wikisource, ou `Annexe:…` sur le Wiktionnaire ; elle est ajoutée telle quelle, avec son PDF officiel (pour une page d'auteur : biographie et liste des œuvres, sans les œuvres elles-mêmes). Une page des espaces standard (`Wikilivres:…`, `Aide:…`, `Catégorie:…`, etc.) ou de discussion est refusée, sauf si elle est une liste de livre : une compilation de Wikilivres (`https://fr.wikibooks.org/wiki/Wikilivres:Compilations/Programmation_C`) ou toute page faite de lignes `: [[…]]` sans autre texte (au moins 2, et 80 % des lignes qui contiennent un lien, `wikipedia_api.is_book_listing`) est lue comme une page de livre de Wikipédia : pages dans l'ordre, chapitres `;`, titre du livre tiré du nom de la page (« Programmation C »), pages prises sur le même projet et dans la même langue. Une discussion qui cite des pages reste refusée, avec le message « Seules les pages de contenu de fr.wikibooks.org (textes, pages d'auteur…) et les compilations ou pages de livre sont acceptées. » Chaque page est ajoutée telle quelle : pour une œuvre ou un livre découpé en sous-pages (Wikisource, Wikilivres), la page principale ne contient souvent que le sommaire, et il faut ajouter chaque sous-page (on peut coller la liste de leurs URL, une par ligne). La carte de l'article indique le nom du projet, dans la langue de l'interface (par exemple « Wikilivres »), à côté de la langue. Les projets sans adresse `<langue>.<projet>.org` (Commons, Meta-Wiki, MediaWiki.org, Wikispecies, Wikidata) ne sont pas acceptés.

Le champ accepte aussi une **liste de pages, une par ligne** (collée, ou saisie avec Maj+Entrée; Entrée seule lance l'ajout). Chaque ligne est reconnue puis recherchée sur Wikipédia l'une après l'autre, avec un message « Ajout de la liste : n / total — titre » :

* les puces et numéros en début de ligne (`1.`, `2)`, `#`, `*`, `-`, `•`) sont ignorés, ainsi que les lignes vides;
* lien wiki `[[Titre]]`, `[[:fr:Titre]]` ou `[[nl:Titre|texte]]` : le titre, dans la langue indiquée par le préfixe s'il y en a un;
* lien Markdown `[texte](https://…)` : l'URL, parenthèses comprises (`…/Suchet%20(navire)`);
* préfixe de langue `nl:Titre` (2 ou 3 lettres minuscules, éventuellement suivies d'une variante, par exemple `zh-yue`) : la page de ce titre sur cette Wikipédia, ce qui permet des listes multilingues;
* préfixe interwiki de projet, seul ou combiné avec un préfixe de langue dans un ordre quelconque : `w:` Wikipédia, `s:` Wikisource, `b:` Wikilivres, `voy:` Wikivoyage, `v:` Wikiversité, `q:` Wikiquote, `wikt:` Wiktionnaire, `n:` Wikinews (par exemple `b:Programmation Python`, `[[voy:en:Lyon]]`, `fr:wikt:chat`) : la page de ce titre sur ce projet, dans la langue du préfixe ou, à défaut, celle choisie à côté du champ;
* URL Wikipédia ou d'un autre projet accepté : lue avec sa langue; titre seul : sur Wikipédia, dans la langue choisie à côté du champ.

Chaque page trouvée est ajoutée comme un article (ou, pour une page de livre, tous ses articles); une page déjà dans le livre est ignorée. Les lignes sans page exacte, ou en erreur, restent dans le champ pour être corrigées, et sont rappelées sous le champ. Un message final indique le nombre de pages ajoutées, déjà présentes et introuvables. La recherche au fil de la frappe est désactivée dès que le champ contient plusieurs lignes.

Sous le champ, un libellé court et permanent rappelle l'essentiel (« Saisissez un titre, l'adresse d'une page Wikimédia ou plusieurs pages, une par ligne. ») et renvoie, par un lien en gras, vers la page d'aide qui détaille tout ce que le champ accepte, avec des exemples. Les messages d'état (article ajouté, pages importées, aucune page exacte) s'affichent sur une ligne distincte en dessous, sans remplacer ce libellé. Pendant la saisie d'un texte qui n'est pas une URL, des résultats de recherche sont proposés au fil de la frappe, sur le projet et dans la langue des préfixes s'il y en a (`b:fr:Program…` cherche sur Wikilivres en français). Les endpoints précédents (`POST /api/articles`, `POST /api/books/structure`, `GET /api/search`) restent disponibles. Le contenu d'une page « Livre: » peut aussi y être collé (voir plus bas) ; la page d'aide en donne un exemple.

L'utilisateur ajoute ainsi des articles à son livre par l'un des moyens suivants :

* URL d'un article Wikipédia.

* Titre d'article saisi directement.

* Recherche dans Wikipédia : des résultats sont proposés au fil de la saisie, à ajouter d'un clic.

* URL d'une page de « livre » Wikipédia listant des articles : tous les articles qu'elle référence sont importés et pré-sélectionnés, **dans l'ordre où ils apparaissent sur la page de livre** (et non par ordre alphabétique — l'API MediaWiki trie les liens, le logiciel relit donc le wikitexte de la page pour retrouver l'ordre réel). Seuls leur titre et leur URL sont chargés à ce stade; leur PDF complet n'est téléchargé qu'au moment de la génération. La structure de la page de livre est aussi reprise : la première ligne de la forme `=== … ===` devient le sous-titre du livre (seulement si le champ « Sous-titre » de l'étape Édition est vide), et chaque ligne commençant par `;` ouvre un chapitre qui reçoit les articles listés en dessous, jusqu'au chapitre suivant (étape Organisation, section 6). Le livre garde l'ordre exact de la page : les articles placés avant le premier `;` restent sans chapitre mais **en tête du livre**, avant le premier chapitre et sans page de chapitre ni intitulé « Sans chapitre » (réglage `unassigned_first` du livre, enregistré dans le fichier JSON); cela ne vaut que si le livre n'avait encore aucun chapitre avant l'import, sinon ces articles rejoignent les autres articles sans chapitre, à la fin. Les liens et la mise en forme `''`/`'''` de ces lignes sont réduits à leur texte; un chapitre sans article est ignoré, et les lignes `== … ==` (titre enregistré par le créateur de livres) ne sont pas utilisées. Le message de confirmation renvoie vers la page d'aide Wikipédia sur les livres (`https://fr.wikipedia.org/wiki/Aide:Livres`).
  Syntaxe d'une page de livre, telle que décrite par l'aide Wikipédia ([Aide:Livres/Aide avancée](https://fr.wikipedia.org/wiki/Aide:Livres/Aide_avanc%C3%A9e)), et traitement par le logiciel (`wikipedia_api.get_book`) :
  * Titre — `== Titre ==` : ignoré; le titre du livre se saisit dans l'étape Édition.
  * Sous-titre — `=== Sous-titre ===` : la première ligne de cette forme devient le sous-titre du livre (voir ci-dessus).
  * Chapitre — `;Nom du chapitre` : ouvre un chapitre.
  * Article — `:[[Article]]` : l'article est ajouté au chapitre en cours. En pratique, tout lien `[[…]]` d'une ligne qui n'est ni un titre ni un chapitre est pris, même sans `:` initial; une ancre (`#section`) est retirée; les liens dont le titre contient `:` (autres espaces de noms, liens interlangues, fichiers) et les doublons sont ignorés; au plus 200 articles sont lus.
  * Article renommé — `:[[Frégate (bateau)|Frégate]]` : c'est l'article cible (`Frégate (bateau)`) qui est ajouté; le libellé après `|` est ignoré, le livre affiche le titre de l'article.
  * Version donnée — `:[{{fullurl:Nom de l'article|oldid=numéro de version}} Titre de l'article]` : non prise en charge. Ce n'est pas un lien `[[…]]`, l'article n'est donc pas importé; le PDF d'un article est toujours celui de sa version actuelle.

* Contenu d'une page de livre collé tel quel dans le champ, sur plusieurs lignes : dès qu'une ligne commence par `;` ou `:[[`, ou est un titre `== … ==` ou `=== … ===`, le texte entier est envoyé d'un seul bloc à `POST /api/books/from-wikitext` (`{"wikitext": "…", "language": "fr"}`, 200 000 caractères au plus) au lieu d'être lu ligne par ligne. Il est lu par la même fonction que le wikitexte d'une page de livre (`wikipedia_api.parse_book_wikitext`, mêmes règles, 200 articles au plus) : ordre, chapitres `;`, sous-titre `===`, et en plus le titre : la première ligne `== … ==` devient le titre du livre (`book_wikitext_title`). Les articles sont pris sur Wikipédia, dans la langue choisie à côté du champ, sans vérifier qu'ils existent (comme pour une page de livre, un article introuvable n'échoue qu'à la génération). Un texte sans lien `[[…]]` vers un article est refusé (HTTP 422). Cela permet de composer un livre au format « Livre: » sans l'enregistrer sur Wikipédia.

* Version imprimable de Wikilivres écrite à la main (syntaxe décrite par [Wikilivres/Créer la version imprimable d'un livre](https://fr.wikibooks.org/wiki/Wikilivres/Cr%C3%A9er_la_version_imprimable_d%27un_livre)), collée telle quelle ou donnée par son adresse : dès que le texte contient une inclusion `{{:Page}}`, il est lu comme une version imprimable (`wikipedia_api.parse_printable_wikitext`, même endpoint `POST /api/books/from-wikitext`, 500 pages au plus). Chaque inclusion `{{:Livre/Chapitre}}` devient une page de **Wikilivres**, dans la langue choisie à côté du champ, dans l'ordre du texte ; chaque titre de niveau 1 `= … =` ouvre un chapitre (balises comme `<center>` et mise en forme retirées) ; les autres modèles (`{{Notice de version imprimable}}`, `{{Nouvelle page imprimée}}`, `{{#ifeq:…}}`…), les doublons, les inclusions d'un autre espace de noms et les pages de couverture et de licence (`…/Couverture`, `Licence de documentation libre GNU`…, `PRINTABLE_SKIPPED_PAGES`), que l'application produit elle-même, sont ignorés ; le paramètre `titre=` (ou `title=`) du premier modèle qui en a un (`{{Couverture de version imprimable|titre=…}}`, `{{Page de titre|titre=…}}`) devient le titre du livre (`printable_wikitext_title`). L'adresse d'une page « …/Version imprimable » de Wikilivres (noms de `FULL_TEXT_PAGES`) n'est plus ajoutée comme une seule page : le serveur lit son wikitexte (`MediaWikiClient.get_wikitext`) ; s'il contient des inclusions, le livre en est tiré de la même façon (titre repris de `titre=`, sinon du sommaire) ; sinon (version imprimable par le module `{{imprimable}}`, qui relit le sommaire), c'est le sommaire parent qui est proposé, avec la fenêtre « Le livre entier » / « Le livre entier et son sommaire » / « Seulement cette page » décrite plus haut.

Exemple d'URL d'article :

`https://fr.wikipedia.org/wiki/Épaves_de_la_rade_de_Saint-Pierre`

### 3.2 Informations conservées par article

Pour chaque article, le logiciel conserve :

* Le titre.

* L'URL Wikipédia.

* La langue.

* Le résumé, lorsqu'il provient d'une recherche (les articles ajoutés par URL, par titre ou importés depuis une page de livre n'ont pas de résumé pré-rempli).

* L'identifiant de page Wikipédia, lorsqu'il est connu (résultats de recherche).

L'utilisateur peut supprimer un article principal sans affecter les autres.

### 3.3 Introduction et auteur proposés automatiquement

Quand le tout premier article principal du livre est ajouté (y compris le premier article d'une page de livre importée, section 3.1), le logiciel propose automatiquement, dans l'étape Édition (section 12) :

* L'introduction du livre, à partir du résumé introductif de cet article sur Wikipédia.

* L'auteur du livre, à partir du pseudonyme (ou de l'IP, pour une contribution anonyme) ayant créé la page sur Wikipédia.

Cette proposition ne remplace jamais un champ déjà renseigné par l'utilisateur, et reste entièrement modifiable. Elle ne se déclenche qu'une fois, pour le premier article seulement — ajouter d'autres articles ensuite ne la redéclenche pas.

## 4\. Exploration des articles liés

### 4.1 Principe

Le logiciel explore les liens internes présents dans les articles principaux afin de proposer des articles complémentaires, en s'appuyant sur l'API officielle MediaWiki (`action=parse&prop=text`) : les liens sont lus dans le rendu HTML de l'article, donc **dans leur ordre d'apparition dans la page** (bandeaux, infobox et légendes compris), et non par ordre alphabétique comme le renverrait `prop=links`. Sont ignorés : les liens vers des pages inexistantes (liens rouges), les liens hors espace principal (`Fichier:`, `Catégorie:`, `Aide:`, etc.), les ancres internes, le lien de la page vers elle-même et les doublons.

### 4.2 Profondeur d'exploration

La profondeur est paramétrable, entre 0 et 3, côté API (`/api/explore`); l'interface utilise toujours la profondeur 1 (section 4.4) :

| Profondeur | Comportement                                      |
| ---------- | ------------------------------------------------- |
| 0          | Aucun article complémentaire                      |
| 1          | Articles directement liés aux articles principaux |
| 2          | Articles liés aux articles de profondeur 1        |
| 3          | Articles liés aux articles de profondeur 2        |

La profondeur maximale est bornée à 3 niveaux afin d'éviter une exploration excessive.

### 4.3 Résultats de l'exploration

Pour chaque article découvert, le logiciel affiche :

* Son titre.

* Son URL.

* Un bouton « Ajouter au livre » et un bouton « × » pour l'écarter (section 5).

Au-dessus de la liste, une ligne rappelle de quel article viennent les suggestions (« Liens de « … », dans l'ordre de la page »). Les doublons sont éliminés automatiquement (comparaison insensible à la casse sur la langue et le titre), et les articles déjà présents dans « Vos articles » ne sont pas reproposés.

### 4.4 Lancer l'exploration

* Par défaut, la section « Suggestions » est vide et ne contient aucun bouton : un message invite à cliquer sur « Articles liés » sur l'un de ses articles.

* Le bouton « Articles liés », présent sur chaque carte de « Vos articles », remplit la liste avec les articles cités par cet article, dans l'ordre de la page (profondeur 1, jusqu'à 200 liens). Le bouton de l'article dont les liens sont affichés est mis en évidence.

* Un clic sur « Articles liés » d'un autre article **vide la liste** et la remplit avec les liens de ce nouvel article : la liste montre toujours les liens d'un seul article à la fois.

* Aucun réglage n'est demandé. L'API, elle, accepte toujours une profondeur de 0 à 3 et un maximum de 1 à 200.

* À la fin, un message indique le nombre de suggestions trouvées, puis la page défile jusqu'à la liste; si l'article ne cite aucun nouvel article, un message le précise.

## 5\. Sélection des articles

Cette fonctionnalité est essentielle.

Aucun article découvert ne doit être intégré automatiquement au livre.

Le logiciel présente la liste des articles découverts (« Suggestions ») et laisse l'utilisateur choisir exactement ceux qu'il souhaite conserver.

Fonctionnalités disponibles :

* « Ajouter au livre » sur une suggestion : elle quitte la liste des suggestions et rejoint « Vos articles », cochée, avec la mention de l'article d'origine; un message confirme l'ajout. Elle devient alors un article principal comme les autres : elle peut être décochée, retirée, ou servir de point de départ à une nouvelle exploration.

* « × » sur une suggestion : elle est retirée de la liste.

* « Tout ajouter » : ajoute toutes les suggestions visibles (en respectant le filtre par titre). Ce bouton, le filtre et le choix du tri n'apparaissent que lorsque la liste contient des suggestions.

* Recherche par titre parmi les suggestions.

* Tri des suggestions, sur la même ligne que le filtre (qui se raccourcit pour leur laisser la place, y compris sur smartphone), par deux boutons : « Ordre de la page » (ordre d'apparition des liens dans l'article, choix initial à chaque ouverture de l'application) ou « A → Z » (ordre alphabétique selon la langue de l'interface, sans tenir compte des majuscules ni des accents : « Éruption » est rangé à la lettre E). Le tri se combine avec le filtre; la phrase indiquant l'article d'origine précise l'ordre affiché. Ce choix n'est pas enregistré dans le fichier JSON du livre.

* Dans « Vos articles », une case à cocher par article indique s'il est inclus dans le livre.

La sélection est conservée avec le reste du livre, en mémoire et dans l'export JSON. Les suggestions, elles, ne sont pas enregistrées dans l'export JSON (`discovered_articles` y est toujours vide depuis la 1.9.6) : on les retrouve en relançant « Articles liés ». À l'ouverture d'un fichier JSON plus ancien, les articles découverts qui y étaient cochés sont rangés dans « Vos articles », les autres restent dans les suggestions.

## 6\. Organisation du livre

L'utilisateur organise les articles sélectionnés avant la génération du PDF.

Fonctionnalités :

* Réordonner les articles par glisser-déposer.

* Créer des chapitres et leur donner un titre. Le premier chapitre créé s'ajoute après les articles déjà présents, qui restent en tête du livre sans intitulé (`unassigned_first`), sans faire apparaître « Sans chapitre » ; il suffit ensuite d'y glisser des articles.

* Déplacer un article d'un chapitre à un autre, ou hors de tout chapitre, par glisser-déposer : l'appartenance à un chapitre vient de la place de l'article sous la ligne du chapitre (il n'y a pas de menu de choix du chapitre). Un article lâché sur la ligne d'un chapitre entre en tête de ce chapitre ; lâché sur « Sans chapitre », il sort de tout chapitre ; lâché sur un autre article, il prend sa place (`applyOrgSequence` dans `app.js`, qui met à jour `chapters`, `article_order` et `unassigned_first`).

* Déplacer un chapitre par glisser-déposer, en l'attrapant par n'importe quel endroit de sa ligne hors de son titre (le champ du titre n'est pas plus large que le titre, car Chrome ne lance pas de glisser-déposer depuis un champ de saisie). La liste se lit comme une suite : seule la ligne du chapitre se déplace, et chaque article appartient au chapitre placé au-dessus de lui ; les articles placés avant le premier chapitre sont en tête du livre, sans intitulé (`unassigned_first`). Quand le livre a un groupe « Sans chapitre » en fin de liste, un chapitre ne peut pas passer sous cette ligne.

* Chaque ligne d'article ou de document importé tient sur une ligne (titre, puis origine en plus petit) et porte un bouton « × » qui le retire du livre (un article retiré disparaît aussi de « Vos articles », un document importé est supprimé) et un bouton « ↗ » qui ouvre l'article sur Wikipédia ou le document importé dans un nouvel onglet. Les chapitres, la table des matières et les coupures de volume ont la même croix « × ».

* La table des matières ne figure pas dans la liste de l'étape Organisation : elle se choisit dans l'étape Édition, à côté de « Numéroter les pages », parmi trois choix — « Aucune » (`table_of_contents` faux), « Au début », juste après la couverture (`toc_position` `start`), ou « À la fin », après le dernier article, avant la licence et la conclusion (`toc_position` `end`). Le serveur accepte toujours `before:<clé>` (clé d'article/document, `chapter:<id>`, ou `chapter:` pour le groupe « Sans chapitre ») pour un appel direct de l'API ; un fichier JSON qui place la table des matières au milieu du livre la remet au début à l'ouverture.


* Un livre d'un seul article ou document n'a pas de table des matières, quel que soit le choix de l'étape Édition : le PDF n'en contient pas (`book_builder.toc_slot_index`). Elle revient dès que le livre compte deux éléments ; un volume d'un seul article n'en a pas non plus.

* Quand le livre a des chapitres, les articles qui n'appartiennent à aucun chapitre sont affichés à la fin de la liste, sous l'intitulé « Sans chapitre », comme dans le PDF. Exception : quand le premier chapitre a été créé après eux, qu'ils ont été glissés avant le premier chapitre, ou pour un livre importé d'une page de livre Wikipédia dont des articles précèdent le premier chapitre (section 3.1), ces articles sont affichés et placés dans le PDF en tête, avant le premier chapitre, sans intitulé ni page de chapitre.

* Couper le livre en plusieurs volumes à sa guise, même sous la limite du serveur : le bouton « Nouveau volume + » de la barre d'outils ajoute une coupure au milieu du dernier volume ; la ligne « Début d'un volume » se déplace par glisser-déposer comme la table des matières, et se retire par sa croix « × » (le volume rejoint alors le précédent). Chaque coupure est enregistrée par rapport à l'élément qui la suit (`volume_breaks`, liste de `before:<clé>`, mêmes clés que `toc_position`, gardée dans l'export JSON et ignorée par le serveur) ; une coupure dont l'élément disparaît, qui viserait le premier élément du livre ou un chapitre sans article est ignorée. Chaque volume est généré dans un PDF à part (section 11.1).

* Ajouter une introduction générale et une conclusion.

* Choisir dans l'étape Édition une image de fond pour la couverture et une autre pour la dernière page, chacune importée depuis un fichier ou depuis son adresse (section 11.1).

* Activer ou non la numérotation des pages (activée par défaut).

Un article peut être déplacé librement dans la structure du livre.

### 6.1 Documents importés (images et PDF)

Dans l'étape Organisation, l'utilisateur peut aussi importer ses propres fichiers (image ou PDF), par le bouton « Choisir un fichier + » de la barre d'outils, à côté de « Nouveau volume + », ou par leur adresse (champ d'adresse suivi de « Utiliser l'adresse », ou touche Entrée), pour les intégrer au livre comme s'il s'agissait d'articles :

* Formats acceptés : images (`image/*`) et PDF (`application/pdf`); 15 Mo maximum par fichier.

* Par adresse : l'adresse doit commencer par `https://` (sinon « L'adresse doit commencer par https://. »). Une page de fichier Wikimédia passe par l'API `imageinfo`, comme pour les images de fond (section 11.1) : un PDF donne l'adresse du fichier original, une image sa vignette de 2 000 px ; pour toute autre adresse, le document est un PDF si l'adresse finit par `.pdf`, sinon une image, que le navigateur essaie d'afficher avant de l'accepter (« Document inaccessible à cette adresse (…). » en cas d'échec). Seule l'adresse est gardée dans le livre et dans l'export JSON (`url`, sans `data_base64`) : le serveur télécharge le document à chaque génération, pendant l'étape « Préparation du document importé », avec les mêmes contrôles que les images de fond (PNG, JPEG, GIF, WebP ou PDF d'après l'en-tête `Content-Type`, qui décide aussi s'il s'agit d'un PDF), et la génération s'arrête avec l'adresse en cause s'il est inaccessible. « ↗ » ouvre alors l'adresse elle-même.

* Un document importé apparaît dans la liste des éléments à organiser au même titre qu'un article : il peut être réordonné et déplacé dans un chapitre par glisser-déposer, compte dans un volume, se retire par « × » et s'ouvre par « ↗ » (à partir d'une adresse `blob:`, Chrome refusant d'ouvrir une adresse `data:` dans un nouvel onglet), et sa page de départ apparaît dans la table des matières si la numérotation est activée.

* Une image importée est intégrée comme une page entière, centrée et mise à l'échelle au format du livre; un PDF importé est intégré tel quel, page par page.

* Le document se retire du livre par son bouton « × », indépendamment des autres documents et articles ; il n'y a pas de liste séparée des documents importés ni de case pour les exclure sans les supprimer. Un document désélectionné dans un fichier JSON antérieur à la 1.9.6 revient dans le livre à l'ouverture du fichier.

* Le contenu du fichier est conservé encodé en base64 dans l'état du livre et dans l'export JSON, afin de pouvoir régénérer le PDF ou reprendre le livre sans avoir à ré-importer le fichier.

* **Titre du document** : chaque document importé a, dans la liste de l'étape Organisation, un champ de titre (« Titre du document dans le livre », 300 caractères au plus, un titre vide n'est pas enregistré). Ce titre remplace le nom du fichier partout dans le PDF : table des matières, signets, page de licence. À l'import d'un fichier, le titre proposé est le nom du fichier sans son extension (« IMG_1234 » pour « IMG_1234.jpg »).

* **Page web** : le champ d'adresse accepte aussi l'adresse `https://` d'une page web quelconque (« Adresse d'une image, d'un PDF ou d'une page web ») : une adresse qui ne finit ni par `.pdf` ni par une extension d'image et que le navigateur n'arrive pas à afficher comme image devient un document `kind` = `html` (étiquette « Page web convertie en PDF »), donné par son adresse seulement. Une page d'un projet Wikimédia est refusée (« Pour une page Wikimédia, utilisez le champ de l'étape Sources : il reprend son PDF officiel. »), côté navigateur comme côté serveur. À chaque génération, le serveur télécharge la page (5 Mo au plus, type `text/html` ou `application/xhtml+xml`, mêmes contrôles que les autres adresses : HTTPS, adresses publiques, redirections revérifiées), retire scripts, cadres, formulaires, objets, vidéos et attributs `on…` (`app/html_document.py`), télécharge lui-même ses feuilles de style (10 au plus, `@import` et `url(…)` retirés) et ses images (40 au plus, PNG, JPEG, GIF, WebP ou SVG, 5 Mo chacune et 20 Mo en tout pour toutes les ressources), avec les mêmes contrôles, et les intègre en `data:` ; une ressource refusée ou inaccessible est simplement omise. La page est ensuite rendue en PDF par WeasyPrint au format du livre (marges de 15 mm), toujours limité aux adresses `data:`, dans un processus de travail, puis recomposée comme les autres documents. Une page inaccessible ou qui n'est pas du HTML arrête la génération avec un message qui donne l'adresse.

## 7\. Récupération du contenu Wikipédia

L'ajout et l'exploration ne téléchargent pas le contenu complet des pages. Au moment de générer le PDF, chaque article sélectionné est récupéré via l'endpoint PDF officiel de Wikimedia (`/api/rest_v1/page/pdf/{titre}/{format}`), équivalent à la fonction « Télécharger comme PDF » de Wikipédia. Wikipédia ne compose ses PDF qu'en trois formats (`a4`, `letter`, `legal`, toujours en portrait) : le logiciel demande `letter` pour un livre au format Letter, `legal` pour un livre au format Legal, et `a4` pour tous les autres formats (A0 à A6, personnalisé). Pour Letter et Legal, les pages des articles sont donc composées par Wikipédia directement au bon format, sans marges blanches dues à un changement de proportions.

Le contenu de chaque article (texte, structure, images, références) n'est jamais reconstruit : c'est exactement celui du PDF officiel Wikipédia. Seule sa mise en page physique change : chaque page est recomposée (mise à l'échelle et centrée, sans déformation) sur le format et l'orientation choisis pour le livre — voir section 10.1.

## 8\. Références, images et licences

Le logiciel ne reconstruit pas le contenu des articles : chaque article sélectionné est intégré sous la forme du PDF officiel généré par Wikipédia. En conséquence :

* Les références et citations restent exactement celles du PDF Wikipédia, avec leur mise en forme d'origine.

* Les images et leurs légendes sont celles intégrées par Wikipédia à l'export PDF, avec leur mise en page d'origine.

* Les crédits et licences des textes et des images sont ceux imprimés par Wikipédia dans son propre PDF; le logiciel ne les extrait pas et ne les réécrit pas séparément.

* Quand Wikimédia refuse temporairement une requête parce qu'il reçoit trop de demandes (HTTP 429) ou qu'il est surchargé (HTTP 503), le logiciel attend puis réessaie, jusqu'à 4 fois : le délai indiqué par Wikimédia (en-tête `Retry-After`, borné à 20 s), ou sinon 2, 4, 8 puis 16 s. L'attente est commune à tous les téléchargements en cours d'un même livre (ils reprennent ensemble au lieu de relancer Wikimédia chacun de leur côté) et ne bloque pas le serveur, qui continue de répondre aux autres requêtes. Pendant la génération du PDF, chaque nouvelle pause est signalée dans la fenêtre de statut, sous le libellé de l'étape en cours, par un compte à rebours (« Wikipédia limite les requêtes en ce moment : nouvel essai dans 5 s… ») qui disparaît à la fin de la pause; l'étape et la barre de progression ne bougent pas. Cela vaut pour toutes les requêtes vers Wikipédia (PDF et API MediaWiki).
* Si Wikipédia ne peut pas produire de PDF pour un article sélectionné (page introuvable, service indisponible, réponse invalide, ou encore refus après ces 4 nouvelles tentatives, avec le message « Wikipédia limite le nombre de requêtes en ce moment… »), la génération du livre échoue dans son ensemble et un message d'erreur explicite est affiché; aucun livre partiel n'est produit.

* Seule exception à l'intégrité du PDF officiel : lorsque la numérotation des pages est activée (section 10), un numéro de page est superposé en bas de chaque page, y compris les pages d'articles — sans toucher au contenu, aux crédits ni aux licences imprimés par Wikipédia.

## 9\. Paramétrage du format du livre

Le format du document est entièrement configurable.

### 9.1 Formats standards

Formats proposés :

| Format | Dimensions    |
| ------ | ------------- |
| A0     | 841 × 1189 mm |
| A1     | 594 × 841 mm  |
| A2     | 420 × 594 mm  |
| A3     | 297 × 420 mm  |
| A4     | 210 × 297 mm  |
| A5     | 148 × 210 mm  |
| A6     | 105 × 148 mm  |
| Letter | 216 × 279 mm  |
| Legal  | 216 × 356 mm  |

Le format A4 est proposé par défaut, sans être imposé.

### 9.2 Format personnalisé

L'utilisateur peut saisir :

* La largeur en millimètres.

* La hauteur en millimètres.

### 9.3 Orientation

Deux orientations sont disponibles :

* Portrait.

* Paysage.

### 9.4 Marges

L'utilisateur choisit d'abord un jeu de marges prédéfini :

| Préréglage    | Haut | Bas | Intérieure | Extérieure | Reliure |
| ------------- | ---- | --- | ---------- | ---------- | ------- |
| Standard      | 18   | 18  | 18         | 16         | 0       |
| Étroites      | 10   | 10  | 12         | 10         | 0       |
| Larges        | 25   | 25  | 25         | 22         | 0       |
| Pour reliure  | 18   | 18  | 20         | 16         | 10      |

Valeurs en millimètres; « Standard » correspond aux valeurs par défaut. Le choix « Personnalisées », ou le dépliage de « Régler les marges au millimètre », donne accès au réglage individuel de chaque marge. Le préréglage affiché est déduit des valeurs du livre : dès qu'une marge ne correspond plus à aucun préréglage, « Personnalisées » est affiché. Les préréglages ne sont pas enregistrés en tant que tels dans le livre ni dans l'export JSON, seules les cinq valeurs le sont.

Les marges réglables individuellement sont :

* La marge supérieure.

* La marge inférieure.

* La marge intérieure.

* La marge extérieure.

* La marge de reliure, en complément de la marge intérieure.

## 10\. Mise en page du livre

Le PDF est structuré comme un véritable livre.

Éléments générés par l'application :

* Couverture (titre du livre, sous-titre, auteur, note ; la date d'édition est en fin de livre, sous le logo).

* Introduction, si elle a été saisie.

* Table des matières, groupée par chapitre : sous un titre souligné, chaque chapitre est une ligne en gras (titre à gauche, numéro de page aligné à droite), suivie en retrait de la liste de ses articles et documents, avec leur numéro de page aligné dans la même colonne. Chaque ligne, numéro de page compris, est un lien interne cliquable vers la première page du chapitre ou de l'article.

* Pages de titre de chapitre, pour chaque chapitre contenant des articles.

La table des matières peut être absente si l'utilisateur l'a retirée (section 6).

* Conclusion, si elle a été saisie.

* Page de licence (section 15), toujours présente, après la conclusion (ou après le dernier article, et après la table des matières si elle est en fin de livre), terminée par le logo, la date d'édition et les liens de Wikipedia2Book.

* Image de fond de dernière page, seule sur une page, si elle a été choisie.

Le contenu des articles et des documents importés n'est pas mis en page par l'application : ce sont les pages de leur PDF d'origine (officiel Wikipédia, ou document importé). Leur format physique, lui, est systématiquement harmonisé avec le reste du livre — voir section 10.1.

La couverture et la table des matières sont deux sections distinctes dans le PDF final : la position choisie pour la table des matières dans l'étape Édition (section 6) est celle effectivement utilisée à la génération — la couverture reste toujours la première page, et la table des matières s'insère exactement à l'endroit choisi : juste après la couverture, avant un chapitre (avant sa page de titre), avant un article, ou après le dernier article (avant la licence et la conclusion).

La navigation dans le PDF final s'appuie sur des signets (couverture, table des matières, une entrée par chapitre et par article, licence, conclusion) et sur les liens de la table des matières. Ces liens sont produits ainsi : WeasyPrint génère chaque ligne comme un lien vers une adresse provisoire (`https://wikipedia2book.invalid/toc/<clé>`, clé d'article ou de document, ou `chapter:<n>`); après l'assemblage, ces liens sont relus (`pdf_generator.internal_links`), retirés, puis remplacés par des liens internes vers la page réelle de l'élément dans le livre (`BookAssembly.link_toc`), y compris quand la numérotation des pages est désactivée.

### 10.1 Format et orientation, appliqués à toutes les pages

Toutes les pages du PDF final respectent le format et l'orientation choisis pour le livre (section 9), sans exception :

* Les pages générées par l'application (couverture, introduction, table des matières, pages de chapitre, licence, conclusion) sont nativement produites à ce format.

* Chaque page d'article (PDF officiel Wikipédia) et chaque page de document importé est recomposée sur une page de ce même format : son contenu est mis à l'échelle et centré, en conservant ses proportions d'origine (pas de déformation). Si les proportions de la page source diffèrent de celles du livre, des marges blanches apparaissent sur les côtés ou en haut/bas plutôt que de déformer le contenu. Une page qui a déjà le format du livre à 1 point près (0,35 mm), sans rotation, n'est pas recomposée : sa taille est seulement fixée exactement au format du livre, sans réécrire son contenu. C'est le cas des PDF Wikipédia pour les livres A4, Letter et Legal, demandés directement dans ce format (section 7) : leur assemblage est alors environ sept fois plus rapide.

* Le contenu lui-même (texte, images, références) n'est jamais modifié ni reconstruit — seule sa mise à l'échelle et sa position sur la page changent.

### 10.2 Numérotation des pages

L'option « Numéroter les pages » (section 6) est activée par défaut et peut être désactivée.

Quand elle est activée :

* Toutes les pages du livre affichent un numéro en bas de page, de façon continue — y compris les pages d'articles et de documents importés, à l'exception de la couverture et de la dernière page de fond (image, couleur ou logo).

* La table des matières affiche, pour chaque chapitre et chaque article, le numéro de la page où il commence.

* Pour calculer ces numéros avant d'assembler le livre, le logiciel génère la couverture (qui ne dépend pas des numéros et sert telle quelle dans le livre, sans être générée une seconde fois) et une première version de la table des matières si elle n'est pas placée à la fin, afin d'en mesurer la pagination (les numéros des éléments placés après la table des matières en tiennent compte); il régénère ensuite la table des matières avec les numéros corrects. Dans de rares cas (livre très dense), l'ajout des numéros dans la table des matières peut légèrement décaler cette pagination d'une page.

Aucune fonctionnalité de prévisualisation n'est proposée actuellement.

## 11\. Génération du PDF

### 11.1 Déroulement

Le bouton « Générer le PDF » est toujours visible et actif, quel que soit l'onglet affiché; si aucun article ni document n'est sélectionné, un message l'indique au moment du clic plutôt que de désactiver le bouton.

Une fois le PDF lancé, le logiciel :

* Vérifie qu'au moins un article ou document est sélectionné; sinon, la génération est refusée.

* Télécharge le PDF officiel de chaque article sélectionné; décode chaque document importé sélectionné (section 6.1), en convertissant une image en page PDF si besoin.

* Si la numérotation des pages est activée, calcule à l'avance la page de départ de chaque chapitre et de chaque article (section 10.2).

* Génère la couverture (avec l'introduction éventuelle) et la table des matières (avec les numéros de page si activés) comme deux sections distinctes; la couverture reçoit le signet racine portant le titre du livre.

* Insère la table des matières à la position choisie (section 6), ou l'omet si elle a été retirée.

* Pour chaque chapitre (ou pour l'ensemble des articles s'il n'y a pas de chapitre) : génère une page de titre de chapitre avec son propre signet, puis ajoute le PDF officiel de chaque article du chapitre, avec un signet par article.

* Recompose chaque page ajoutée (couverture, table des matières, chapitres, articles, documents importés) sur le format et l'orientation choisis pour le livre (section 10.1), avant de l'assembler au document final. Le PDF de chaque article ou document est recomposé en arrière-plan dès qu'il est téléchargé ou préparé, pendant le téléchargement du suivant, si bien qu'au moment de l'assemblage ses pages sont en général déjà prêtes.

* Ajoute une page de licence avec signet « Licence » (section 15), après la conclusion, ou après le dernier chapitre/article et la table des matières éventuellement placée en fin de livre quand il n'y a pas de conclusion.

* Termine la page de licence, juste après son texte, par le logo de Wikipedia2Book (`app/static/Wikipedia2bookLogoPrint.png`, incorporé au PDF, 100 mm de large au plus, lui-même cliquable vers https://wikipedia2book.toolforge.org/), la date d'édition (« Édition du JJ/MM/AAAA », qui n'est plus sur la couverture) et deux liens cliquables, https://wikipedia2book.toolforge.org/ et https://github.com/gmoulard/wikipedia2book ; un livre en volumes les a à la fin de chaque volume.

* **Images de fond** (étape Édition, champs « Image de fond de la couverture » et « Image de fond de la dernière page ») : chaque image est importée depuis un fichier (PNG, JPEG, GIF, WebP ou SVG, 15 Mo au plus) ou depuis son adresse ; une adresse de page de fichier Wikimédia (`https://commons.wikimedia.org/wiki/File:…`, ou `Fichier:…` sur un projet en `<langue>.<projet>.org`) passe par l'API `imageinfo` de ce wiki, appelée par le navigateur (`origin=*`) pour obtenir une vignette de 2 000 px de large sur `upload.wikimedia.org` ; paramètres de suivi `utm_*` retirés ; toute autre adresse doit commencer par `https://` (sinon « L'adresse doit commencer par https://. ») et n'est acceptée que si le navigateur arrive à afficher l'image, sans besoin d'autorisation CORS (sinon un message invite à télécharger l'image puis à importer le fichier). Une image importée depuis un fichier est gardée dans le livre en base64 ; une image donnée par son adresse ne garde que l'adresse, dans le livre comme dans l'export JSON, et le serveur la télécharge à chaque génération (étape de progression `fetch_image`, « Téléchargement de l'image « … » », avant les articles) : `main.fetch_remote_file`, puis `json_source.download`, avec les contrôles de `GET /api/pdf/from-json` (HTTPS, adresses publiques seulement, revérifiées à chaque redirection, 3 au plus, 30 s au plus) et 15 Mo au plus, type PNG, JPEG, GIF, WebP ou SVG d'après l'en-tête `Content-Type`. L'image téléchargée n'est gardée en mémoire que le temps de la génération ; si elle est inaccessible ou d'un autre type, la génération s'arrête avec un message qui donne l'adresse (événement `error`, HTTP 502 sur `/api/pdf`). Modèle `BookImage` (`cover_image`, `back_image`) : `title`, puis soit `url`, soit `mime_type` et `data_base64` (base64 vérifié par le serveur), jamais les deux. L'aperçu s'affiche depuis l'adresse ou le contenu, avec un bouton « Retirer ». Chaque image remplit toute sa page, marges comprises, sans déformation : ce qui dépasse en largeur ou en hauteur est rogné à partir du centre (`background-size: cover` ; `background-attachment: fixed`, sans lequel WeasyPrint dimensionne le fond sur la zone intérieure aux marges). Sous chaque champ, quand l'image ne convient pas, l'interface indique la taille recommandée en pixels, calculée à 300 dpi d'après le format et l'orientation du livre (2 480 × 3 508 px en A4 portrait, `recommendedBackgroundSize` dans `app.js`) et mise à jour quand ils changent, avec l'alerte qui la justifie : image trop petite (moins de 150 dpi une fois la page remplie : « Image trop petite (… px) : elle sera floue à l'impression. ») ou d'orientation différente de la page (« L'image n'a pas l'orientation de la page : une grande partie sera rognée. »)  ; rien ne s'affiche pour une image qui convient, sans image, ni pour une image SVG. Avant le rendu, le serveur ramène chaque image de fond plus grande que la page à la taille de la page à 300 dpi, recadrée au centre comme à l'affichage (`book_builder.fit_background`, Pillow, dans le processus d'assemblage, étape `fit_backgrounds` du journal) : JPEG de qualité 90, ou PNG si l'image a de la transparence ; une image déjà assez petite, une image SVG ou illisible est gardée telle quelle. Une photo de 5 616 × 3 744 px (5,2 Mo) devient ainsi un JPEG de 2 480 × 3 508 px (1,6 Mo) en A4 : sur Toolforge, le rendu de la couverture par WeasyPrint passe de 2,0 s à 0,7 s ; le pic mémoire de l'assemblage de 328 à 283 Mo (la réduction décode l'image entière mais ne redimensionne que la partie visible, `resize(box=…)`) ; le PDF n'y gagne presque rien, WeasyPrint recompressant déjà la photo. L'image de couverture est placée sous le titre, le sous-titre, l'auteur et la note de couverture, dont la couleur dépend de l'image (`book_builder.cover_text_style`, Pillow) : le serveur mesure la luminance de la partie de l'image visible derrière le texte (zone intérieure aux marges, 65 % supérieurs de la hauteur utile) ; texte noir si 95 % de cette zone est assez claire pour un contraste de 4,5:1, blanc si 95 % est assez sombre, sinon (image contrastée, SVG ou image illisible) texte noir sur un bandeau blanc semi-transparent. Les pages d'introduction n'ont pas d'image. Avec une image de dernière page, une page de plus est ajoutée après la licence, sans marge ni texte, entièrement couverte par l'image (`book_builder.build_back_cover_html`, étape `render_back_cover` du journal) ; le logo, la date et les liens restent sur la licence. Chaque volume d'un livre en volumes reprend les deux images. Tests : `tests/test_backgrounds.py`.

* **Couleurs et logo Wikipédia** (étape Édition, sous chacune des deux images de fond : case « Couleur de fond » avec un sélecteur de couleur, case « Logo Wikipédia ») : `cover_color` et `back_color` (`#rrggbb`, `null` sans couleur, toute autre valeur refusée par le serveur ; la couverture est bleue par défaut, `#273c75` soit rgb(39, 60, 117), case cochée dans l'interface, `null` explicite pour s'en passer ; `back_color` vaut `null` par défaut), `cover_logo` et `back_logo` (booléens, faux par défaut). La couleur remplit toute la page, sous l'image de fond s'il y en a une (`background-color` de `@page`). Sur la couverture sans image, le texte passe en blanc quand la couleur est sombre (luminance relative sous 0,5, `book_builder.color_text_style`), sinon il reste noir ; avec une image, c'est l'image qui décide, comme avant. Le logo Wikipédia (`app/static/WikipediaLogo.png`, copie à 480 px du fichier [Wikipedia-logo-v2.svg](https://commons.wikimedia.org/wiki/File:Wikipedia-logo-v2.svg) de Wikimedia Commons, CC BY-SA 3.0, version 1 par Nohat d'après un concept de Paullusmagnus ; marque de la Wikimedia Foundation, rappelé sous les champs) se place en bas à droite de la couverture (25 mm de large, dans les marges) et de la dernière page (25 mm de large et 15 mm du bord au plus, moins sur une petite page). Le logo imprimé après la licence est `Wikipedia2bookLogoPrintTransparent.png`, version à fond transparent de `Wikipedia2bookLogoPrint.png` (gardé tel quel). Une couleur ou le logo en dernière page suffisent à créer la page de fin après la licence, même sans image (`book_builder.has_back_cover`) ; cette dernière page, comme la couverture, ne porte pas de numéro de page (`BookAssembly.stamp_page_numbers(skip_last=True)`). Tests : `tests/test_backgrounds.py` (`ColorAndLogoTest`), `tests/test_pdf_stream.py`.

* Ajoute une page de conclusion avec signet, si une conclusion a été saisie — après la table des matières, même quand elle est positionnée en fin de livre, et avant la licence.

* Si la numérotation des pages est activée, superpose un numéro de page en bas de chaque page du document assemblé (sauf la couverture et la dernière page de fond).

* Fusionne l'ensemble en un seul fichier PDF et le rend accessible au téléchargement, nommé d'après le titre du livre.

* **Assemblage sur disque temporaire** : chaque PDF recomposé (article, document importé, page générée) est écrit dans un dossier temporaire propre à la génération, au lieu de rester en mémoire. Le livre est assemblé par PyMuPDF (bibliothèque MuPDF) en deux temps : fusion des fichiers par lots de 20, chaque lot ajouté au fichier fusionné en mise à jour incrémentale puis libéré de la mémoire, suppression aussitôt des fichiers des parties, puis réouverture de ce fichier pour y ajouter signets, liens de la table des matières et numéros de page, et écriture du PDF final, lui aussi dans ce dossier, puis envoyé par morceaux à l'utilisateur (`/api/pdf/stream` comme `/api/pdf`, qui annonce sa taille). Le dossier est supprimé dès que l'envoi se termine, que la génération échoue ou que l'utilisateur l'abandonne. Chaque téléchargement garde son créneau jusqu'à ce que son PDF soit recomposé et écrit : au plus 2 ou 4 PDF bruts (section 13.2) sont en mémoire en même temps, même sur un serveur au processeur limité. La mémoire du serveur ne croît donc presque plus avec la taille du livre : sur un livre de test de 100 articles et 197 Mo, le pic passe de 1 100 Mo à 158 Mo, de 2 130 Mo à 200 Mo pour 200 articles et 393 Mo, et à 262 Mo pour 300 articles et 590 Mo (mesures locales, section 13.12). Les flux sont recopiés tels quels, sans décompression ni recompression : le PDF final a la même taille qu'avant.

* **Numérotation sans réécriture des pages** : le numéro de chaque page est ajouté dans deux petits flux placés autour du contenu existant de la page, qui n'est ni relu ni réécrit (police Helvetica intégrée de MuPDF). L'ancienne superposition d'une page de numéros réécrivait le contenu de chaque page sans le compresser : un livre de 100 articles pesait 173 Mo au lieu de 96 (mesure locale du 16/11/2026).

* **Limite de 300 articles par livre, sur tous les hébergements** : au-delà, la génération est refusée d'emblée (HTTP 413, `detail` = `{"code": "too_many_articles", "count", "limit", "message"}`), sur `/api/pdf`, `/api/pdf/stream` et les endpoints de génération directe. C'est une limite volontaire, pour ménager le service PDF de Wikimédia (chaque livre y télécharge tous ses articles) et la mémoire du conteneur, que le test aux limites remplit presque entièrement vers 600 articles (section 13.12). La valeur (300 sur Toolforge en 1.8.7 et 1.8.8, 2 000 en 1.8.9 et 1.9.0, 300 partout depuis la 1.9.1) reste sous la limite mesurée de la mémoire de Toolforge, entre 800 et 1 000 articles. L'interface ne propose pas de choix : au-delà de la limite, elle découpe d'elle-même le livre en volumes (voir ci-dessous) ; la fenêtre d'alerte avec le message traduit (« Ce livre compte {count} articles, mais la génération est limitée à {limit} articles par livre… ») ne reste que pour un volume que le serveur refuserait encore. Deux variables d'environnement, posées dans le `Dockerfile` (`ENV`) ou passées au conteneur (`docker run -e`), règlent un déploiement : `WIKIPEDIA2BOOK_ARTICLE_LIMIT` (nombre maximal d'articles par livre, `0` = pas de limite ; `300` dans le `Dockerfile`, et 300 aussi quand elle n'est pas positionnée, sur Toolforge comme ailleurs) et `WIKIPEDIA2BOOK_DOWNLOADS` (téléchargements simultanés par livre : de 1 à 2 hors Toolforge, politique robots de Wikimédia, de 1 à 4 sur Toolforge ; `2` dans le `Dockerfile`). Une valeur invalide empêche le serveur de démarrer, avec un message explicite (`main.deployment_settings`). La limite d'articles se règle d'après la mémoire du conteneur : environ 250 Mo pour le serveur et le processus d'assemblage, plus 2 à 2,5 Mo par article au pic, avec une large marge pour plusieurs utilisateurs (README, « Deploying your own container » ; mesures en section 13.12).

* **Mémoire vérifiée avant chaque étape** (`app/resource_gate.py`, `MEMORY_GATE` dans `main.py`) : avant de télécharger un article, un document ou une image de fond, avant de recomposer un article et avant l'assemblage du livre, la génération estime la mémoire dont l'étape a besoin d'après la taille des fichiers : téléchargement 10 Mo par fichier (sa taille n'est pas encore connue, la réserve dépend donc du nombre de fichiers téléchargés en même temps), recomposition 5 Mo + 25 fois la taille du PDF reçu, assemblage 100 Mo + 2,5 fois la taille des articles recomposés + 35 fois celle des images de fond (coefficients mesurés le 2026-11-17, section 13.12). L'étape ne démarre que si la mémoire utilisée par le conteneur (cgroup), plus les réserves des étapes en cours, plus son estimation, reste sous une part de la limite du conteneur : `WIKIPEDIA2BOOK_MEMORY_RATIO`, 0,95 par défaut (`0` = pas de contrôle ; toute valeur hors de 0 à 1 empêche le démarrage). Sinon elle attend, sans limite de temps, son tour dans l'ordre d'arrivée (une grosse étape n'est pas doublée par les petites), et la fenêtre de progression affiche « Serveur occupé : votre livre reprend dès qu'il y a assez de mémoire (attente : 14 s)… » (événement `{"type": "busy", "seconds"}` du flux, renvoyé toutes les 10 s, clé `progress.busy`). Une étape démarre toujours quand aucune autre n'a de réserve, pour qu'un livre plus gros que la marge se fasse quand même, seul ; sans limite de mémoire connue (poste local), rien n'attend. Fermer la fenêtre abandonne l'attente. Chaque attente d'au moins une seconde est notée dans le journal des générations (étape `memory_wait`), et `/api/health/details` donne l'état du contrôle (`memory_gate`).

* **Place disque vérifiée avant chaque téléchargement et avant l'assemblage** : même mécanisme (`DISK_GATE`), sur le disque du dossier temporaire (`shutil.disk_usage`) : un téléchargement d'article ou de document ne démarre que si l'espace utilisé du disque, plus les réserves en cours, plus 30 Mo (taille du fichier recomposé, inconnue avant le téléchargement, `DOWNLOAD_DISK_BYTES`) reste sous `WIKIPEDIA2BOOK_DISK_RATIO` de sa taille, 0,95 par défaut (`0` = pas de contrôle). La réserve dure jusqu'à l'écriture du fichier recomposé, qui compte ensuite dans l'espace utilisé ; l'attente affiche le même « Serveur occupé » et figure dans le journal (`memory_wait`, `reason` = `disk`). Sur Toolforge, ce disque est partagé avec d'autres outils (146 Go, environ 49 Go utilisés le 2026-11-17) ; la place disque n'a encore jamais manqué. Avant l'assemblage, la même vérification réserve 50 Mo + 2 fois la taille des articles recomposés (`assembly_disk_reserve` : le fichier fusionné est écrit pendant que les parties existent encore, puis le livre final à côté du fichier fusionné), gardés jusqu'à la fin de l'assemblage (`reason` = `assembly_disk` dans le journal).

* **Mémoire du serveur rendue et contenue** (depuis les tests de générations simultanées de la section 13.12) : (1) la glibc limite ses réserves de mémoire (`MALLOC_ARENA_MAX=2` dans le `Dockerfile` et le `Procfile`) et rend au système la mémoire libérée après chaque article et à la fin de chaque génération (`resource_gate.release_memory`, `malloc_trim`) ; (2) chaque génération est admise à l'entrée, avant de charger quoi que ce soit, contre un budget à part de `WIKIPEDIA2BOOK_GENERATIONS_RATIO` de la limite du conteneur (0,5 par défaut) : elle réserve 25 Mo + 3 fois la taille des données en base64 du livre reçu (documents importés, images de fond) + 15 Mo par image de fond donnée par son adresse (`generation_reserve`), gardés jusqu'à sa fin ; les suivantes attendent au tout début, avec le même « Serveur occupé » (`reason` = `generation` dans le journal) ; ce budget est distinct du contrôle des étapes, qu'il bloquerait sinon sans fin ; (3) les images de fond, téléchargées ou importées, sont écrites dans le dossier temporaire de la génération et retirées du livre transmis à l'assemblage, qui les relit (`background_files`) ; (4) la recomposition de chaque article ou document se fait dans un processus de travail (`isolation.run_in_worker`, 2 processus, un nouveau pour chaque tâche, qui rend toute sa mémoire en se terminant), et non plus dans le processus du serveur ; un processus de travail arrêté (faute de mémoire) arrête la génération avec un message explicite. Les téléchargements restent dans le processus du serveur, où la limite de 2 téléchargements simultanés de la politique de Wikimédia est commune à tous les livres.
* **Volumes** : les coupures posées dans l'étape Organisation (section 6) délimitent d'abord les volumes ; le découpage automatique ci-dessous s'applique ensuite à chaque volume qui dépasse encore la limite. Avec des coupures et sans dépassement, « Générer le PDF » génère de même un volume par requête et annonce « Ce livre est généré en {count} volumes, téléchargés l'un après l'autre. » ; l'indication sous le compteur n'apparaît que si le découpage automatique ajoute des volumes. `/api/version` renvoie aussi `article_limit` (la limite du serveur, `null` sans limite), lue au chargement de la page. Quand le livre compte plus d'articles Wikimédia que cette limite (les documents importés ne comptent pas), l'étape Organisation l'annonce sous le compteur (« Au-delà de {limit} articles, le livre sera généré en {count} volumes, chacun avec sa propre numérotation des pages. »), et « Générer le PDF » génère les volumes l'un après l'autre, chacun par une requête `/api/pdf/stream` séparée, sans rien demander. Le découpage suit l'ordre de l'étape Organisation et coupe entre deux chapitres ; un chapitre est coupé seulement s'il dépasse la limite à lui seul, et son titre est alors repris en tête du volume suivant. Chaque volume est un livre complet : couverture au titre « {titre} — Tome {n}/{total} », table des matières, pages de chapitre, numérotation des pages repartant de 1, page de licence ; l'introduction n'est que dans le premier volume, la conclusion que dans le dernier. Les fichiers s'appellent `<nom-du-livre>-1.pdf`, `<nom-du-livre>-2.pdf`, etc. ; le navigateur peut demander l'autorisation de télécharger plusieurs fichiers. La carte de progression affiche « Volume {n} sur {total} » au-dessus de l'étape en cours, et la relance après un plantage reprend le volume en cours, pas le livre entier. Si la limite n'a pas pu être lue (`/api/version` injoignable), le premier refus `too_many_articles` du serveur fournit la limite et la génération repart en volumes. L'API ne change pas : elle génère toujours un livre par requête, et un appelant qui veut des volumes envoie un `Project` par volume.

* **Assemblage dans un processus séparé** : une fois tous les articles téléchargés et recomposés, la suite de la génération (rendus WeasyPrint de la couverture, de la table des matières, des pages de chapitre, de la licence et de la conclusion, puis fusion, signets, liens, numérotation et écriture du PDF final) s'exécute dans un processus séparé, démarré pour cette génération (`app/isolation.py`, méthode `forkserver` : les modules sont chargés une fois pour toutes dans le processus qui démarre les autres). Ce processus envoie la progression au serveur par un tube, écrit le PDF final dans le dossier temporaire, puis se termine : la mémoire de l'assemblage, plusieurs centaines de Mo pour un gros livre (section 13.12), est rendue au système à la fin de chaque génération au lieu de rester au serveur. S'il manque de mémoire et qu'il est arrêté, la génération échoue avec un message explicite (« L'assemblage du livre s'est arrêté (code …), probablement faute de mémoire : essayez avec moins d'articles. ») ; le serveur, lui, n'est arrêté que si la plateforme arrête tout le conteneur. Si l'utilisateur abandonne la génération, le processus est arrêté aussitôt. Chaque étape de l'assemblage est notée, avec la mémoire, dans le journal des générations (section 13.3).

* **Pages générées légères** : la table des matières d'un gros livre est rendue par blocs de 100 entrées (`book_builder.GENERATED_BLOCK_ENTRIES`), chacun dans un rendu WeasyPrint séparé, pour que la mémoire du rendu ne grandisse pas avec le livre ; chaque bloc commence sur une nouvelle page, le titre n'apparaît que dans le premier. La table des matières n'utilise plus de boîte flexible (le numéro de page est placé en flottant), et toutes les pages générées imposent les polices DejaVu Serif et DejaVu Sans. La page de licence ne contient plus la liste des articles : elle tient en une page quelle que soit la taille du livre.

Pendant toute la génération, une fenêtre de statut indique l'étape en cours sous la forme « Étape n / total », avec son libellé (dans la langue de l'interface) et une barre de progression. Les étapes sont, dans l'ordre : le téléchargement de chaque article (une étape par article, avec son titre; jusqu'à 4 articles sont téléchargés en même temps depuis Wikipédia sur Toolforge, 2 sur les autres hébergements (section 13.2), et chaque étape s'affiche au début de son téléchargement — l'ordre des articles dans le livre n'en dépend pas; si un téléchargement échoue, les autres sont abandonnés et l'erreur du premier article en échec, dans l'ordre du livre, est affichée) ou la préparation de chaque document importé, le calcul des numéros de page (si la numérotation est activée), la composition de la couverture et de la table des matières, l'assemblage des pages au format du livre, la numérotation des pages (si activée), la finalisation du fichier, puis le téléchargement du PDF par le navigateur (« Téléchargement du PDF : 45 % », clé `progress.download`, dernière étape, comptée dans le total par le serveur mais affichée par le navigateur au fur et à mesure des octets reçus). Le total est connu dès le départ. Chaque message est envoyé au moment où l'étape commence : la recomposition des articles s'exécute dans un fil d'exécution séparé (`asyncio.to_thread`) et l'assemblage dans un processus séparé, ce qui laisse le serveur libre d'envoyer la progression et de répondre aux autres utilisateurs pendant une génération. La fenêtre se ferme à la fin, en cas de succès comme d'échec.

Côté serveur, cette progression est transmise par l'endpoint `POST /api/pdf/stream`, qui renvoie un flux NDJSON (une ligne JSON par événement) : `{"type": "progress", "step", "total", "code", "title"?}` pour chaque étape, `{"type": "wait", "seconds"}` au début de chaque pause imposée par Wikimédia (section 8; durée arrondie à la seconde supérieure, ne compte pas comme une étape), puis `{"type": "done", "size"}` immédiatement suivi des `size` octets du PDF, en binaire et sans encodage (envoyés par morceaux de 256 Ko), ou `{"type": "error", "detail"}` en cas d'échec en cours de génération. Le navigateur lit les lignes JSON jusqu'au message `done`, puis rassemble les octets du PDF; s'il en reçoit moins que `size`, il affiche « la connexion avec le serveur a été interrompue avant la fin ». **Relance après un plantage** : quand la génération est coupée par un plantage du serveur — connexion perdue ou flux interrompu avant la fin, serveur injoignable, ou réponse 502, 503 ou 504 du proxy pendant un redémarrage (« no healthy upstream » sur Toolforge) —, le navigateur attend que le serveur réponde de nouveau à `GET /health` (vérifié toutes les 3 s, au plus 2 min), puis relance la génération depuis le début, avec un message dans la fenêtre de statut (« Le serveur a été interrompu : nouvel essai n° 1, la génération repart de zéro… »). Il le fait deux fois automatiquement ; au-delà, il demande à l'utilisateur avant chaque nouvel essai, et s'arrête sur l'erreur s'il refuse. Une erreur renvoyée par le serveur lui-même (événement `error` : article introuvable, refus de Wikipédia, requête invalide…) n'est jamais relancée : elle s'affiche aussitôt. Une sélection vide est refusée avant le début du flux (erreur HTTP 400). L'endpoint `POST /api/pdf`, qui renvoie directement le fichier PDF sans progression, reste disponible pour un usage direct de l'API.

Deux endpoints de génération de haut niveau renvoient également directement un fichier PDF : `POST /api/books/generate` reçoit une liste explicite de références d'articles (titre ou URL), les métadonnées et les principaux réglages de mise en page; `POST /api/books/generate-from-wikipedia-book` reçoit l'URL d'une page de livre Wikipédia et un titre de livre facultatif. Dans ce dernier cas, tous les articles listés par Wikipédia sont inclus dans leur ordre d'apparition et sélectionnés pour la génération, avec les chapitres (lignes `;`) et, sauf si `book_subtitle` est fourni, le sous-titre (ligne `=== … ===`) de la page de livre, comme pour l'import dans l'interface (section 3.1). `POST /api/books/structure` renvoie cette lecture sans générer de PDF (`articles`, `subtitle`, `chapters` au format des chapitres du livre, `unassigned_first` vrai quand des articles précèdent le premier chapitre); `POST /api/books/import` renvoie seulement la liste des articles. Sans `book_title`, le titre du livre (couverture, signet, nom du fichier PDF) est la dernière partie du nom de la page de livre : `Utilisateur:X/Livres/Les épaves` donne « Les épaves », `Livre:Animaux` donne « Animaux ». Le paramètre `book_conclusion` (GET et POST) fixe le texte de la page de conclusion; il est vide par défaut (pas de page de conclusion), comme dans l'interface web. Ces endpoints ne conservent aucun livre côté serveur.

### 11.2 Résultat

Le PDF produit est :

* Imprimable et structuré par des signets de navigation.

* Conforme, sur toutes ses pages, au format et à l'orientation choisis pour le livre.

* Fidèle au contenu du PDF officiel Wikipédia pour les articles, et de chaque document importé.

* Compatible avec les lecteurs PDF courants.

### 11.3 Gestion des erreurs

En cas d'échec, le logiciel affiche un message explicite. Les erreurs possibles sont :

* Aucun article sélectionné avant l'export.

* URL, titre d'article ou code de langue invalide.

* Page de livre ou article introuvable sur Wikipédia.

* Impossible de joindre l'API Wikipédia, ou PDF officiel indisponible/invalide pour un article : la génération échoue dans son ensemble, sans produire de livre partiel.

* Échec inattendu pendant l'assemblage du PDF.

## 12\. Interface utilisateur

L'application est une page unique, organisée en trois étapes accessibles par des onglets. Les onglets des étapes sont affichés directement sous la barre supérieure : le titre du livre et la note de couverture ne sont pas affichés au-dessus des étapes, ils se saisissent uniquement dans l'étape Édition (partie A, « Identité du livre »).

**Titre par défaut :** si le champ « Titre du livre » est laissé vide, le titre utilisé (couverture, signet racine, nom des fichiers PDF et JSON) est celui du premier article Wikipédia du livre, dans l'ordre défini à l'étape Organisation (à défaut d'article Wikipédia, le premier document importé). Ce titre par défaut est affiché en grisé dans le champ vide, pour que l'utilisateur sache ce qui sera imprimé; il est calculé au moment de la génération et n'est pas enregistré dans le livre. Un titre importé d'une page de livre Wikipédia (section 3.1) ou saisi par l'utilisateur est toujours prioritaire.

* 01 — Sources : ajout des articles principaux (affichés sous le titre « Vos articles ») et exploration des liens (articles découverts, affichés sous le titre « Suggestions »).

* 02 — Organisation : réorganisation des articles, documents importés, chapitres et volumes.

* 03 — Édition : identité du livre (titre, sous-titre, auteur, note de couverture, introduction, conclusion, images de fond de la couverture et de la dernière page), table des matières (aucune, au début, à la fin) et format d'impression (format papier, orientation, préréglage de marges, numérotation des pages).

En bas des étapes Sources et Organisation, un bouton « Étape suivante : … » ouvre l'étape suivante et remonte en haut de la page.

Le logo de la barre supérieure s'agrandit à 5 cm de côté au survol de la souris, puis reprend sa taille.

Le pied de page affiche le logo, l'état de connexion à l'API, un lien vers le dépôt Git du projet (https://github.com/gmoulard/wikipedia2book, ouvert dans un nouvel onglet) puis le numéro de version, le commit, la date et l'auteur du déploiement.

Une barre supérieure permet à tout moment d'ouvrir un livre enregistré (bouton « Ouvrir », import JSON), d'enregistrer le livre sur son ordinateur (bouton « Enregistrer », export JSON) et de lancer la génération du PDF. Elle indique aussi si le livre en cours a été enregistré. Sur smartphone, les boutons « Ouvrir » et « Enregistrer » ne montrent que leur icône et le nom de l'application est masqué, pour que la barre tienne dans la largeur de l'écran.

L'interface est utilisable sur ordinateur, tablette et smartphone, et respecte le thème clair/sombre du système.

Son apparence reprend le système de design Codex de Wikimedia (couleurs, boutons, onglets, champs, coins à 2 px, polices système sans-serif et titres en serif comme sur Wikipédia), pour s'intégrer à l'environnement Wikimedia. Aucune police ni ressource n'est chargée depuis un service tiers (pas de Google Fonts).

### 12.1 Langues de l'interface

L'interface (libellés, boutons, messages) est disponible en français, anglais, espagnol, portugais, italien, allemand, néerlandais, turc, chinois, japonais, arabe et persan, via un sélecteur dans la barre supérieure. L'arabe et le persan s'affichent de droite à gauche : toute la page passe alors en sens d'écriture `rtl` (attribut `dir` du document), et revient en `ltr` pour les autres langues. La langue choisie est mémorisée dans le navigateur (elle n'est pas enregistrée dans le livre ni dans l'export JSON) et détectée automatiquement à la première visite à partir de la langue du navigateur, avec repli sur l'anglais quand celle-ci ne fait pas partie des 12 langues.

Cette langue d'interface est indépendante de la langue des articles Wikipédia (section 3), qui reste un réglage séparé par article. Elle ne s'applique pas aux messages d'erreur renvoyés par le serveur. En revanche, elle est transmise au serveur au moment de la génération du PDF (paramètre `language` de `/api/pdf` et `/api/pdf/stream`, français par défaut, toute autre valeur que les 12 langues de l'interface est refusée) : les titres et libellés ajoutés par l'application dans le PDF sont alors rédigés dans cette langue — « Introduction », « Table des matières », mention « Chapitre » des pages de chapitre, « Sans chapitre », « Conclusion », « Licence », la mention « Édition du … » placée sous le logo en fin de livre, ainsi que les signets correspondants. Les pages générées portent la langue choisie (attribut `lang`) et passent en écriture de droite à gauche pour l'arabe et le persan. La page de licence est entièrement rédigée dans cette langue : nom officiel traduit de la licence CC BY-SA 4.0, lien vers la version de l'acte de licence dans cette langue sur creativecommons.org, conditions de réutilisation, mentions sur les médias, les documents importés et le caractère non officiel du livre. Le texte saisi par l'utilisateur (titre, introduction, conclusion, titres de chapitre) et le contenu des articles Wikipédia ne sont jamais traduits.

### 12.2 Page d'administration

Page de suivi du service réservée aux administrateurs, à l'adresse `/admin` (par exemple https://wikipedia2book.toolforge.org/admin). Elle n'est liée depuis aucune page de l'interface et n'est pas indexée par les moteurs de recherche (`noindex`).

* **Connexion par le compte Wikimédia** (OAuth 2.0 de Meta-Wiki, application « identification seulement » : elle ne permet ni de lire ni de modifier quoi que ce soit au nom de l'utilisateur) :
  1. le bouton « Se connecter avec Wikimédia » mène à `/admin/login`, qui renvoie vers `https://meta.wikimedia.org/w/rest.php/oauth2/authorize` avec un état aléatoire, gardé 10 minutes dans un cookie signé (`w2b_oauth_state`) ;
  2. Wikimédia renvoie vers `/admin/callback`, qui vérifie l'état, échange le code contre un jeton (`oauth2/access_token`), puis lit le nom d'utilisateur (`oauth2/resource/profile`) ;
  3. si ce nom figure dans la liste des administrateurs, un cookie de session signé est posé (`w2b_admin` : HttpOnly, Secure en HTTPS, SameSite=Lax, limité au chemin `/admin`, 2 heures). Sinon la page affiche « Ce compte Wikimédia n'est pas administrateur de Wikipedia2Book. », sans session.
  * Le jeton Wikimédia n'est pas gardé. Le serveur reste sans état : la session tient tout entière dans le cookie, signé par une clé tirée au démarrage du serveur. Un redémarrage invalide donc les sessions, et il faut se reconnecter.
  * Chaque appel vérifie que le nom figure toujours dans la liste. `/admin/logout` efface le cookie.
* **Administrateurs** : variable `WIKIPEDIA2BOOK_ADMINS`, noms d'utilisateur Wikimédia écrits en hexadécimal UTF-8 et séparés par des virgules. Pour obtenir la valeur d'un nom : `python -c "print('Exemple'.encode().hex())"`. Sans la variable, deux comptes par défaut ; une valeur invalide empêche le démarrage. Les noms sont comparés comme sur MediaWiki (première lettre en majuscule, `_` lu comme une espace).
* **Configuration** :
  * `WIKIPEDIA2BOOK_OAUTH_CLIENT_ID` et `WIKIPEDIA2BOOK_OAUTH_CLIENT_SECRET` : application OAuth 2.0 enregistrée sur [Special:OAuthConsumerRegistration](https://meta.wikimedia.org/wiki/Special:OAuthConsumerRegistration/propose/oauth2), en « User identity verification only », approuvée automatiquement ;
  * `WIKIPEDIA2BOOK_OAUTH_CALLBACK` : l'adresse de retour enregistrée dans l'application, `https://wikipedia2book.toolforge.org/admin/callback` pour Toolforge (posée dans le `Procfile`).
  * Il faut une application par hébergement, puisque l'adresse de retour diffère. Sans ces trois valeurs, la page indique que la connexion n'est pas configurée.
* **Indicateurs**, actualisés toutes les 30 s :
  * **Système et conteneur** : hôte, plateforme, système, version de Python, durée de fonctionnement, processeurs et limite du conteneur (`cpu.max`), charge sur 1, 5 et 15 minutes, temps processeur du serveur, fils d'exécution, fichiers ouverts, processus et leur limite (`pids.current`, `pids.max`), arrêts faute de mémoire (`oom_kill` de `memory.events`), processus de recomposition, versions des bibliothèques (FastAPI, Starlette, Uvicorn, Pydantic, httpx, WeasyPrint, pypdf, PyMuPDF, Pillow, reportlab) ; une valeur absente (hors Linux, sans cgroup) s'affiche « — ».
  * **Serveur** : version et commit, démarrage, générations en cours, mémoire du conteneur et sa limite, mémoire du processus, espace temporaire libre, étapes en attente (mémoire, disque, entrée). Ce sont les données de `/api/health/details`.
  * **Utilisation** : requêtes sur 24 et 48 heures, générations par statut, articles et documents des dernières générations.
  * **Performance**, sur les générations réussies : durée médiane, à 90 % et maximale, médiane par article, taille médiane du PDF, pic de mémoire d'une génération, attente « Serveur occupé » cumulée.
  * **Limites et alertes** : réglages du serveur et franchissements de limites.
  * **Dernières générations** (journal, début, statut, durée, articles, taille, attente, pic de mémoire, version) et **requêtes par heure**. Le numéro de chaque génération ouvre sa page de détail (`/admin/generation?id=<n>`) : résumé (statut, début, durée, taille, version, langue, articles, documents, chapitres, format, numérotation, table des matières, erreur), **téléchargements** (type, adresse téléchargée, taille, durée du téléchargement, durée de la recomposition, pages, moment), **étapes** (moment, étape, processus, mémoire, détails) un bouton « Télécharger le journal (JSON) » qui enregistre le journal de cette génération (`/admin/api/generations/{id}`) et un bouton « Télécharger la demande (JSON) » qui enregistre le livre demandé, au format des fichiers de l'interface (`wikipedia2book-workspace`, à rouvrir avec « Ouvrir » pour reproduire la génération ; `/admin/api/generations/{id}/request`). Le contenu des images et documents importés depuis l'ordinateur n'y est pas gardé (`data_base64` vide, `removed_base64_chars` donne sa taille) ; une demande de plus de 1 Mo n'est pas gardée, et les demandes les plus anciennes sont oubliées au-delà de 30 Mo en tout ou quand leur génération sort du journal (message « La demande de cette génération n'est plus en mémoire… »).
  * **Adresses refusées** : les 500 dernières adresses (`http…`) refusées par Wikipedia2Book (erreurs 4xx de `/api/sources/resolve`, `/api/articles`, `/api/books/structure`, `/api/pdf/from-source`, `/api/pdf/from-json` : adresse hors Wikimédia, page introuvable, page qui n'est pas une page de contenu…), avec le dernier refus, le nombre de refus, le code HTTP et le motif. Une erreur de Wikimédia (5xx) n'y figure pas.
  * Toutes ces données sont en mémoire seulement, sans adresse IP : 48 heures de requêtes, jusqu'aux 1 000 dernières générations avec leurs demandes et les 500 dernières adresses refusées, perdues au redémarrage.
* **API** : `GET /admin/api/session` donne `configured` (connexion configurée) et `user` (administrateur connecté, ou `null`) ; `GET /admin/api/summary` donne tous les indicateurs (`user`, `version`, `server`, `settings`, `usage`, `performance`, `recent`), jamais mis en cache, avec la session d'administrateur seulement (sinon HTTP 401, `detail.code` = `admin_login_required`). Ni l'un ni l'autre n'est compté dans les requêtes par heure. `GET /admin/api/generations/{id}` donne le journal d'une génération et `GET /admin/api/generations/{id}/request` sa demande (fichier JSON en pièce jointe, 404 si elle n'est plus en mémoire), avec la même session ; `summary` contient aussi `refused_urls`. Ces routes n'apparaissent pas dans la description publique de l'API (`/docs`, `/openapi.json`). `/api/health/details` et `/api/health/generations` sont réservés à la supervision par jeton (section 13.3).
* **Protections** :
  * en-têtes de sécurité sur `/admin`, `/admin/*` et `/api/health/*` : `Content-Security-Policy` (aucune source extérieure, pas d'affichage dans le cadre d'un autre site), `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`, `Referrer-Policy: no-referrer` ;
  * `/admin/login` et `/admin/callback`, qui ne demandent aucune identification, sont limités en nombre d'appels par minute ; au-delà, « Trop de tentatives de connexion : réessayez dans une minute. » et une alerte ;
  * la page et ses API ne font que lire : aucune action ne modifie le serveur.
* Textes dans les 12 langues de l'interface (clés `admin.*`). Tests : `tests/test_admin.py`.

## 15\. Respect des licences Wikipédia

Le logiciel doit respecter les licences applicables aux contenus récupérés depuis Wikipédia.

Les textes Wikipédia sont généralement publiés sous licence Creative Commons Attribution-Partage dans les Mêmes Conditions (CC BY-SA). Chaque article conserve, dans le PDF officiel Wikipédia intégré au livre, les mentions de licence et d'attribution telles que générées par Wikipédia elle-même.

Le logiciel :

* Conserve le lien vers chaque article original.

* Ajoute au livre une page « Licence », juste après la conclusion, qui indique que les textes de Wikipédia et des autres projets sous la même licence (Wikilivres, Wikivoyage, Wikiversité, Wikiquote, Wiktionnaire) sont sous licence Creative Commons Attribution – Partage dans les mêmes conditions 4.0 International (CC BY-SA 4.0), en nommant les projets présents dans le livre, avec le lien vers la licence, un résumé des conditions de réutilisation, et une phrase indiquant que les auteurs de chaque article sont crédités par le lien vers sa source placé à la fin de l'article (« Ce document provient de… » dans le PDF de Wikipédia : lien permanent vers la version reproduite, dont l'historique recense les auteurs). Elle ne reprend plus la liste des articles avec leur adresse et celle de leur historique (« Sources et auteurs », jusqu'en 1.9.4), redondante avec ce lien. Les documents importés y sont cités comme non couverts par cette licence. Si le livre contient des textes de Wikisource, la page précise qu'ils sont pour la plupart dans le domaine public, les autres (traductions, éditions récentes) étant sous la licence indiquée sur leur page Wikisource, en général CC BY-SA 4.0; s'il contient des articles de Wikinews, qu'ils sont sous licence Creative Commons Attribution (CC BY), dans la version indiquée sur leur page; la mention CC BY-SA n'est affichée que si le livre contient au moins une page d'un projet sous cette licence. Cette page rappelle aussi que le livre n'est pas une publication officielle des projets dont il reprend des pages (Wikipédia par défaut) ni de la Wikimedia Foundation; les noms des projets y sont ceux de la langue de l'interface (`site_*` de `PDF_LABELS`, par exemple « Wikilivres » en français, « Wikibooks » en anglais); elle est entièrement rédigée dans la langue de l'interface (section 12.1).

* N'altère pas le contenu, les crédits ni les mentions de licence imprimés par Wikipédia dans son propre PDF.

* Ne présente pas le livre généré comme une publication officielle de Wikipédia.

Les images et médias intégrés par Wikipédia à son export PDF conservent leurs propres mentions de licence; le logiciel ne les extrait pas séparément et n'effectue pas de vérification de licence indépendante.

## 16\. Critères d'acceptation

La version actuelle est considérée comme fonctionnelle si les points suivants sont validés :

* Ajout de plusieurs articles principaux (URL, titre, recherche, page de livre Wikipédia) depuis un champ unique, le type de saisie étant reconnu automatiquement.

* Exploration des liens internes avec profondeur paramétrable (API).

* Détection des doublons parmi les articles découverts.

* Affichage des liens d'un article dans l'ordre de la page ou par ordre alphabétique, filtre par titre et ajout au livre en un clic.

* Sélection manuelle des articles; aucun ajout automatique d'article découvert.

* Réorganisation des articles et création de chapitres.

* Import d'une page de livre Wikipédia en conservant l'ordre réel des articles, son sous-titre et ses chapitres.

* Import d'images ou de PDF comme documents intégrés au livre, au même titre que des articles.

* Positionnement de la table des matières n'importe où dans le livre, ou retrait.

* Récupération du PDF officiel de chaque article sélectionné au moment de l'export.

* Choix du format papier, de l'orientation et des marges, y compris la marge de reliure.

* Génération d'un PDF imprimable dont toutes les pages respectent le format et l'orientation choisis, avec couverture, table des matières, signets de navigation et pagination (activée par défaut); la table des matières indique alors la page de chaque chapitre et de chaque article.

* Le bouton de génération du PDF est toujours visible et actif.

* Téléchargement du PDF généré.

* Export puis import du livre via un fichier JSON local, nommé d'après le titre du livre.

* Changement de la langue de l'interface (12 langues, section 12.1) sans rechargement de la page.

* Proposition automatique, non destructive, de l'introduction et de l'auteur du livre à partir du premier article ajouté.

## 18\. État d'avancement et évolutions futures

L'essentiel du socle fonctionnel décrit dans ce document est implémenté : livre unique en mémoire, ajout et exploration des articles, sélection manuelle, organisation en chapitres, formats et marges configurables, génération du PDF avec signets de navigation.

Évolutions envisageables, non implémentées à ce jour :

* Filtrage de l'exploration par langue ou par catégorie d'article.

* Journalisation des erreurs et limitation du débit des requêtes API.

* Couverture de tests automatisés plus large (aujourd'hui : syntaxe Python, numérotation des pages/table des matières, documents importés, API Wikipédia, traductions, script de statistiques Toolviews, et déroulement de `/api/pdf` et `/api/pdf/stream` via `tests/test_pdf_stream.py` — avec Wikipédia et WeasyPrint simulés : le rendu réel des pages par WeasyPrint et l'interface ne sont pas couverts).

* Caractères chinois rares (僻字) dans le PDF officiel de Wikisource : vérifié en novembre 2026, une partie des caractères des extensions CJK B et suivantes y laisse un blanc (police LiberationSerif sans glyphe, par exemple 𡼢 U+21F22 dans « 大南寔錄/大南寔錄前編/卷10 » de zh.wikisource.org), seuls ceux que Wikisource fournit en image s'affichent ; l'application ne modifie pas ce PDF : à signaler à Wikimédia (Phabricator, service PDF). Demande exprimée par PacmanD sur le Bistro technique de la Wikipédia en chinois (novembre 2026), dont l'autre partie — importer une œuvre entière depuis sa page sommaire — est faite (section 3.1).

Toute évolution doit préserver les principes fondamentaux du logiciel, notamment le contrôle total de l'utilisateur sur la sélection des articles et la gestion d'un seul livre à la fois.
