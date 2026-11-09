# Wikipedia2Book — Spécifications fonctionnelles et techniques

Version : 1.1 — Statut : aligné sur l'implémentation actuelle — Format : Markdown (`.md`)

## 1\. Présentation de Wikipedia2Book

### 1.1 Objectif

Wikipedia2Book est un logiciel qui permet de créer directement un livre au format PDF imprimable à partir d'articles Wikipédia : il n'y a pas d'étape de création ou de gestion de « projet », l'utilisateur commence immédiatement à construire son livre.

Dès l'ouverture de l'application, un livre vide est prêt à l'emploi. L'utilisateur ajoute un ou plusieurs articles principaux, explore les articles qui leur sont liés, choisit précisément les contenus à intégrer, organise les articles en chapitres et génère un document PDF structuré.

Le logiciel fonctionne sur toutes les plateformes grâce à une architecture Python conteneurisée avec Docker.

### 1.2 Principes fondamentaux

* Le logiciel n'est pas limité à un thème ou à une catégorie d'articles.

* Plusieurs articles principaux peuvent être ajoutés à un même livre.

* L'exploration des liens Wikipédia est paramétrable (profondeur, nombre maximal d'articles).

* Aucun article découvert n'est ajouté automatiquement au livre.

* L'utilisateur garde le contrôle total sur la sélection des articles.

* Le format du livre est configurable (dimensions, orientation, marges).

* Le PDF produit est adapté à l'impression.

## 2\. Le livre en mémoire et sa sauvegarde

Le logiciel ne gère pas de liste de projets : un seul livre est construit à la fois, entièrement en mémoire dans le navigateur.

* À l'ouverture de l'application, un livre vide est créé automatiquement; l'utilisateur peut lui donner un nom et une description.

* Toutes les modifications (articles, sélection, organisation, mise en page) sont conservées en mémoire dans le navigateur pendant la session, et envoyées à l'API uniquement pour les opérations qui le nécessitent (recherche, exploration, génération du PDF).

* L'utilisateur peut télécharger explicitement l'état du livre sous forme de fichier JSON.

* L'utilisateur peut importer un fichier JSON précédemment téléchargé pour reprendre un livre; l'import remplace le livre en cours.

* Le serveur ne persiste aucun livre ni fichier sur son disque : la persistance est entièrement à la charge de l'utilisateur, via le téléchargement puis l'import manuel du fichier JSON.

Le livre contient notamment :

* Les articles principaux.

* Les articles découverts.

* La sélection des articles.

* La structure du livre (ordre, chapitres, position de la table des matières).

* Les paramètres de mise en page.

* Les informations de couverture (titre, sous-titre, auteur, introduction, conclusion).

## 3\. Ajout des articles

### 3.1 Méthodes d'ajout

L'utilisateur ajoute des articles à son livre par l'un des moyens suivants :

* URL d'un article Wikipédia.

* Titre d'article saisi directement.

* Recherche dans Wikipédia : des résultats sont proposés au fil de la saisie, à ajouter d'un clic.

* URL d'une page de « livre » Wikipédia listant des articles : tous les articles qu'elle référence sont importés et pré-sélectionnés. Seuls leur titre et leur URL sont chargés à ce stade; leur PDF complet n'est téléchargé qu'au moment de la génération.

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

## 4\. Exploration des articles liés

### 4.1 Principe

Le logiciel explore les liens internes présents dans les articles principaux afin de proposer des articles complémentaires, en s'appuyant sur l'API officielle MediaWiki (`action=query&prop=links`).

### 4.2 Profondeur d'exploration

La profondeur est paramétrable, entre 0 et 3 :

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

* L'article principal qui a conduit à sa découverte.

* Sa profondeur de découverte.

* Son statut de sélection.

Les doublons sont éliminés automatiquement (comparaison insensible à la casse sur la langue et le titre), y compris lorsqu'un même article est lié depuis plusieurs pages.

### 4.4 Limites de l'exploration

L'utilisateur peut limiter :

* Le nombre maximal d'articles découverts (entre 1 et 200, 30 par défaut).

* La profondeur maximale (entre 0 et 3, 1 par défaut).

## 5\. Sélection des articles

Cette fonctionnalité est essentielle.

Aucun article découvert ne doit être intégré automatiquement au livre.

Le logiciel présente la liste des articles découverts et laisse l'utilisateur choisir exactement ceux qu'il souhaite conserver.

Fonctionnalités disponibles :

* Sélection individuelle.

* Désélection individuelle.

* Tout sélectionner (parmi les articles découverts).

* Sélectionner les visibles (respecte les filtres actifs).

* Tout désélectionner.

* Recherche par titre parmi les articles découverts.

* Filtrage par article d'origine.

* Filtrage par profondeur de découverte.

La sélection est conservée avec le reste du livre, en mémoire et dans l'export JSON.

## 6\. Organisation du livre

L'utilisateur organise les articles sélectionnés avant la génération du PDF.

Fonctionnalités :

* Réordonner les articles par glisser-déposer.

* Créer des chapitres et leur donner un titre.

* Déplacer un article d'un chapitre à un autre, ou hors de tout chapitre, par glisser-déposer.

* Positionner la table des matières au début ou à la fin du livre, également par glisser-déposer.

* Ajouter une introduction générale et une conclusion.

* Activer ou non la numérotation des pages.

Un article peut être déplacé librement dans la structure du livre.

## 7\. Récupération du contenu Wikipédia

L'ajout et l'exploration ne téléchargent pas le contenu complet des pages. Au moment de générer le PDF, chaque article sélectionné est récupéré via l'endpoint PDF officiel de Wikimedia (`/api/rest_v1/page/pdf/{titre}`), équivalent à la fonction « Télécharger comme PDF » de Wikipédia.

Le PDF officiel de chaque article est conservé intégralement, avec son contenu, sa structure, ses images et ses références. Les PDFs sont assemblés dans l'ordre du livre sans reconstruire ni tronquer le corps des articles.

## 8\. Références, images et licences

Le logiciel ne reconstruit pas le contenu des articles : chaque article sélectionné est intégré sous la forme du PDF officiel généré par Wikipédia. En conséquence :

* Les références et citations restent exactement celles du PDF Wikipédia, avec leur mise en forme d'origine.

* Les images et leurs légendes sont celles intégrées par Wikipédia à l'export PDF, avec leur mise en page d'origine.

* Les crédits et licences des textes et des images sont ceux imprimés par Wikipédia dans son propre PDF; le logiciel ne les extrait pas et ne les réécrit pas séparément.

* Si Wikipédia ne peut pas produire de PDF pour un article sélectionné (page introuvable, service indisponible, réponse invalide), la génération du livre échoue dans son ensemble et un message d'erreur explicite est affiché; aucun livre partiel n'est produit.

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

L'utilisateur règle indépendamment :

* La marge supérieure.

* La marge inférieure.

* La marge intérieure.

* La marge extérieure.

* La marge de reliure, en complément de la marge intérieure.

## 10\. Mise en page du livre

Le PDF est structuré comme un véritable livre.

Éléments générés par l'application :

* Couverture (titre du livre, sous-titre, auteur, note, date de génération).

* Introduction, si elle a été saisie.

* Table des matières, groupée par chapitre.

* Pages de titre de chapitre, pour chaque chapitre contenant des articles.

* Conclusion, si elle a été saisie.

Les articles eux-mêmes ne sont pas mis en page par l'application : ce sont les pages du PDF officiel Wikipédia, insérées telles quelles.

Point important : les pages générées par l'application (couverture, introduction, table des matières, pages de chapitre, conclusion) suivent le format, l'orientation et les marges configurés; les pages d'articles conservent intégralement la mise en page du PDF Wikipédia d'origine, quel que soit le format choisi pour le reste du livre.

La navigation dans le PDF final s'appuie sur des signets (une entrée par chapitre et par article), et non sur les liens de la table des matières.

### 10.1 Numérotation des pages

Quand l'option « Numéroter les pages » est activée (section 6) :

* Toutes les pages du livre affichent un numéro en bas de page, de façon continue — y compris les pages d'articles (PDF officiel Wikipédia), à l'exception de la couverture.

* La table des matières affiche, pour chaque chapitre et chaque article, le numéro de la page où il commence.

* Pour calculer ces numéros avant d'assembler le livre, le logiciel génère la couverture/introduction/table des matières une première fois pour en mesurer la pagination, puis la régénère avec les numéros corrects. Dans de rares cas (livre très dense), l'ajout des numéros dans la table des matières peut légèrement décaler cette pagination d'une page.

Aucune fonctionnalité de prévisualisation n'est proposée actuellement.

## 11\. Génération du PDF

### 11.1 Déroulement

Une fois les articles sélectionnés et organisés, l'utilisateur lance la génération du PDF. Le logiciel :

* Vérifie qu'au moins un article est sélectionné; sinon, la génération est refusée.

* Télécharge le PDF officiel de chaque article sélectionné.

* Si la numérotation des pages est activée, calcule à l'avance la page de départ de chaque chapitre et de chaque article (section 10.1).

* Génère la couverture, l'introduction éventuelle et la table des matières (avec les numéros de page si activés), avec un signet racine portant le titre du livre.

* Pour chaque chapitre (ou pour l'ensemble des articles s'il n'y a pas de chapitre) : génère une page de titre de chapitre avec son propre signet, puis ajoute le PDF officiel de chaque article du chapitre, avec un signet par article.

* Ajoute une page de conclusion avec signet, si une conclusion a été saisie.

* Si la numérotation des pages est activée, superpose un numéro de page en bas de chaque page du document assemblé (sauf la couverture).

* Fusionne l'ensemble en un seul fichier PDF et le rend accessible au téléchargement, nommé d'après le titre du livre.

### 11.2 Résultat

Le PDF produit est :

* Imprimable et structuré par des signets de navigation.

* Conforme au format choisi pour ses pages de couverture, de chapitre et de conclusion.

* Fidèle au PDF officiel Wikipédia pour ses pages d'articles.

* Compatible avec les lecteurs PDF courants.

### 11.3 Gestion des erreurs

En cas d'échec, le logiciel affiche un message explicite. Les erreurs possibles sont :

* Aucun article sélectionné avant l'export.

* URL, titre d'article ou code de langue invalide.

* Page de livre ou article introuvable sur Wikipédia.

* Impossible de joindre l'API Wikipédia, ou PDF officiel indisponible/invalide pour un article : la génération échoue dans son ensemble, sans produire de livre partiel.

* Échec inattendu pendant l'assemblage du PDF.

## 12\. Interface utilisateur

L'application est une page unique, organisée en trois étapes accessibles par des onglets, sans écran de création ou de gestion de projet :

* 01 — Sources : ajout des articles principaux et exploration des liens.

* 02 — Organisation : réorganisation des articles, chapitres, position de la table des matières.

* 03 — Édition : identité du livre (titre, sous-titre, auteur, introduction, conclusion) et format d'impression.

Une barre supérieure permet à tout moment d'importer ou d'exporter le livre en JSON et de lancer la génération du PDF.

L'interface est utilisable sur ordinateur, tablette et smartphone, et respecte le thème clair/sombre du système.

## 13\. Architecture technique

### 13.1 Technologies

| Composant        | Technologie utilisée    |
| ----------------- | ------------------------------------------------------------ |
| Langage           | Python 3.12                                                   |
| Backend           | FastAPI + Uvicorn                                             |
| Client HTTP       | httpx (appels à l'API MediaWiki et à l'endpoint PDF)          |
| Analyse HTML      | BeautifulSoup4 (extraits de recherche)                        |
| Interface         | HTML, CSS, JavaScript (page unique, sans framework)           |
| API Wikipédia     | API MediaWiki (`action=query`) + endpoint REST `page/pdf`     |
| Échange du livre  | JSON navigateur ↔ API                                         |
| Génération PDF    | PDF officiel Wikimedia (articles) + WeasyPrint (couverture, chapitres, conclusion) + pypdf (fusion, signets, lecture du nombre de pages) + reportlab (superposition des numéros de page) |
| Conteneurisation  | Docker                                                        |

### 13.2 API Wikipédia

Le logiciel utilise les interfaces officielles de MediaWiki pour :

* Rechercher des articles (`action=query&list=search`).

* Résoudre les URL d'article et valider les codes de langue.

* Explorer les liens internes (`action=query&prop=links`).

* Récupérer la liste des articles d'une page de livre (`prop=info|links`, avec pagination `continue`).

* Télécharger le PDF officiel de chaque article sélectionné, au moment de l'export (`/api/rest_v1/page/pdf/{titre}`).

Chaque requête utilise un en-tête `User-Agent` dédié; les délais d'attente sont bornés (20 secondes pour les appels à l'API, 120 secondes pour le téléchargement d'un PDF).

### 13.3 Docker et déploiement

Le logiciel est livré avec :

* Un `Dockerfile` (image Python 3.12-slim avec les dépendances système de WeasyPrint).

* Un fichier `requirements.txt`.

* Un script `docker-build.sh` qui construit l'image en y injectant le commit, la date et l'auteur git courants, affichés en pied de page de l'application.

Exemple :

```bash
sh docker-build.sh
docker run --rm -p 8000:8000 wikipedia2book
```

L'application est alors accessible sur `http://localhost:8000`, avec sa documentation interactive sur `http://localhost:8000/docs`.

Le serveur ne stocke aucun livre ni PDF sur disque; tout l'état est conservé dans le navigateur et échangé via JSON.

## 14\. Sécurité et robustesse

Le logiciel met en œuvre aujourd'hui :

* La validation stricte des URL fournies (schéma HTTPS, domaine `*.wikipedia.org`, titre présent).

* La validation des codes de langue (expression régulière, 2 à 12 caractères).

* La validation des champs de formulaire (longueurs minimales/maximales, exclusivité titre/URL) au niveau de l'API.

* La gestion des erreurs réseau vers Wikipédia, traduites en messages explicites côté interface.

* Des délais d'attente bornés sur les appels réseau.

* Aucun contenu HTML d'article n'est interprété ni réinjecté par l'application : seuls le PDF officiel Wikipédia (binaire) et les champs texte validés par l'API transitent par le serveur.

Les URL externes ne sont jamais exécutées comme du code.

Points non couverts par l'implémentation actuelle, à considérer pour une version ultérieure : limitation du débit des requêtes vers l'API Wikipédia, journalisation structurée des erreurs, quotas explicites sur la taille des PDFs téléchargés.

## 15\. Respect des licences Wikipédia

Le logiciel doit respecter les licences applicables aux contenus récupérés depuis Wikipédia.

Les textes Wikipédia sont généralement publiés sous licence Creative Commons Attribution-Partage dans les Mêmes Conditions (CC BY-SA). Chaque article conserve, dans le PDF officiel Wikipédia intégré au livre, les mentions de licence et d'attribution telles que générées par Wikipédia elle-même.

Le logiciel :

* Conserve le lien vers chaque article original.

* N'altère pas le contenu, les crédits ni les mentions de licence imprimés par Wikipédia dans son propre PDF.

* Ne présente pas le livre généré comme une publication officielle de Wikipédia.

Les images et médias intégrés par Wikipédia à son export PDF conservent leurs propres mentions de licence; le logiciel ne les extrait pas séparément et n'effectue pas de vérification de licence indépendante.

## 16\. Critères d'acceptation

La version actuelle est considérée comme fonctionnelle si les points suivants sont validés :

* Ajout de plusieurs articles principaux (URL, titre, recherche, page de livre Wikipédia).

* Exploration des liens internes avec profondeur paramétrable.

* Détection des doublons parmi les articles découverts.

* Affichage des articles découverts avec leurs filtres (origine, profondeur, titre).

* Sélection manuelle des articles; aucun ajout automatique d'article découvert.

* Réorganisation des articles et création de chapitres.

* Positionnement de la table des matières au début ou à la fin.

* Récupération du PDF officiel de chaque article sélectionné au moment de l'export.

* Choix du format papier, de l'orientation et des marges, y compris la marge de reliure.

* Génération d'un PDF imprimable avec couverture, table des matières, signets de navigation et pagination optionnelle; quand la pagination est activée, la table des matières indique la page de chaque chapitre et de chaque article.

* Téléchargement du PDF généré.

* Export puis import du livre via un fichier JSON local.

## 17\. Structure du projet

```text
Wikipedia2Book/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── models.py
│   ├── wikipedia_api.py
│   ├── explorer.py
│   ├── book_builder.py
│   ├── pdf_generator.py
│   │
│   └── static/
│       ├── index.html
│       ├── styles.css
│       ├── app.js
│       └── Wikipedia2bookLogo.png
│
├── tests/
│   ├── test_syntax.py
│   └── test_pdf_generation.py
│
├── Dockerfile
├── docker-build.sh
├── requirements.txt
├── .gitignore
├── CLAUDE.md
├── README.md
└── SPECIFICATIONS.md
```

## 18\. État d'avancement et évolutions futures

L'essentiel du socle fonctionnel décrit dans ce document est implémenté : livre unique en mémoire, ajout et exploration des articles, sélection manuelle, organisation en chapitres, formats et marges configurables, génération du PDF avec signets de navigation.

Évolutions envisageables, non implémentées à ce jour :

* Filtrage de l'exploration par langue ou par catégorie d'article.

* Extraction indépendante des crédits et licences des images, au-delà de ce qu'intègre le PDF officiel Wikipédia.

* Journalisation des erreurs et limitation du débit des requêtes API.

* Couverture de tests automatisés plus large (aujourd'hui : syntaxe Python via `tests/test_syntax.py`, et numérotation des pages/table des matières via `tests/test_pdf_generation.py` — le reste du comportement, notamment l'assemblage complet du PDF, n'est pas couvert).

* Prévisualisation du livre avant génération.

* Importation de contenus depuis d'autres encyclopédies.

* Personnalisation avancée de la couverture et des styles typographiques.

* Génération de livres volumineux (regroupement par volumes, par exemple).

Toute évolution doit préserver les principes fondamentaux du logiciel, notamment le contrôle total de l'utilisateur sur la sélection des articles et l'absence de toute notion de projet.

## 19\. Historique des versions

Numéro de version applicatif (`app/main.py`, affiché dans le pied de page de l'application — voir section 12). Mis à jour à chaque génération de code, selon la règle définie dans `CLAUDE.md`.

| Version | Date       | Modifications apportées |
| ------- | ---------- | ------------------------ |
| 0.1.0   | 2026-11-07 | Version initiale : livre unique en mémoire, ajout et exploration des articles, sélection manuelle, organisation en chapitres, formats et marges configurables, génération du PDF avec signets de navigation. |
| 0.2.0   | 2026-11-09 | Nettoyage du code mort (suppression de `article_parser.py`, des champs `Article` inutilisés, du flux de création de « projet »). Ajout d'un test automatisé de syntaxe (`tests/test_syntax.py`) et de la politique de versionnement. |
| 0.2.1   | 2026-11-09 | Correction : le bouton « Ajouter » ne réagissait pas quand le champ de saisie était vide (validation HTML silencieuse) — un message d'erreur explicite est affiché à la place. |
| 0.3.0   | 2026-11-09 | Le numéro de version applicatif est désormais affiché dans le pied de page, en plus du commit git. |
| 0.4.0   | 2026-11-09 | Numérotation continue de toutes les pages du PDF généré (y compris les pages d'articles, via une superposition reportlab/pypdf) et affichage du numéro de page de chaque chapitre/article dans la table des matières. Ajout de `tests/test_pdf_generation.py`. |

Fin du document — Wikipedia2Book, spécifications version 1.1.
