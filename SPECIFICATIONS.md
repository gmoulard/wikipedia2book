# Wikipedia2Book — Spécifications fonctionnelles et techniques

Version : 1.0 Statut : Document de référence Format : Markdown (`.md`)

## 1\. Présentation du projet

### 1.1 Objectif

Wikipedia2Book est un logiciel permettant de créer un livre au format PDF imprimable à partir d'articles de Wikipédia.

L'utilisateur peut sélectionner plusieurs articles principaux, explorer les articles qui leur sont liés, choisir précisément les contenus à intégrer, organiser les articles et générer un document PDF structuré.

Le logiciel doit fonctionner sur toutes les plateformes grâce à une architecture Python conteneurisée avec Docker.

### 1.2 Principes fondamentaux

* Le logiciel ne doit pas être limité à un thème ou à une catégorie d'articles.

* Plusieurs articles principaux peuvent être ajoutés à un même projet.

* L'exploration des liens Wikipédia doit être paramétrable.

* Aucun article découvert ne doit être ajouté automatiquement au livre.

* L'utilisateur conserve le contrôle total sur la sélection des articles.

* Le format du livre doit être configurable.

* Le PDF produit doit être adapté à l'impression.

## 2\. Gestion des projets

Le logiciel doit permettre de créer et gérer plusieurs projets indépendants.

Fonctionnalités attendues :
| Version | Statut | Format |
| --- | --- | --- |
| 1.0 | Document de référence | Markdown (`.md`) |

* Créer un nouveau projet.

* Nommer et décrire un projet.

* Conserver les modifications en mémoire dans le navigateur pendant la session.

* Télécharger explicitement l'espace de travail sous forme de fichier JSON.

* Importer un fichier JSON local contenant un ou plusieurs projets.

* Supprimer un projet.

* Exporter un projet ou sa configuration.

Chaque projet contient notamment :

* Les articles principaux.

* Les articles découverts.

* Les articles sélectionnés.

* La structure du livre.

* Les paramètres de mise en page.

* Les paramètres d'exportation.

Le serveur ne doit pas persister les projets sur son disque. Le navigateur conserve les projets en mémoire et échange leur structure JSON avec l'API pour les opérations qui nécessitent le serveur. La persistance est à la charge de l'utilisateur, via le téléchargement puis l'import manuel d'un fichier JSON.

## 3\. Gestion des articles principaux

### 3.1 Ajout des articles

L'utilisateur doit pouvoir ajouter plusieurs articles Wikipédia à un projet.

L'ajout peut se faire à partir :

* D'une URL Wikipédia.

* D'un titre d'article.

* D'une recherche sur Wikipédia.

* De l'URL d'une page de livre Wikipédia contenant la liste des pages à imprimer.

Les articles importés depuis une page de livre sont ajoutés à la sélection. Seuls leurs titres et leurs URL sont chargés à ce stade; leur PDF complet est téléchargé au moment de la génération.

Exemple :

`https://fr.wikipedia.org/wiki/Épaves_de_la_rade_de_Saint-Pierre`

### 3.2 Identification des articles

Pour chaque article, le logiciel doit récupérer :

* Le titre.

* L'URL Wikipédia.

* Le résumé.

* La langue.

* L'identifiant de page Wikipédia.

* La date de dernière modification, si disponible.

L'utilisateur doit pouvoir supprimer un article principal sans supprimer les autres.

## 4\. Exploration des articles liés

### 4.1 Principe

Le logiciel doit explorer les liens internes présents dans les articles principaux afin de proposer des articles complémentaires.

L'exploration doit s'appuyer sur l'API officielle MediaWiki.

### 4.2 Profondeur d'exploration

La profondeur doit être paramétrable.

Exemple :

| Profondeur | Comportement                                      |
| ---------- | ------------------------------------------------- |
| 0          | Aucun article complémentaire                      |
| 1          | Articles directement liés aux articles principaux |
| 2          | Articles liés aux articles de profondeur 1        |
| 3          | Articles liés aux articles de profondeur 2        |

La profondeur maximale autorisée doit être configurable afin d'éviter une exploration excessive.

### 4.3 Gestion des résultats

Pour chaque article découvert, afficher :

* Son titre.

* Son résumé.

* Son URL.

* Son article d'origine.

* Sa profondeur de découverte.

* Son statut de sélection.

Le logiciel doit éliminer les doublons, notamment lorsqu'un même article est lié depuis plusieurs pages.

### 4.4 Limites de l'exploration

L'utilisateur doit pouvoir limiter :

* Le nombre maximal d'articles découverts.

* La profondeur maximale.

* Les langues acceptées.

* Les catégories d'articles, si une fonctionnalité de filtrage est disponible.

## 5\. Sélection des articles

Cette fonctionnalité est essentielle.

Aucun article secondaire ne doit être intégré automatiquement au livre.

Le logiciel doit présenter la liste des articles découverts et laisser l'utilisateur choisir exactement ceux qu'il souhaite conserver.

Fonctionnalités attendues :

* Sélection individuelle.

* Désélection individuelle.

* Sélection multiple.

* Tout sélectionner.

* Tout désélectionner.

* Recherche par titre.

* Filtrage par article d'origine.

* Filtrage par profondeur.

* Affichage des articles déjà sélectionnés.

La sélection doit être conservée lors de la sauvegarde du projet.

## 6\. Organisation du livre

L'utilisateur doit pouvoir organiser les articles sélectionnés avant la génération du PDF.

Fonctionnalités :

* Réordonner les articles.

* Créer des chapitres.

* Déplacer un article d'un chapitre à un autre.

* Modifier les titres des chapitres.

* Ajouter une introduction générale.

* Ajouter une conclusion.

* Définir l'ordre de publication.

Un article peut être déplacé librement dans la structure du livre.

## 7\. Récupération du contenu Wikipédia

L'ajout et l'exploration ne doivent pas télécharger le contenu complet des pages. Au moment de générer le PDF, chaque article sélectionné doit être récupéré via l'endpoint PDF officiel de Wikimedia (`/api/rest_v1/page/pdf/{titre}`), équivalent à la fonction « Télécharger comme PDF » de Wikipédia.

Le PDF officiel de chaque article doit être conservé intégralement, avec son contenu, sa structure, ses images et ses références. Les PDFs sont assemblés dans l'ordre du livre sans reconstruire ni tronquer le corps des articles.

## 8\. Gestion des références et citations

La conservation des références est obligatoire.

Le logiciel doit préserver les références présentes dans les articles Wikipédia.

Deux modes de présentation peuvent être proposés :

* Références en notes de bas de page.

* Références regroupées à la fin de chaque article.

Les références doivent rester associées au texte auquel elles se rapportent.

Les URL des sources doivent être conservées lorsqu'elles sont disponibles.

Le logiciel ne doit jamais supprimer silencieusement les références d'un article.

## 9\. Gestion des images et des médias

### 9.1 Récupération

Le logiciel doit récupérer les images associées aux articles lorsque cela est techniquement possible et autorisé.

Pour chaque image, conserver :

* Le fichier ou son URL.

* La légende.

* Le nom du contributeur.

* La source.

* La licence.

* L'URL de la page de description du média.

### 9.2 Attribution

Les crédits et licences des images doivent être respectés.

Les images ne doivent pas être considérées comme automatiquement couvertes par la licence du texte Wikipédia : chaque média peut avoir sa propre licence.

### 9.3 Mise en page

Les images doivent être intégrées dans le PDF avec :

* Une taille adaptée.

* Un redimensionnement proportionnel.

* Une légende lisible.

* Une attribution lorsque nécessaire.

Si une image ne peut pas être récupérée, le logiciel doit gérer proprement son absence.

## 10\. Paramétrage du format du livre

Le format du document doit être entièrement configurable.

### 10.1 Formats standards

Formats à proposer :

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

Le format A5 doit être proposé par défaut, sans être imposé.

### 10.2 Format personnalisé

L'utilisateur doit pouvoir saisir :

* La largeur en millimètres.

* La hauteur en millimètres.

### 10.3 Orientation

Deux orientations doivent être disponibles :

* Portrait.

* Paysage.

### 10.4 Marges

L'utilisateur doit pouvoir régler indépendamment :

* La marge supérieure.

* La marge inférieure.

* La marge intérieure.

* La marge extérieure.

Une option de marge supplémentaire pour la reliure peut être prévue.

## 11\. Mise en page du livre

Le PDF doit être structuré comme un véritable livre.

Éléments possibles :

* Couverture.

* Titre du livre.

* Sous-titre.

* Auteur ou éditeur.

* Date de génération.

* Table des matières.

* Chapitres.

* Articles.

* Pagination.

* Références.

* Crédits et licences.

La mise en page doit garantir :

* Une typographie lisible.

* Une hiérarchie claire des titres.

* Des paragraphes correctement espacés.

* Des images correctement dimensionnées.

* Des tableaux adaptés à la largeur des pages.

* Des sauts de page cohérents.

* Une pagination continue.

Aucune fonctionnalité de prévisualisation n'est nécessaire dans la première version.

## 12\. Génération du PDF

### 12.1 Fonctionnement

Une fois les articles sélectionnés et organisés, l'utilisateur lance la génération du PDF.

Le logiciel doit :

* Vérifier la configuration du projet.

* Vérifier les articles sélectionnés.

* Télécharger, uniquement à cette étape, le PDF officiel complet de chaque article sélectionné.

* Préparer le frontispice et les pages de chapitre.

* Assembler en mémoire les PDFs Wikipédia dans l'ordre du livre et ajouter les signets de navigation.

* Générer la table des matières.

* Appliquer les paramètres de mise en page aux pages générées par l'application; les pages d'articles conservent le format de leur PDF Wikipédia.

* Générer le PDF.

* Rendre le fichier accessible au téléchargement.

### 12.2 Résultat

Le PDF doit être :

* Imprimable.

* Lisible.

* Structuré.

* Les articles complets sont ceux fournis par Wikipédia; le format personnalisé s'applique aux pages générées par l'application.

* Compatible avec les lecteurs PDF courants.

### 12.3 Gestion des erreurs

En cas d'échec, le logiciel doit afficher un message explicite.

Les erreurs possibles comprennent :

* Article introuvable.

* Problème de connexion à Wikipédia.

* Contenu indisponible.

* Image inaccessible.

* Référence invalide.

* Erreur de génération PDF.

* Espace disque insuffisant.

## 13\. Interface utilisateur

L'application doit proposer une interface web simple et intuitive.

### Écrans principaux

* Accueil et gestion des projets.

* Création et configuration d'un projet.

* Ajout des articles principaux.

* Exploration des articles liés.

* Sélection des articles.

* Organisation du livre.

* Paramétrage de la mise en page.

* Génération et téléchargement du PDF.

L'interface doit être utilisable sur ordinateur, tablette et smartphone.

## 14\. Architecture technique

### 14.1 Technologies

| Composant        | Technologie envisagée    |
| ---------------- | ------------------------ |
| Langage          | Python                   |
| Backend          | FastAPI                  |
| Interface        | HTML, CSS, JavaScript    |
| API Wikipédia    | MediaWiki API            |
| Échange de projets | JSON navigateur-serveur |
| Génération PDF   | PDF officiel Wikimedia, WeasyPrint et pypdf |
| Conteneurisation | Docker                   |
| Orchestration    | Docker Compose           |

Les technologies peuvent évoluer si une solution plus adaptée est identifiée.

### 14.2 API Wikipédia

Le logiciel doit utiliser les interfaces officielles de MediaWiki pour :

* Rechercher des articles.

* Identifier les pages.

* Explorer les liens internes.

* Récupérer les contenus.

* Télécharger les PDFs complets des pages sélectionnées au moment de l'export.

* Récupérer les informations relatives aux médias.

Les requêtes doivent respecter les règles d'utilisation de Wikipédia et limiter la charge imposée aux serveurs.

### 14.3 Docker

Le logiciel doit être livré avec :

* Un `Dockerfile`.

* Un fichier `docker-compose.yml`.

* Un fichier `requirements.txt`.

* Une documentation d'installation.

Le lancement doit être aussi simple que possible.

Exemple :

```bash
docker compose up -d --build
```

L'application doit être accessible depuis un navigateur web.

Le serveur ne stocke aucun projet ni PDF sur disque. Le navigateur doit permettre de télécharger et d'importer un fichier JSON contenant les projets et leurs structures complètes.

### 15\. Sécurité et robustesse

Le logiciel doit intégrer les précautions suivantes :

* Validation des URL fournies.

* Vérification des titres d'articles.

* Protection contre les injections.

* Gestion des erreurs réseau.

* Limitation des requêtes API.

* Gestion des délais d'attente.

* Nettoyage des fichiers temporaires.

* Limitation de la taille des téléchargements.

* Journalisation des erreurs.

Les URL externes ne doivent pas être exécutées comme du code.

## 16\. Respect des licences Wikipédia

Le logiciel doit respecter les licences applicables aux contenus récupérés.

Les textes Wikipédia sont généralement publiés sous licence Creative Commons Attribution-Partage dans les Mêmes Conditions (CC BY-SA), sous réserve des conditions applicables à chaque contenu.

Le logiciel doit donc prévoir :

* L'attribution des auteurs et contributeurs lorsque nécessaire.

* La mention de la licence applicable.

* La mention de la source Wikipédia.

* La conservation des liens vers les articles originaux.

* Le respect des obligations de partage à l'identique lorsque celles-ci s'appliquent.

Les images et médias doivent faire l'objet d'une vérification de licence indépendante.

Le logiciel ne doit pas présenter le PDF généré comme une publication officielle de Wikipédia.

## 17\. Critères d'acceptation

La version initiale sera considérée comme fonctionnelle si les points suivants sont validés :

* Création d'un projet.

* Ajout de plusieurs articles principaux.

* Exploration des liens internes.

* Paramétrage de la profondeur d'exploration.

* Détection des doublons.

* Affichage des articles découverts.

* Sélection manuelle des articles.

* Aucun ajout automatique d'article secondaire.

* Réorganisation des articles.

* Création de chapitres.

* Récupération du contenu des articles.

* Conservation des références.

* Récupération des images lorsque possible.

* Conservation des crédits et licences.

* Choix du format papier.

* Choix de l'orientation.

* Paramétrage des marges.

* Génération d'un PDF imprimable.

* Téléchargement du PDF.

* Export puis import des projets via un fichier JSON local.

## 18\. Découpage prévisionnel

### Version 1 — Socle fonctionnel

* Gestion des projets.

* Ajout de plusieurs articles.

* Exploration des liens.

* Paramétrage de la profondeur.

* Sélection manuelle.

* Génération PDF simple.

### Version 2 — Qualité éditoriale

* Organisation en chapitres.

* Table des matières.

* Couverture.

* Pagination.

* Conservation avancée des références.

* Gestion des tableaux et images.

### Version 3 — Personnalisation avancée

* Formats personnalisés.

* Réglages typographiques.

* Paramètres de reliure.

* Personnalisation avancée de la couverture.

* Amélioration de la gestion des licences et crédits.

## 19\. Structure cible du projet

```text
Wikipedia2Book/
│
├── app/
│   ├── main.py
│   ├── models.py
│   ├── wikipedia_api.py
│   ├── explorer.py
│   ├── article_parser.py
│   ├── book_builder.py
│   ├── pdf_generator.py
│   │
│   ├── templates/
│   │   └── index.html
│   │
│   └── static/
│       ├── style.css
│       └── app.js
│
├── data/
│   └── projects/
│
├── output/
│
├── tests/
│
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── README.md
├── SPECIFICATIONS.md
└── DEMANDES_EVOLUTION.md
```

## 20\. Évolutivité

Le logiciel doit être conçu de manière modulaire afin de permettre l'ajout ultérieur de fonctionnalités.

Les évolutions pourront notamment concerner :

* L'importation de contenus depuis d'autres encyclopédies.

* La gestion de plusieurs langues.

* L'amélioration de la qualité éditoriale.

* La personnalisation des styles.

* L'export dans d'autres formats.

* La génération de livres volumineux.

* La gestion avancée des licences.

* L'ajout d'une interface d'administration.

Toute évolution devra préserver les principes fondamentaux du projet, notamment le contrôle de l'utilisateur sur la sélection des articles.

Fin du document — Wikipedia2Book, spécifications version 1.0.
