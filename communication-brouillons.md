# Brouillons de communication sur Wikipedia2Book

Préparé le 18/11/2026 à partir de `todo-mediawiki2latex-visibility.md` et de la section « Communication » de `todo.md`. **Rien n'est publié** : chaque action attend ton accord, numéro par numéro.

Pour toutes les publications :
- résumé de modification qui signale le conflit d'intérêts : « conflit d'intérêts : je suis l'auteur de Wikipedia2Book » ou « COI: I am the author of Wikipedia2Book » ;
- signature `~~~~` sur les pages de discussion ;
- texte de présentation de référence : celui de `todo.md`, adapté à chaque page.

## Décisions (18/11/2026)

Validées : 0, 1, 2, 4, 5, 6, 7, 8a, 8b, 9, 10a, 10b, 10c, 11 (après 10), 12a, 12b, 13a, 13b. 12c reste suspendue à la réponse de la Rundschau (action 9).

Refusée : 3 (Help talk:Books, en.wikipedia).

## Déjà fait (rien à publier)

| Page | Par | Remarque |
|---|---|---|
| en.wikipedia [Wikipedia:Books](https://en.wikipedia.org/wiki/Wikipedia:Books) | toi, 18/11 03:13–03:16 | Puce Wikipedia2Book dans la liste des alternatives. |
| mediawiki.org [PDF export](https://www.mediawiki.org/wiki/PDF_export) | toi, 18/11 03:32–03:39 | Ligne Wikipedia2Book dans les deux tableaux. |
| en.wikibooks [Help:Print versions](https://en.wikibooks.org/wiki/Help:Print_versions) | toi, 18/11 03:42 | Section `=== Wikipedia2Book ===`. **À vérifier** : elle est insérée *au milieu* de la section « MediaWiki to LaTeX », juste avant la phrase « More than 80 % of books… created with MediaWiki2LaTeX ». Cette phrase semble maintenant parler de Wikipedia2Book. Je propose de déplacer la section Wikipedia2Book après la fin de la section MediaWiki to LaTeX (voir action 0). |
| fr.wikibooks [Wikilivres/Créer la version imprimable d'un livre](https://fr.wikibooks.org/wiki/Wikilivres/Cr%C3%A9er_la_version_imprimable_d%27un_livre) | 16/11 | Remplace l'action prévue sur « Aide:Version imprimable », page qui n'existe pas. |

## 0. Correction de Help:Print versions (en.wikibooks) — modification directe

Déplacer le bloc `=== Wikipedia2Book ===` (2 lignes) après le dernier paragraphe de la section « MediaWiki to LaTeX », pour ne pas couper cette section en deux. Aucun texte ne change.

Résumé : `Move the Wikipedia2Book subsection after the MediaWiki to LaTeX text it was splitting (COI: I am the author of Wikipedia2Book)`

## 1. fr.wikipedia — messages système de Spécial:Livre (demande aux administrateurs d'interface)

Page : [Wikipédia:Demande d'intervention sur un message système](https://fr.wikipedia.org/wiki/Wikip%C3%A9dia:Demande_d%27intervention_sur_un_message_syst%C3%A8me), nouvelle section en bas de page, au format `{{DIMS début}}` / `{{DIMS fin}}` des autres requêtes.

Titre : `[[MediaWiki:Coll-notice-download-pdf-text]] et [[MediaWiki:Coll-unknown subpage text]] – PDF des livres`

```
{{DIMS début|statut=|date=<!--~~~~~-->}}
'''Pages où apparaissent ces messages''' : [[Spécial:Livre]] (encadré « Télécharger des pages individuelles ») et l'ancien lien de rendu PDF des livres (<code>Spécial:Livre?bookcmd=render_collection…</code>), qui affiche « Sous-page inconnue ».

'''Changement proposé''' :
* [[MediaWiki:Coll-notice-download-pdf-text]] (texte par défaut aujourd'hui), ajouter à la fin : « Pour obtenir le PDF d'un livre entier, enregistrez-le (« Enregistrer le livre ») puis utilisez « Télécharger en PDF avec Wikipedia2Book » sur sa page, ou collez son adresse dans [[toolforge:wikipedia2book/|Wikipedia2Book]]. »
* [[MediaWiki:Coll-unknown subpage text]] : remplacer « Cette sous-page de livre n'existe pas. » par « Wikipédia ne produit plus de PDF de livres depuis cette page. Ouvrez la page du livre enregistré et utilisez « Télécharger en PDF avec Wikipedia2Book », ou collez son adresse dans [[toolforge:wikipedia2book/|Wikipedia2Book]] ; voir aussi [[Aide:Livres]]. »

Contexte : [[Modèle:Livre sauvegardé]] propose déjà ce lien sur chaque livre enregistré. [[toolforge:wikipedia2book/|Wikipedia2Book]] est un outil libre (AGPL) hébergé sur Toolforge, qui assemble les PDF officiels des articles avec couverture, table des matières et numéros de page. Je précise que j'en suis l'auteur (conflit d'intérêts) : n'hésitez pas à adapter ou refuser.

~~~~
{{DIMS fin}}
```

## 2. de.wikipedia — Wikipedia:Technik/Text/Konverter — modification directe

Dans `== Konvertierung von Wikitext (Export) ==` › `=== PDF ===`, après la puce mediawiki2latex/wb2pdf et sa sous-puce :

```
* [[toolforge:wikipedia2book/|Wikipedia2Book]] (Toolforge, AGPL) – stellt einen Buch-PDF aus mehreren Artikeln zusammen (auch aus einer gespeicherten Buchseite oder einer Wikibooks-Sammlung): offizielle PDF-Dateien der Artikel mit Titelseite, Inhaltsverzeichnis und Seitenzahlen. Dokumentation: [[github:gmoulard/wikipedia2book|GitHub]]
```

Résumé : `Wikipedia2Book bei PDF ergänzt (Interessenkonflikt: ich bin der Autor des Werkzeugs)`

## 3. en.wikipedia — Help:Books/FAQ — proposition en page de discussion (refusée le 18/11)

Page : [Help talk:Books](https://en.wikipedia.org/wiki/Help_talk:Books), nouvelle section.

Titre : `Mentioning Wikipedia2Book in Help:Books/FAQ`

```
[[Help:Books/FAQ]] mentions only MediaWiki2LaTeX for a PDF of a book (sections "How do I obtain a copy of a book?" and "PDF e-books"). [[Help:Books]] and [[Wikipedia:Books]] already list [[toolforge:wikipedia2book/|Wikipedia2Book]], a free (AGPL) Toolforge tool that builds a printable PDF book from a saved book or a list of articles, using the official PDF of each article, with a cover, a table of contents and page numbers.

I suggest adding, after each MediaWiki2LaTeX sentence of the FAQ:
: ''The Toolforge tool [[toolforge:wikipedia2book/|Wikipedia2Book]] can also build a PDF of a saved book, from the official PDF of each article.''

Disclosure: I am the author of Wikipedia2Book, so I would rather let someone else decide and edit the FAQ. ~~~~
```

## 4. es.wikipedia — Ayuda:Libros — proposition en page de discussion

Page : [Ayuda discusión:Libros](https://es.wikipedia.org/wiki/Ayuda_discusi%C3%B3n:Libros), nouvelle section. Ayuda:Libros est semi-protégée.

Titre : `Crear el PDF de un libro: Wikipedia2Book`

```
Hola. La creación de PDF desde [[Especial:Libro]] ya no funciona. Propongo añadir en [[Ayuda:Libros]] una frase como:
: ''Para obtener el PDF de un libro guardado, se puede usar [[toolforge:wikipedia2book/|Wikipedia2Book]], una herramienta libre (AGPL) de Toolforge que reúne los PDF oficiales de los artículos con portada, índice y números de página.''

Aviso: soy el autor de esta herramienta (conflicto de intereses), por eso lo propongo aquí en lugar de editar la página. ~~~~
```

## 5. it.wikipedia — Aiuto:Libri — proposition en page de discussion

Page : [Discussioni aiuto:Libri](https://it.wikipedia.org/wiki/Discussioni_aiuto:Libri), nouvelle section.

Titre : `PDF di un libro: Wikipedia2Book`

```
Ciao. La generazione del PDF da [[Speciale:Libro]] non funziona più. Propongo di aggiungere in [[Aiuto:Libri]] una frase come:
: ''Per ottenere il PDF di un libro salvato si può usare [[toolforge:wikipedia2book/|Wikipedia2Book]], uno strumento libero (AGPL) su Toolforge che riunisce i PDF ufficiali delle voci con copertina, indice e numeri di pagina.''

Nota: sono l'autore dello strumento (conflitto di interessi), per questo lo propongo qui invece di modificare la pagina. ~~~~
```

## 6. mediawiki.org — Talk:Reading/Web — message

`Talk:Reading/Web/PDF Functionality` renvoie vers [Talk:Reading/Web](https://www.mediawiki.org/wiki/Talk:Reading/Web) : nouvelle section là.

Titre : `PDF of books: a community tool on Toolforge`

```
For people who land here looking for a way to get a PDF of a whole book since the Collection rendering was turned off: [[toolforge:wikipedia2book/|Wikipedia2Book]] is a free (AGPL) Toolforge tool that builds a printable PDF from a saved book (Book: / User:…/Books/…), a Wikibooks printable version or compilation, or a list of pages from Wikipedia, Wikisource, Wikibooks, Wikivoyage, Wikiversity, Wikiquote, Wiktionary and Wikinews. It assembles the official PDF of each page (Special:DownloadAsPdf) with a cover, a table of contents and page numbers. It is listed on [[PDF export]] next to MediaWiki2LaTeX. Disclosure: I am its author. ~~~~
```

## 7. en.wikipedia — User talk:Steelpillow — message personnel

Page : [User talk:Steelpillow](https://en.wikipedia.org/wiki/User_talk:Steelpillow), nouvelle section.

Titre : `Wikipedia2Book, for your Wikipedia Books essay`

```
Hello Steelpillow, I read [[User:Steelpillow/Wikipedia Books]] with interest. In case it is useful for the essay: [[toolforge:wikipedia2book/|Wikipedia2Book]] is a free Toolforge tool I wrote that turns a saved book or a list of articles into a printable PDF (official PDF of each article, cover, table of contents, page numbers, volumes beyond 300 articles). It is already listed in [[Help:Books]] and [[Wikipedia:Books]]. Feedback welcome! ~~~~
```

## 8. en.wikibooks — livres qui expliquent mediawiki2latex — pages de discussion

8a. [Talk:RAC Attack - Oracle Cluster Database at Home](https://en.wikibooks.org/wiki/Talk:RAC_Attack_-_Oracle_Cluster_Database_at_Home), nouvelle section `Another way to create the full book PDF` :

```
[[RAC Attack - Oracle Cluster Database at Home/Create Full Book]] explains how to make a PDF with MediaWiki2LaTeX. Another option is [[toolforge:wikipedia2book/|Wikipedia2Book]], which builds the PDF from the official PDF of each chapter, with a cover, a table of contents and page numbers: [{{fullurl:toolforge:wikipedia2book/|source={{urlencode:{{canonicalurl:RAC Attack - Oracle Cluster Database at Home}}}}}} this book in Wikipedia2Book]. Maybe worth a line on the "Create Full Book" page? Disclosure: I am the author of the tool. ~~~~
```

8b. [Talk:Chatbots For Social Change](https://en.wikibooks.org/wiki/Talk:Chatbots_For_Social_Change) (page à créer), même message adapté : page `Chatbots For Social Change/Building on this WikiBook`, lien `canonicalurl:Chatbots For Social Change`.

## 9. de.wikibooks — Hilfe:Sammlungen — proposition à la Rundschau

Page : [Wikibooks:Rundschau](https://de.wikibooks.org/wiki/Wikibooks:Rundschau), nouvelle section.

Titre : `Wikipedia2Book als weitere PDF-Möglichkeit in Hilfe:Sammlungen`

```
Hallo, [[Hilfe:Sammlungen]] nennt für den PDF-Export nur mediawiki2latex. Ich schlage vor, dort einen kurzen Absatz zu ergänzen:
: ''Eine weitere Möglichkeit ist [[toolforge:wikipedia2book/|Wikipedia2Book]] (Toolforge, freie Software, AGPL): Man fügt die Adresse des Inhaltsverzeichnisses eines Buches oder einer Sammlung ein und erhält ein PDF aus den offiziellen PDF-Dateien der Kapitel, mit Titelseite, Inhaltsverzeichnis und Seitenzahlen.''

Ich bin der Autor des Werkzeugs (Interessenkonflikt) und schlage es deshalb hier vor, statt die Seite selbst zu ändern. Ein Helferlein „addWikipedia2BookLink“, analog zu [[MediaWiki:Gadget-addMediawiki2LatexLink]], könnte ich ebenfalls vorbereiten, falls Interesse besteht. ~~~~
```

## 10. en.wikiversity — pages de cours — modifications directes

10a. [Open Educational Resources/Tailored WikiBooks](https://en.wikiversity.org/wiki/Open_Educational_Resources/Tailored_WikiBooks), à la fin de `== Multiformat Export ==`, avant `== See also ==` :

```
=== Wikipedia2Book ===
[[toolforge:wikipedia2book/|Wikipedia2Book]] is another free (AGPL) tool on Toolforge for tailored books: paste the address of a saved book, a Wikibooks table of contents or a list of pages (Wikipedia, Wikiversity, Wikibooks…), reorder them into chapters, then download a PDF built from the official PDF of each page, with a cover, a table of contents and page numbers. The resulting PDF can be annotated privately as described above.
```

Résumé : `Add Wikipedia2Book as another way to build tailored PDF books (COI: I am its author)`

10b. [Risk Management/Tailored Wikibooks](https://en.wikiversity.org/wiki/Risk_Management/Tailored_Wikibooks), dans `== Wikibook Tool ==`, après le bloc MediaWiki to LaTeX :

```
* [[toolforge:wikipedia2book/|'''Wikipedia2Book''']] – PDF book from a saved book, a Wikibooks table of contents or a list of pages, with cover, table of contents and page numbers
** '''Input:''' address of the book or list of pages
** '''Output:''' PDF document (one per volume beyond 300 articles)
```

10c. [Wikibooks](https://en.wikiversity.org/wiki/Wikibooks), dans `== WikiMediaFoundation Labs ==`, même bloc que 10b.

Résumé 10b et 10c : `Add Wikipedia2Book (COI: I am its author)`

## 11. en.wikiversity — User talk:Bert Niehaus — message personnel (après 10)

Titre : `Wikipedia2Book for tailored Wikibooks`

```
Hello Bert, I added a short mention of [[toolforge:wikipedia2book/|Wikipedia2Book]] to [[Open Educational Resources/Tailored WikiBooks]] (and the two related pages). It is a Toolforge tool I wrote that builds a PDF book from a saved book or a list of pages, which seems close to your multi-format export work ([[User:Bert Niehaus/2021/Multi-Format Export]]). Please revert or adapt if it does not fit your course pages. ~~~~
```

## 12. Liens dans la barre latérale — propositions aux communautés germanophones

Code proposé (même principe que le lien mediawiki2latex existant) :

```js
mw.util.addPortletLink('p-tb', 'https://wikipedia2book.toolforge.org/?source=' + encodeURIComponent('https:' + mw.config.get('wgServer') + mw.util.getUrl(mw.config.get('wgPageName'))), 'Wikipedia2Book (PDF)');
```

12a. de.wikiversity — [Wikiversity:Cafeteria](https://de.wikiversity.org/wiki/Wikiversity:Cafeteria), titre `Link „Wikipedia2Book (PDF)“ im Werkzeugmenü` :

```
Hallo, [[MediaWiki:Common.js]] fügt im Werkzeugmenü den Link „Multi Format Export“ (mediawiki2latex) hinzu. Ich schlage vor, daneben einen Link „Wikipedia2Book (PDF)“ einzufügen (eine Zeile, siehe unten). [[toolforge:wikipedia2book/|Wikipedia2Book]] (Toolforge, AGPL) erstellt aus einer Seite, einem gespeicherten Buch oder dem Inhaltsverzeichnis eines Kurses ein PDF mit Titelseite, Inhaltsverzeichnis und Seitenzahlen. Auch [[Vorlage:Gespeichertes Buch]] könnte einen solchen Link bekommen.
<syntaxhighlight lang="js">(Code oben)</syntaxhighlight>
Ich bin der Autor des Werkzeugs (Interessenkonflikt); die Änderung müsste ein Oberflächenadministrator vornehmen. ~~~~
```

12b. de.wikisource — [Wikisource:Skriptorium](https://de.wikisource.org/wiki/Wikisource:Skriptorium), même proposition, en précisant que WS Export reste l'outil principal pour une œuvre seule et que Wikipedia2Book sert surtout à relier plusieurs textes en un seul PDF.

12c. de.wikibooks — proposition du gadget `addWikipedia2BookLink` : seulement si la Rundschau (action 9) répond favorablement.

## 13. Hors des wikis

13a. **Wikidata** — créer l'élément « Wikipedia2Book » :
- libellés : fr « Wikipedia2Book », en « Wikipedia2Book » ;
- description : en « web tool that builds printable PDF books from Wikimedia pages », fr « outil web qui crée des livres PDF imprimables à partir de pages Wikimédia » ;
- déclarations : nature de l'élément (P31) logiciel libre (Q341) et application web ; site officiel (P856) https://wikipedia2book.toolforge.org/ ; dépôt de code (P1324) https://github.com/gmoulard/wikipedia2book ; licence (P275) GNU AGPL v3 (Q27017232) ; langage de programmation (P277) Python ; Software Heritage ID (P6138) d'après `CITATION.cff`.
- Résumé : `Create item (COI: I am the author)`.

13b. **Tech/News** — brève proposée sur [m:Tech/News/Next](https://meta.wikimedia.org/wiki/Tech/News/Next) ou sa page de discussion :

```
* [[toolforge:wikipedia2book/|Wikipedia2Book]], a community tool on Toolforge, can now build a printable PDF from a saved book, a Wikibooks compilation or printable version, or a list of pages from eight Wikimedia projects, with a cover, a table of contents and page numbers.
```
