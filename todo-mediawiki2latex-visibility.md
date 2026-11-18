# Visibilité de Wikipedia2Book là où mediawiki2latex est cité

Relevé du 17/11/2026 : recherche « mediawiki2latex » dans tous les espaces de noms de 19 wikis Wikimédia (API `list=search`), puis lecture du wikitexte de chaque page retenue pour compter les mentions de mediawiki2latex (m2l) et de Wikipedia2Book (w2b). Ne sont pas retenus : les fichiers (vidéos et PDF de démonstration de mediawiki2latex, présents sur tous les wikis par Commons), les archives de discussions, les bulletins Tech/News, les pages « Livres » d'utilisateurs (elles ne citent mediawiki2latex que par le modèle de livre) et les `common.js` personnels.

Règles communes avant toute modification :

- **Conflit d'intérêts** : en tant qu'auteur de l'outil, le dire dans le résumé de modification ou sur la page de discussion ; pour une page d'aide très suivie, proposer d'abord le texte en page de discussion et laisser un autre contributeur l'intégrer.
- **Ton neutre** : présenter Wikipedia2Book comme une option parmi d'autres (mediawiki2latex, WS Export, Special:DownloadAsPdf), sans comparaison avantageuse ; renvoyer vers https://wikipedia2book.toolforge.org/ et sa documentation https://gmoulard.github.io/wikipedia2book/.
- **Pages `MediaWiki:`** (gadgets, `Common.js`) : seuls les administrateurs d'interface peuvent les modifier ; passer par une demande de modification (`{{Edit request}}` ou équivalent local) après accord de la communauté (Bistro / Village pump / Rundschau).

## Pages où Wikipedia2Book est déjà cité

| Wiki | Page | m2l | w2b | Action |
|---|---|---|---|---|
| en.wikipedia | [Help:Books](https://en.wikipedia.org/wiki/Help:Books) | 4 | 3 | Rien ; vérifier de temps en temps que la description reste exacte (limite de 300 articles, projets acceptés). |
| en.wikipedia | [Help:Download as PDF](https://en.wikipedia.org/wiki/Help:Download_as_PDF) | 1 | 1 | Rien. |
| fr.wikipedia | [Aide:Livres](https://fr.wikipedia.org/wiki/Aide:Livres) | 0 | 1 | Rien. |
| de.wikipedia | [Hilfe:Buchfunktion](https://de.wikipedia.org/wiki/Hilfe:Buchfunktion) | 1 | 1 | Rien. |

## Pages d'aide et de documentation à compléter

| Wiki | Page | m2l | w2b | Comment ajouter Wikipedia2Book |
|---|---|---|---|---|
| en.wikipedia | [Help:Books/FAQ](https://en.wikipedia.org/wiki/Help:Books/FAQ) | 2 | 0 | Dans la réponse qui cite mediawiki2latex, ajouter une phrase sur Wikipedia2Book. Proposer sur [Help talk:Books](https://en.wikipedia.org/wiki/Help_talk:Books), qui suit aussi la FAQ. |
| en.wikipedia | [Wikipedia:Books](https://en.wikipedia.org/wiki/Wikipedia:Books) | 4 | 0 | À côté des mentions de mediawiki2latex, ajouter une ligne « Wikipedia2Book (Toolforge) : PDF d'un livre ou d'une page Book:, à partir des PDF officiels des articles ». Proposition en page de discussion. |
| en.wikipedia | [User:Steelpillow/Wikipedia Books](https://en.wikipedia.org/wiki/User:Steelpillow/Wikipedia_Books) | 6 | 0 | Page personnelle (essai sur l'avenir des livres) : ne pas la modifier ; laisser un message à Steelpillow sur sa page de discussion pour signaler l'outil. |
| de.wikipedia | [Wikipedia:Technik/Text/Konverter](https://de.wikipedia.org/wiki/Wikipedia:Technik/Text/Konverter) | 6 | 0 | Liste des convertisseurs (mediawiki2latex y a sa section) : ajouter une courte section ou une ligne de tableau pour Wikipedia2Book (PDF, Toolforge, AGPL), en allemand. Modification directe acceptable sur cette page technique, avec mention du conflit d'intérêts. |
| es.wikipedia | [Ayuda:Libros](https://es.wikipedia.org/wiki/Ayuda:Libros) | 0 | 0 | Ne cite pas mediawiki2latex, mais c'est l'équivalent d'Aide:Livres : proposer une phrase en espagnol sur la page de discussion. |
| it.wikipedia | [Aiuto:Libri](https://it.wikipedia.org/wiki/Aiuto:Libri) | 0 | 0 | Même chose, en italien. |
| mediawiki.org | [Reading/Web/PDF Functionality](https://www.mediawiki.org/wiki/Reading/Web/PDF_Functionality) | 2 | 0 | Page du projet de la WMF, figée : ne pas modifier ; ajouter un message dans [Talk:Reading/Web/PDF Functionality](https://www.mediawiki.org/wiki/Talk:Reading/Web/PDF_Functionality), lu par les personnes qui cherchent encore une solution. |
| mediawiki.org | [PDF export](https://www.mediawiki.org/wiki/PDF_export) | 2 | 0 | Page qui recense les solutions d'export PDF (mediawiki2latex, WS Export…) : ajouter une entrée Wikipedia2Book à côté de mediawiki2latex. Page traduisible : modifier la version source, les traducteurs suivront. |
| meta.wikimedia | [Grants:IEG/LaTeX Export](https://meta.wikimedia.org/wiki/Grants:IEG/LaTeX_Export) | 1 | 0 | Dossier de subvention de mediawiki2latex, archivé : rien à ajouter. |
| en.wikibooks | [Help:Print versions](https://en.wikibooks.org/wiki/Help:Print_versions) | 1 | 0 | À côté de la mention de mediawiki2latex, ajouter que Wikipedia2Book prend l'adresse d'une page « Print version » ou du sommaire d'un livre et produit un PDF avec chapitres. Proposition sur la page de discussion ou au [Reading room](https://en.wikibooks.org/wiki/Wikibooks:Reading_room). |
| en.wikibooks | [RAC Attack…/Create Full Book](https://en.wikibooks.org/wiki/RAC_Attack_-_Oracle_Cluster_Database_at_Home/Create_Full_Book) | 1 | 0 | Mode d'emploi propre à ce livre : proposer aux auteurs du livre une ligne « ou avec Wikipedia2Book » sur la page de discussion du livre. |
| en.wikibooks | [Chatbots For Social Change/Building on this WikiBook](https://en.wikibooks.org/wiki/Chatbots_For_Social_Change/Building_on_this_WikiBook) | 1 | 0 | Même chose. |
| de.wikibooks | [Hilfe:Sammlungen](https://de.wikibooks.org/wiki/Hilfe:Sammlungen) | 3 | 0 | Page d'aide sur les recueils, qui explique l'export par mediawiki2latex : ajouter un paragraphe « Wikipedia2Book » en allemand, proposé à la [Wikibooks:Rundschau](https://de.wikibooks.org/wiki/Wikibooks:Rundschau). |
| fr.wikibooks | [Aide:Version imprimable](https://fr.wikibooks.org/wiki/Aide:Version_imprimable) | 0 | 0 | Ne cite aucun outil : proposer au [Bistro de Wikilivres](https://fr.wikibooks.org/wiki/Wikilivres:Le_Bistro) une phrase sur la création d'un PDF à partir de la version imprimable (accepté depuis la 1.12.0). |
| en.wikiversity | [Open Educational Resources/Tailored WikiBooks](https://en.wikiversity.org/wiki/Open_Educational_Resources/Tailored_WikiBooks) | 3 | 0 | Ressource pédagogique qui présente mediawiki2latex pour composer des livres sur mesure : ajouter une sous-section « Wikipedia2Book » avec un exemple de livre (lien `?source=`). Modification directe acceptable (contenu de cours), signaler à l'auteur (Bert Niehaus). |
| en.wikiversity | [Risk Management/Tailored Wikibooks](https://en.wikiversity.org/wiki/Risk_Management/Tailored_Wikibooks) | 1 | 0 | Même approche, courte mention. |
| en.wikiversity | [Wikibooks](https://en.wikiversity.org/wiki/Wikibooks) | 1 | 0 | Page de cours sur Wikibooks : ajouter une ligne dans la liste des outils d'export. |
| en.wikiversity | [User:Bert Niehaus/2021/Multi-Format Export](https://en.wikiversity.org/wiki/User:Bert_Niehaus/2021/Multi-Format_Export) | 4 | 0 | Page personnelle : ne pas modifier ; écrire à Bert Niehaus, qui recense les exports multi-formats. |

## Liens dans l'interface des wikis (gadgets, `Common.js`)

| Wiki | Page | m2l | w2b | Comment ajouter Wikipedia2Book |
|---|---|---|---|---|
| de.wikibooks | [MediaWiki:Gadget-addMediawiki2LatexLink](https://de.wikibooks.org/wiki/MediaWiki:Gadget-addMediawiki2LatexLink) et [MediaWiki:Gadgets-definition](https://de.wikibooks.org/wiki/MediaWiki:Gadgets-definition) | 1 | 0 | Gadget qui ajoute un lien « mediawiki2latex » dans la barre latérale. Écrire un gadget équivalent `addWikipedia2BookLink` (lien vers `https://wikipedia2book.toolforge.org/?source=<adresse de la page>`, qui reconnaît déjà les sommaires de Wikilivres), le proposer à la Rundschau, puis demander son installation à un administrateur d'interface. |
| fr.wikibooks | [MediaWiki:Coll-unknown_subpage_text](https://fr.wikibooks.org/wiki/MediaWiki:Coll-unknown_subpage_text) | 0 | 0 | Message affiché par `Spécial:Livre?…&bookcmd=render_collection` depuis l'arrêt de l'export de l'extension Collection (« Cette sous-page de compilation n'existe pas »). Proposer en page de discussion, pour un administrateur d'interface : « L'export en PDF des compilations n'est plus disponible depuis cette page. Pour obtenir le PDF d'une compilation, collez son adresse dans le champ « Construire le livre » de [https://wikipedia2book.toolforge.org/ Wikipedia2Book], un outil de Toolforge qui assemble les PDF officiels des pages en un seul livre. Voir aussi [[Aide:Compilations]]. » Le message ne reçoit pas le titre de la compilation : pas de lien direct. À faire après le déploiement de la lecture des compilations (`Wikilivres:Compilations/…`). |
| de.wikiversity | [MediaWiki:Common.js](https://de.wikiversity.org/wiki/MediaWiki:Common.js) | 2 | 0 | Le `Common.js` du wiki ajoute un lien mediawiki2latex dans la barre latérale : proposer à la [Cafeteria](https://de.wikiversity.org/wiki/Wikiversity:Cafeteria) d'ajouter un lien Wikipedia2Book de la même façon (même adresse `?source=`). |
| de.wikiversity | [Vorlage:Gespeichertes Buch](https://de.wikiversity.org/wiki/Vorlage:Gespeichertes_Buch) | 1 | 0 | Modèle posé sur les livres enregistrés, avec un lien de rendu mediawiki2latex : proposer d'y ajouter un lien « PDF avec Wikipedia2Book » (`?source=` avec l'adresse de la page du livre, page « Livre: » acceptée depuis la 1.3.0). Même modèle à chercher sur les autres wikis (« Saved book », « Livre enregistré »). |
| de.wikisource | [MediaWiki:Common.js](https://de.wikisource.org/wiki/MediaWiki:Common.js) | 2 | 0 | Même chose qu'à de.wikiversity, proposé au [Skriptorium](https://de.wikisource.org/wiki/Wikisource:Skriptorium) ; Wikisource a déjà WS Export : présenter Wikipedia2Book pour les recueils de plusieurs œuvres et les PDF reliés en un seul volume. |

## Hors des wikis

| Endroit | État | Comment ajouter Wikipedia2Book |
|---|---|---|
| [Toolhub](https://toolhub.wikimedia.org/) | Wikipedia2Book y est déjà (2 fiches trouvées par la recherche du 17/11/2026) ; mediawiki2latex n'y est pas | Rien à ajouter ; garder `toolinfo.json` à jour à chaque version. |
| Wikidata | Q130455252 est l'article scientifique de 2024 sur mediawiki2latex (« Wikipedia to LaTeX, PDF, EPUB and ODT ») | Créer un élément « Wikipedia2Book » (logiciel, licence AGPL-3.0, dépôt GitHub, site officiel, SWHID) ; la notoriété de Wikidata est plus souple que celle de Wikipédia pour un outil de Toolforge. |
| Tech/News (meta) | mediawiki2latex y a été annoncé en 2019 et en 2024 | Proposer une brève pour une nouvelle version importante (page de proposition de Tech News sur meta), une fois par grande nouveauté. |
