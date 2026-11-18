# Brouillons de communication sur Wikipedia2Book

Préparé le 18/11/2026 à partir de `todo-mediawiki2latex-visibility.md` et de la section « Communication » de `../todo.md`. **Rien n'est publié** : chaque action attend ton accord, numéro par numéro.

Pour toutes les publications :
- résumé de modification qui signale le conflit d'intérêts : « conflit d'intérêts : je suis l'auteur de Wikipedia2Book » ou « COI: I am the author of Wikipedia2Book » ;
- signature `~~~~` sur les pages de discussion ;
- Ajouté un liens vers wikipedia2book https://wikipedia2book.toolforge.org/
- Ajouté l'image https://www.mediawiki.org/wiki/Reading/Web/PDF_Functionality#/media/File:Wikipedia2book_Logo.png e, 70*70 avec un liens vers https://wikipedia2book.toolforge.org/
- Ajouté quand quand il y a une URL un liens [ Télécharger en PDF ](https://iw.toolforge.org/wikipedia2book/api/pdf/from-source?source=https://...) comme sur la page : https://fr.wikipedia.org/wiki/Utilisateur:474D6F756C617264/Livres/Les_%C3%A9paves_de_la_rade_de_Saint-Pierre_suite_a_l'%C3%A9ruption_de_la_montagne_Pel%C3%A9e_en_1902
  - remarque: dans un page on peut mettre: {| class="wikitable"
|[[File:Wikipedia2book Logo.png|left|thumb|70x70px]][https://wikipedia2book.toolforge.org/ Wikipedia2Book] is a web application that allows you to compile a book in a printable PDF format. Users can select a Wikipedia book or specific articles, explore related links, organize content into chapters and volumes, and configure the layout before exporting the final PDF file. Available for: Wikipedia, Wikisource, Wikibooks, Wikivoyage, Wikiversity, Wikiquote, Wiktionary, and Wikinews.
|}
- texte de présentation de référence : celui de `../todo.md`, adapté à chaque page.

## Déjà fait (rien à publier)

| Page | Par | Remarque |
|---|---|---|
| en.wikipedia [Wikipedia:Books](https://en.wikipedia.org/wiki/Wikipedia:Books) | toi, 18/11 03:13–03:16 | Puce Wikipedia2Book dans la liste des alternatives. |
| mediawiki.org [PDF export](https://www.mediawiki.org/wiki/PDF_export) | toi, 18/11 03:32–03:39 | Ligne Wikipedia2Book dans les deux tableaux. |
| mediawiki.org [Reading/Web/PDF Functionality](https://www.mediawiki.org/wiki/Reading/Web/PDF_Functionality) | toi, 18/11 02:22 | Tableau Wikipedia2Book (logo + description) dans la section « Alternative », après mediawiki2latex. **Conflit d'intérêts non signalé** : résumé « introduce wikipedia2book » sans mention d'auteur, modification directe d'une page de la WMF. Tableau placé dans un bloc `<translate>` sans marqueur `<!--T:nnn-->` : il faut qu'un administrateur des traductions marque la page. Les deux sont rattrapés par l'action 6, publiée le 18/11 à 08:21 UTC ([diff](https://www.mediawiki.org/w/index.php?diff=8734535)) ; en attente d'un administrateur des traductions. |
| en.wikibooks [Help:Print versions](https://en.wikibooks.org/wiki/Help:Print_versions) | toi, 18/11 03:42 | Section `=== Wikipedia2Book ===`. **À vérifier** : elle est insérée *au milieu* de la section « MediaWiki to LaTeX », juste avant la phrase « More than 80 % of books… created with MediaWiki2LaTeX ». Cette phrase semble maintenant parler de Wikipedia2Book. Je propose de déplacer la section Wikipedia2Book après la fin de la section MediaWiki to LaTeX (voir action 0). |
| fr.wikipedia [Demande d'intervention sur un message système](https://fr.wikipedia.org/w/index.php?diff=241449346) | moi depuis ton compte, 18/11 09:00 | Action 1 publiée (encadré PDF de Spécial:Livre + « Sous-page inconnue »), corrigée à 09:04 ([diff](https://fr.wikipedia.org/w/index.php?diff=241449387)) : « cadre de droite » et nom du livre. Complétée à 09:11 ([diff](https://fr.wikipedia.org/w/index.php?diff=241449461)) : script pour `MediaWiki:Common.js` (voir action 1 bis). Réponse d'Escargot bleu à 12:18 CET : contre le script dans `Common.js`, il l'a copié dans [MediaWiki:Gadget-Wikipedia2Book.js](https://fr.wikipedia.org/wiki/MediaWiki:Gadget-Wikipedia2Book.js) (créé à 10:51 UTC, ni dans `Gadgets-definition` ni chargé nulle part) et propose que Spécial:Livre invite à ajouter `obtenir('Wikipedia2Book');` à son `common.js`. Remercié à 11:42 UTC ([diff](https://fr.wikipedia.org/w/index.php?diff=241453771)). | Messages système pas encore modifiés. |
| Action 0 | vérifié le 18/11 | Rien à corriger : la section Wikipedia2Book est avant `=== MediaWiki to LaTeX ===`, la phrase « More than 80 % » reste sous son titre. |
| Actions 2, 3, 4, 7, 8a, 8b, 9, 10a–c, 11, 12a, 12b, 13b, 17a | moi depuis ton compte, 18/11 08:22–08:35 UTC | Publiées avec mention du conflit d'intérêts : de.wikipedia [Technik/Text/Konverter](https://de.wikipedia.org/w/index.php?diff=272261518) ; en.wikipedia [Help talk:Books](https://en.wikipedia.org/w/index.php?diff=1386398091), [User talk:Steelpillow](https://en.wikipedia.org/w/index.php?diff=1386398092), [MediaWiki talk:Coll-unknown subpage text](https://en.wikipedia.org/w/index.php?diff=1386398093) ; es.wikipedia [Ayuda discusión:Libros](https://es.wikipedia.org/w/index.php?diff=176350693) ; en.wikibooks [Talk:RAC Attack…](https://en.wikibooks.org/w/index.php?diff=4682775), [Talk:Chatbots For Social Change](https://en.wikibooks.org/w/index.php?diff=4682776) ; de.wikibooks : action 9 déposée sur [Hilfe Diskussion:Sammlungen](https://de.wikibooks.org/w/index.php?diff=1094419) (la Rundschau est un portail, pas une page de discussion : ajout annulé aussitôt, [diff](https://de.wikibooks.org/w/index.php?diff=1094418)) ; en.wikiversity [Tailored WikiBooks](https://en.wikiversity.org/w/index.php?diff=2846695), [Risk Management/Tailored Wikibooks](https://en.wikiversity.org/w/index.php?diff=2846696), [Wikibooks](https://en.wikiversity.org/w/index.php?diff=2846697), [User talk:Bert Niehaus](https://en.wikiversity.org/w/index.php?diff=2846698) ; de.wikiversity [Cafeteria](https://de.wikiversity.org/w/index.php?diff=1119930) ; de.wikisource [Skriptorium](https://de.wikisource.org/w/index.php?diff=5101954) ; meta [Talk:Tech/News](https://meta.wikimedia.org/w/index.php?diff=31307984) (brève 13b proposée en page de discussion). | Réponses à suivre. |
| Logo et lien PDF dans les messages publiés | moi depuis ton compte, 18/11 09:2x UTC | Règles ajoutées le 18/11 appliquées aux 17 pages publiées par moi (actions 1–4, 6–12b, 13b, 17a), avant toute réponse sur ces pages : logo `[[File:Wikipedia2book Logo.png\|70px\|link=toolforge:wikipedia2book/]]` en tête du message, en modification mineure avec mention du conflit d'intérêts ; lien `Download as PDF` (`api/pdf/from-source?source=…&language=en`) dans 8a et 8b, les seuls messages qui citent un livre (les deux livres sont bien lus par l'outil). Le lien vers l'outil y était déjà partout. Diffs : [Konverter](https://de.wikipedia.org/w/index.php?diff=272262523), [Help talk:Books](https://en.wikipedia.org/w/index.php?diff=1386402749), [User talk:Steelpillow](https://en.wikipedia.org/w/index.php?diff=1386402802), [MediaWiki talk:Coll-unknown subpage text](https://en.wikipedia.org/w/index.php?diff=1386402806), [Ayuda discusión:Libros](https://es.wikipedia.org/w/index.php?diff=176351196), [Talk:RAC Attack…](https://en.wikibooks.org/w/index.php?diff=4682785), [Talk:Chatbots For Social Change](https://en.wikibooks.org/w/index.php?diff=4682786), [Hilfe Diskussion:Sammlungen](https://de.wikibooks.org/w/index.php?diff=1094420), [Tailored WikiBooks](https://en.wikiversity.org/w/index.php?diff=2846704), [Risk Management/Tailored Wikibooks](https://en.wikiversity.org/w/index.php?diff=2846705), [Wikibooks](https://en.wikiversity.org/w/index.php?diff=2846706), [User talk:Bert Niehaus](https://en.wikiversity.org/w/index.php?diff=2846707), [Cafeteria](https://de.wikiversity.org/w/index.php?diff=1119942), [Skriptorium](https://de.wikisource.org/w/index.php?diff=5102660), [Talk:Tech/News](https://meta.wikimedia.org/w/index.php?diff=31308044), [Talk:Reading/Web](https://www.mediawiki.org/w/index.php?diff=8734723), [Demande d'intervention sur un message système](https://fr.wikipedia.org/w/index.php?diff=241450672). Pas touché : tes propres modifications (Wikipedia:Books, PDF export, Help:Print versions, fr.wikibooks), Reading/Web/PDF Functionality ayant déjà le logo. |
| Action 5 (it.wikipedia) | toi, compte CapitaineCanette, 18/11 11:09 UTC | Publiée sur [Discussioni aiuto:Libri](https://it.wikipedia.org/w/index.php?diff=153424523), avec logo, conflit d'intérêts et mention de l'ancien compte (bloqué sans limite de durée depuis le 22/08/2026, motif « Nome utente inappropriato », blocage #1029446). | Réponse à suivre. |
| Action 13a (Wikidata) | non publiée | Création refusée par l'AbuseFilter n° 11 (avertissement « badwords ») ; renvoyer la même modification confirme l'avertissement : à décider. |
| Action 15 (Phabricator) | moi depuis ton compte, 18/11 11:32 | Commentaire publié sur [T224922](https://phabricator.wikimedia.org/T224922#12575282), texte du brouillon inchangé (en:Template:Saved book ne renvoie pas vers Wikipedia2Book : seul le modèle français est cité), avec mention de l'auteur. | Réponse à suivre. |
| Action 14 (Phabricator, caractères CJK rares) | toi, 18/11 | Tâche [T445303](https://phabricator.wikimedia.org/T445303) déposée (étiquettes Proton et All-and-every-Wikisource, PDF-Rendering étant archivé), brouillon dans [phabricator-cjk-wikisource.md](phabricator-cjk-wikisource.md). | Réponse à suivre. |
| Action 16 (Toolhub) | non publiée | Connexion OAuth Wikimédia à faire par toi sur toolhub.wikimedia.org. |
| Action 19 (Diff) | toi, puis moi depuis ton compte, 18/11 | Billet [n° 223381](https://diff.wikimedia.org/?p=223381) : présentation en étapes et captures, puis texte de [story.en.md](story.en.md) ajouté à la suite ; soumis à relecture le 18/11, copie dans [diff-article.md](diff-article.md). | Relecture de l'équipe éditoriale à suivre ; attribution de l'image et remerciements à ajouter. |
| Action 20a (WikiConvention francophone) | toi, 18/11 | Présentation proposée. | Réponse à suivre. |
| Action 20b (Wikimania 2027) | toi, 18/11 | Fait. | Réponse à suivre. |
| Action 17b (es, de) | moi depuis ton compte, 18/11 11:36–11:37 UTC | Demandes aux administrateurs d'interface publiées sans attendre les réponses à 1 et 17a, avec logo et conflit d'intérêts : es.wikipedia [Tablón de solicitudes](https://es.wikipedia.org/w/index.php?diff=176352232) (format Asunto / Usuario / Respuesta) ; de.wikipedia [Technik/Skin/MediaWiki/Änderungen](https://de.wikipedia.org/w/index.php?diff=272266029). Pas it (ancien compte bloqué). | Réponses à suivre. |
| Actions 12c, 18, 21 | non publiées | Conditionnelles (réponse attendue), à faire au fil de l'eau, ou hors wiki ; [m:Talk:Offline](https://meta.wikimedia.org/wiki/Talk:Offline) n'existe pas (page non suivie), 21b abandonnée. |
| fr.wikibooks [Wikilivres/Créer la version imprimable d'un livre](https://fr.wikibooks.org/wiki/Wikilivres/Cr%C3%A9er_la_version_imprimable_d%27un_livre) | 16/11 | Remplace l'action prévue sur « Aide:Version imprimable », page qui n'existe pas. |

## 0. Correction de Help:Print versions (en.wikibooks) — modification directe

Déplacer le bloc `=== Wikipedia2Book ===` (2 lignes) après le dernier paragraphe de la section « MediaWiki to LaTeX », pour ne pas couper cette section en deux. Aucun texte ne change.

Résumé : `Move the Wikipedia2Book subsection after the MediaWiki to LaTeX text it was splitting (COI: I am the author of Wikipedia2Book)`

## 1. fr.wikipedia — messages système de Spécial:Livre (demande aux administrateurs d'interface)

Page : [Wikipédia:Demande d'intervention sur un message système](https://fr.wikipedia.org/wiki/Wikip%C3%A9dia:Demande_d%27intervention_sur_un_message_syst%C3%A8me), nouvelle section en bas de page, au format `{{DIMS début}}` / `{{DIMS fin}}` des autres requêtes.

Titre : `[[MediaWiki:Coll-notice-download-pdf-title]], [[MediaWiki:Coll-notice-download-pdf-text]] et [[MediaWiki:Coll-unknown subpage text]] – PDF des livres`

Les trois messages ont aujourd'hui leur texte par défaut (pas de page locale, vérifié le 18/11/2026) : il faut les créer, ce que seuls les administrateurs d'interface peuvent faire.

```
{{DIMS début|statut=|date=<!--~~~~~-->}}
'''Pages où apparaissent ces messages''' : [[Spécial:Livre]] (encadré « Télécharger des pages individuelles ») et l'ancien lien de rendu PDF des livres (<code>Spécial:Livre?bookcmd=render_collection…</code>), qui affiche « Sous-page inconnue ».

'''Changement proposé''' : remplacer l'encadré de [[Spécial:Livre]], qui dit seulement que le créateur de livre ne fait plus de PDF, par les liens vers Wikipedia2Book.
* [[MediaWiki:Coll-notice-download-pdf-title]] : remplacer « Télécharger des pages individuelles » par « Télécharger le livre en PDF ».
* [[MediaWiki:Coll-notice-download-pdf-text]] : remplacer le texte actuel par :
<pre>
Le créateur de livre ne produit plus de PDF ([[mw:Reading/Web/PDF_Functionality|en savoir plus]]). Pour obtenir le PDF du livre entier, avec couverture, table des matières et numéros de page :
* donner un nom au livre et '''''Sauvegarder le livre''''' (cadre de droite), puis, sur la page du livre sauvegardé, '''''Télécharger en PDF''''' (lien [[toolforge:wikipedia2book/|Wikipedia2Book]] du cadre en tête de page) ;
* ou coller l'adresse du livre sauvegardé, ou la liste des articles, dans [[toolforge:wikipedia2book/|Wikipedia2Book]].
Pour un article seul : '''''Télécharger en tant que PDF''''' dans les outils de la barre latérale.
</pre>
* [[MediaWiki:Coll-unknown subpage text]] : remplacer « Cette sous-page de livre n'existe pas. » par « Wikipédia ne produit plus de PDF de livres depuis cette page. Ouvrez la page du livre sauvegardé et utilisez « Télécharger en PDF » (lien Wikipedia2Book du cadre en tête de page), ou collez son adresse dans [[toolforge:wikipedia2book/|Wikipedia2Book]] ; voir aussi [[Aide:Livres]]. »

Contexte : [[Modèle:Livre sauvegardé]] propose déjà ce lien sur chaque livre enregistré. [[toolforge:wikipedia2book/|Wikipedia2Book]] est un outil libre (AGPL) hébergé sur Toolforge, qui assemble les PDF officiels des articles avec couverture, table des matières et numéros de page. Je précise que j'en suis l'auteur (conflit d'intérêts) : n'hésitez pas à adapter ou refuser.

~~~~
{{DIMS fin}}
```

## 1 bis. fr.wikipedia — script de Spécial:Livre (publié avec l'action 1)

Le livre en cours de Spécial:Livre vit dans la session : un message système ne peut pas le transmettre. Script proposé pour `MediaWiki:Common.js`, exécuté seulement sur Spécial:Livre : il ajoute à l'encadré « Avec le livre en cours : **Générer le PDF du livre** · Ouvrir le livre dans Wikipedia2Book ». Au clic, il lit les articles par `action=collection&submodule=getcollection` (adresses `item.url`) et ouvre `https://wikipedia2book.toolforge.org/api/pdf/from-source?source=…&language=fr` (50 articles au plus, `MAX_URL_SOURCES`) ou `https://wikipedia2book.toolforge.org/?source=…` (200 au plus). Testé le 18/11/2026 avec Saint-Pierre (Martinique) et Montagne Pelée : l'outil s'ouvre avec les 2 articles, le PDF direct répond 200 (3,5 Mo, 6 s). Le texte complet du script est dans la demande publiée.

Limites : ni les chapitres ni le titre du livre ne passent par `?source=`. Les transmettre demanderait un paramètre de plus dans `GET /api/pdf/from-source` et dans `addSourcesFromAddress` (par exemple le wikitexte du livre, déjà lu par `POST /api/books/from-wikitext`).

## 2. de.wikipedia — Wikipedia:Technik/Text/Konverter — modification directe

Dans `== Konvertierung von Wikitext (Export) ==` › `=== PDF ===`, après la puce mediawiki2latex/wb2pdf et sa sous-puce :

```
* [[toolforge:wikipedia2book/|Wikipedia2Book]] (Toolforge, AGPL) – stellt einen Buch-PDF aus mehreren Artikeln zusammen (auch aus einer gespeicherten Buchseite oder einer Wikibooks-Sammlung): offizielle PDF-Dateien der Artikel mit Titelseite, Inhaltsverzeichnis und Seitenzahlen. Dokumentation: [[github:gmoulard/wikipedia2book|GitHub]]
```

Résumé : `Wikipedia2Book bei PDF ergänzt (Interessenkonflikt: ich bin der Autor des Werkzeugs)`

## 3. en.wikipedia — Help:Books/FAQ — proposition en page de discussion

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
For people who land here looking for a way to get a PDF of a whole book since the Collection rendering was turned off: [[toolforge:wikipedia2book/|Wikipedia2Book]] is a free (AGPL) Toolforge tool that builds a printable PDF from a saved book (Book: / User:…/Books/…), a Wikibooks printable version or compilation, or a list of pages from Wikipedia, Wikisource, Wikibooks, Wikivoyage, Wikiversity, Wikiquote, Wiktionary and Wikinews. It assembles the official PDF of each page (Special:DownloadAsPdf) with a cover, a table of contents and page numbers. It is listed on [[PDF export]] next to MediaWiki2LaTeX.

Disclosure: I am its author, and I should have said so in my edit summary: on 18 November 2026 I added a short entry for it under "Alternative" on [[Reading/Web/PDF Functionality]]. Feel free to adjust or revert it. The new paragraph has no translation unit yet; could a translation administrator mark the page for translation? Thanks. ~~~~
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

## 14. Phabricator — caractères CJK rares dans le PDF officiel de Wikisource (`../todo.md`, section 3)

Créer une tâche sur https://phabricator.wikimedia.org/maniphest/task/edit/form/1/, étiquettes `Proton` (service PDF) et `Wikisource`. Pas de conflit d'intérêts à signaler (signalement d'un bug du service de Wikimédia), mais préciser d'où vient le constat.

Titre : `Proton PDF: CJK Extension B+ characters render as blanks (missing font coverage)`

```
**Steps to reproduce**
# Open https://zh.wikisource.org/api/rest_v1/page/pdf/大南寔錄%2F大南寔錄前編%2F卷10/a4
# Look for 𡼢 (U+21F22), present in the wikitext of 大南寔錄/大南寔錄前編/卷10.

**Actual result**
The character leaves a blank space: the PDF uses LiberationSerif, which has no glyph for it, and no fallback font covers CJK Unified Ideographs Extension B and later (U+20000–U+3134F). Only the rare characters that Wikisource provides as images are visible.

**Expected result**
The character is rendered, as it is in the browser.

**Suggested fix**
Install a font covering CJK Extensions B–H in the PDF rendering environment, e.g. HanaMin (Debian package fonts-hanazono) or Plangothic / Jigmo, in addition to Noto CJK, which only covers the BMP and part of Extension B.

**Context**
Reported in November 2026 by PacmanD on the technical village pump of the Chinese Wikipedia, while using Wikipedia2Book (https://wikipedia2book.toolforge.org/), which embeds the official Wikimedia PDF of each page unchanged, so the tool cannot fix it on its side. Wikipedia2Book itself installs fonts-hanazono for the pages it generates.
```

Après création : noter le numéro de la tâche (`T…`) dans la section 18 des spécifications (`FunctionalSpec.fr.md`/`.en.md`) et cocher la ligne de `../todo.md`.

## 15. Phabricator — T224922 (revue de la maintenance de l'extension Collection) — commentaire

Tâche : [T224922 Code Stewardship Review: Collection Extension](https://phabricator.wikimedia.org/T224922), ouverte, 17 abonnés, dernière activité le 26/10/2026. C'est là que se discute l'avenir de Spécial:Livre :
- en octobre 2024, Bugreporter a demandé s'il fallait garder l'extension en production et a proposé à la place un outil sur Toolforge ou Cloud VPS, moins risqué ;
- le 25/06/2025, Steelpillow a proposé MediaWiki2LaTeX pour remplacer le PDF de livres ;
- le même jour, sbassett a compté environ 2 millions de requêtes vers Special:Book en 90 jours sur en.wikipedia, avec un usage notable sur es, de et it.

Wikipedia2Book répond exactement à la proposition de Bugreporter. Un commentaire factuel prévient les 17 abonnés, c'est-à-dire les personnes qui décideront du sort de l'extension.

```
For the record, since a Toolforge tool was suggested above as a lower-risk way to keep book PDFs: Wikipedia2Book (https://wikipedia2book.toolforge.org/, AGPL, https://github.com/gmoulard/wikipedia2book) does this. It takes a saved book (Book:… or User:…/Books/…), a Wikibooks printable version or table of contents, or a list of pages from eight Wikimedia projects, and builds one printable PDF from the official Special:DownloadAsPdf PDF of each page, with a cover, a table of contents, bookmarks, page numbers and a license page; books of more than 300 articles are split into volumes. Nothing is stored on the server.

If it helps the decision about Collection's download features, the PDF part of Special:Book could simply point to it, as fr:Modèle:Livre sauvegardé already does on every saved book; creating and saving books with Special:Book would keep working as it is. Disclosure: I am its author.
```

Avant de publier : si `Template:Saved book` sur en.wikipedia a aussi le lien, le citer en plus du modèle français. Ne pas commenter [T370740](https://phabricator.wikimedia.org/T370740) : c'est un bug sur le PDF d'un seul article, sans rapport avec les livres.

## 16. Toolhub — compléter la fiche existante

Toolhub a déjà deux fiches : [wikipedia2book](https://toolhub.wikimedia.org/tools/wikipedia2book), créée à la main (titre « wikipedia to PDF book »), et `toolforge-wikipedia2book`, importée automatiquement de Toolforge. La première est incomplète. Se connecter à Toolhub (compte Wikimédia), ouvrir la fiche, puis « Edit » :

| Champ | Valeur actuelle | Valeur proposée |
|---|---|---|
| Titre | wikipedia to PDF book | Wikipedia2Book |
| Sous-titre | vide | Printable PDF books from Wikimedia pages |
| Description | Wikipédia seulement, « no project setup » | Builds a printable PDF book from a saved book, a Wikibooks printable version or table of contents, or a list of pages from Wikipedia, Wikisource, Wikibooks, Wikivoyage, Wikiversity, Wikiquote, Wiktionary and Wikinews. Uses the official PDF of each page, with a cover, a table of contents, page numbers and a license page; volumes beyond 300 articles. |
| Mots-clés | vides | book, PDF, print, export, ebook, offline, Special:Book, Collection |
| Wikis | `*.wikipedia.org` | `*.wikipedia.org`, `*.wikisource.org`, `*.wikibooks.org`, `*.wikivoyage.org`, `*.wikiversity.org`, `*.wikiquote.org`, `*.wiktionary.org`, `*.wikinews.org` |
| Langues de l'interface | fr, en, arz | les 12 langues de `SUPPORTED_LANGUAGES` (`app/static/i18n.js`) |
| Signalement des bugs | vide | https://github.com/gmoulard/wikipedia2book/issues |
| Documentation développeur | vide | https://gmoulard.github.io/wikipedia2book/TechnicalSpec.en |
| Élément Wikidata | vide | le QID de l'action 13a, une fois l'élément créé |

Pas de conflit d'intérêts à signaler : c'est la fiche de ton propre outil.

## 17. Messages système de Spécial:Livre — en, es, de, it

Même demande que l'action 1, sur les wikis où sbassett a vu le plus de trafic vers Special:Book (T224922). Sur en.wikipedia, `MediaWiki:Coll-unknown subpage text` affiche encore le texte par défaut « This subpage of Book does not exist. »

17a. en.wikipedia — page [MediaWiki talk:Coll-unknown subpage text](https://en.wikipedia.org/wiki/MediaWiki_talk:Coll-unknown_subpage_text), nouvelle section `Edit request: point to a working PDF tool` :

```
{{edit fully-protected|MediaWiki:Coll-unknown subpage text|answered=no}}
Old links to book PDF rendering (Special:Book?bookcmd=render_collection…) now show "This subpage of Book does not exist." According to [[phab:T224922]], Special:Book still gets about 2 million requests every 90 days on this wiki. Please replace the message with:
: ''Wikipedia no longer produces PDFs of books from this page. Paste the address of the saved book into [[toolforge:wikipedia2book/|Wikipedia2Book]] to get a PDF; see also [[Help:Books]].''
and add to [[MediaWiki:Coll-notice-download-pdf-text]]:
: ''To get a PDF of a whole book, save it, then use [[toolforge:wikipedia2book/|Wikipedia2Book]], listed in [[Help:Books]] and [[Wikipedia:Books]].''
Disclosure: I am the author of Wikipedia2Book (conflict of interest), so please adapt or decline as you see fit. ~~~~
```

17b. es, de, it — attendre la réponse de l'action 1 (fr) et de 17a. Si l'une est acceptée, traduire le même texte et le déposer sur la page de demande aux administrateurs d'interface de chaque wiki (à repérer avant, par les liens interlangues de « Wikipedia:Interface administrators' noticeboard »).

Publiée le 18/11 sans attendre les réponses, sur es et de seulement (pas it : ancien compte bloqué) ; voir « Déjà fait ».

17b-es. es.wikipedia — page [Wikipedia:Administradores de interfaz/Tablón de solicitudes](https://es.wikipedia.org/wiki/Wikipedia:Administradores_de_interfaz/Tabl%C3%B3n_de_solicitudes), nouvelle section `MediaWiki:Coll-unknown subpage text y MediaWiki:Coll-notice-download-pdf-text: PDF de los libros`, résumé `Solicitud: mensajes de Especial:Libro (conflicto de intereses: soy el autor de Wikipedia2Book)` :

```
; Asunto
[[File:Wikipedia2book Logo.png|70px|link=toolforge:wikipedia2book/]]
Los enlaces antiguos a la generación de PDF de libros (Especial:Libro?bookcmd=render_collection…) muestran ahora el mensaje por defecto de [[MediaWiki:Coll-unknown subpage text]]. Según [[phab:T224922]], Especial:Libro sigue recibiendo muchas visitas en este wiki. Propongo crear [[MediaWiki:Coll-unknown subpage text]] con:
: ''Wikipedia ya no genera PDF de libros desde esta página. Pegue la dirección del libro guardado en [[toolforge:wikipedia2book/|Wikipedia2Book]] para obtener un PDF; véase también [[Ayuda:Libros]].''
y añadir a [[MediaWiki:Coll-notice-download-pdf-text]]:
: ''Para obtener el PDF de un libro completo, guárdelo y use [[toolforge:wikipedia2book/|Wikipedia2Book]].''
Aviso: soy el autor de Wikipedia2Book (conflicto de intereses); adapten o rechacen la propuesta como estimen oportuno.
; Usuario que lo solicita
* ~~~~
; Respuesta
(a rellenar por un administrador de interfaz)
```

17b-de. de.wikipedia — page [Wikipedia:Technik/Skin/MediaWiki/Änderungen](https://de.wikipedia.org/wiki/Wikipedia:Technik/Skin/MediaWiki/%C3%84nderungen), nouvelle section `MediaWiki:Coll-unknown subpage text und MediaWiki:Coll-notice-download-pdf-text: PDF von Büchern`, résumé `Änderungswunsch: Systemnachrichten von Spezial:Buch (Interessenkonflikt: ich bin der Autor von Wikipedia2Book)` :

```
[[File:Wikipedia2book Logo.png|70px|link=toolforge:wikipedia2book/]]
Alte Links zur PDF-Erzeugung von Büchern (Spezial:Buch?bookcmd=render_collection…) zeigen jetzt nur die Standardmeldung von [[MediaWiki:Coll-unknown subpage text]]. Laut [[phab:T224922]] wird Spezial:Buch in diesem Wiki weiterhin häufig aufgerufen. Vorschlag: [[MediaWiki:Coll-unknown subpage text]] anlegen mit
: ''Wikipedia erzeugt auf dieser Seite keine PDFs von Büchern mehr. Füge die Adresse des gespeicherten Buchs in [[toolforge:wikipedia2book/|Wikipedia2Book]] ein, um ein PDF zu erhalten; siehe auch [[Hilfe:Buchfunktion]].''
und in [[MediaWiki:Coll-notice-download-pdf-text]] ergänzen:
: ''Für ein PDF eines ganzen Buchs: Buch speichern, dann [[toolforge:wikipedia2book/|Wikipedia2Book]] verwenden.''
Hinweis: Ich bin der Autor von Wikipedia2Book (Interessenkonflikt); bitte nach eigenem Ermessen anpassen oder ablehnen. ~~~~
```

## 18. Réponses aux questions sur les livres en PDF (Teahouse, Help desk, Bistro…)

Pas de message à l'avance : répondre seulement à une vraie question récente, sans relancer une discussion archivée.

Où chercher (« book PDF », « livre PDF », « Special:Book », « Spécial:Livre ») :
- en.wikipedia : [Wikipedia:Teahouse](https://en.wikipedia.org/wiki/Wikipedia:Teahouse), [Wikipedia:Help desk](https://en.wikipedia.org/wiki/Wikipedia:Help_desk), [Help talk:Books](https://en.wikipedia.org/wiki/Help_talk:Books), [Help talk:Download as PDF](https://en.wikipedia.org/wiki/Help_talk:Download_as_PDF) ;
- fr.wikipedia : [Wikipédia:Le Bistro](https://fr.wikipedia.org/wiki/Wikip%C3%A9dia:Le_Bistro), [Wikipédia:Forum des nouveaux](https://fr.wikipedia.org/wiki/Wikip%C3%A9dia:Forum_des_nouveaux), [Discussion aide:Livres](https://fr.wikipedia.org/wiki/Discussion_aide:Livres).

Modèle de réponse (en) :

```
:Book PDF rendering from [[Special:Book]] was turned off in 2017. You can paste the address of your saved book (or a list of articles) into [[toolforge:wikipedia2book/|Wikipedia2Book]], which builds a PDF from the official PDF of each article, with a cover and a table of contents. (Disclosure: I wrote that tool.) ~~~~
```

Ne pas écrire sur [Wikipedia talk:WikiProject Wikipedia-Books](https://en.wikipedia.org/wiki/Wikipedia_talk:WikiProject_Wikipedia-Books) : aucune discussion depuis avril 2022.

## 19. Diff (blog communautaire de Wikimédia) — billet

Proposer un billet sur [diff.wikimedia.org](https://diff.wikimedia.org/) (relecture par l'équipe éditoriale). Le billet doit raconter une utilisation, pas présenter un produit, et signaler le conflit d'intérêts (« I am the developer of the tool »).

Titre proposé : `Printing Wikipedia again: PDF books from saved books and Wikibooks`

Plan :
1. Le constat : depuis 2017, Spécial:Livre ne produit plus de PDF, mais les livres enregistrés et les versions imprimables de Wikilivres existent toujours, et Special:Book reçoit encore des millions de visites (T224922).
2. Un exemple : *Épaves de la rade de Saint-Pierre* (`docs/static/Wrecks-of-Saint-Pierre-harbor.json`), de la page de livre au PDF imprimé, avec deux ou trois captures.
3. Le principe : PDF officiel de chaque page, rien de reconstruit, licence et auteurs repris, rien de gardé sur le serveur.
4. Les usages : classe, atelier hors ligne, version papier d'un livre de Wikilivres, recueil de Wikisource.
5. Les limites : 300 articles par volume, polices du PDF officiel (action 14).
6. Comment contribuer : traductions, GitHub, Phabricator.

### 19a. Texte complet du billet

Dans [story.fr.md](story.fr.md) et [story.en.md](story.en.md) (relecture de Junko Nakayama le 18/11, attribution de l'image à ajouter).

Ajouté le 18/11/2026 à la suite du brouillon [Diff n° 223381](https://diff.wikimedia.org/?p=223381) (après les étapes et captures déjà en place, statut « en attente de relecture » inchangé), sans la ligne « TO COMPLETE » des remerciements.

Texte à envoyer à Diff (anglais, copie de [story.en.md](story.en.md) au 18/11/2026, qui fait foi en cas d'écart) :

````markdown
# Printing Wikipedia again: the story of Wikipedia2Book

*Disclosure: I am the developer of Wikipedia2Book. This post tells why I built it, what it does, and how it was made.*

## Why I built it

For years, Wikipedia had a feature that many readers loved: you could gather articles into a "book" with Special:Book, and download it as a single PDF, or order a printed copy. In 2017 the PDF rendering of books was switched off. The saved books are still there, thousands of them, and Special:Book still receives a lot of visits (see Phabricator task T224922), but the button that turned them into a PDF no longer works. The printable versions of Wikibooks and the works of Wikisource have the same problem: the text is ready to be read on paper, but there is no simple way to get one clean, printable volume.

My own starting point was a set of articles I had started on the French Wikipedia: the wrecks of the harbour of Saint-Pierre, in Martinique, the ships sunk during the eruption of Mount Pelée in 1902. I had gathered them in a book page, [Les épaves de la rade de Saint-Pierre suite à l'éruption de la montagne Pelée en 1902](https://fr.wikipedia.org/wiki/Utilisateur:474D6F756C617264/Livres/Les_%C3%A9paves_de_la_rade_de_Saint-Pierre_suite_a_l'%C3%A9ruption_de_la_montagne_Pel%C3%A9e_en_1902), and I simply wanted to have them together, in a single PDF.

So I built a small tool to give that button back: [Wikipedia2Book](https://wikipedia2book.toolforge.org/).

The original idea was very modest, a sort of `cat pdf2 >> pdf1`: take the PDF files that Wikipedia already generates for each article, and put them end to end in a single PDF of many pages. That's all. But with modern development tools, adding one more feature was so easy that I added lots of them: a cover, a table of contents, chapters, other wikis, twelve languages, volumes… Oops! Maybe it's too much!!!

## What it does

You paste what you want to read, and you get a PDF.

- **Wikipedia's official PDFs, unchanged**: each article is the PDF generated by Wikipedia's own tool (the one behind the "Download as PDF" link), used as it is; Wikipedia2Book touches neither the text, nor the images, nor the references.
- **Sources**: the address of an article, a saved Wikipedia book (Special:Book, "Book:" pages), a Wikibooks book or its printable version, a Wikisource work, a list of pages (one per line: wiki links, URLs or titles), or a plain search. Pages can come from eight Wikimedia projects: Wikipedia, Wikisource, Wikibooks, Wikivoyage, Wikiversity, Wikiquote, Wiktionary and Wikinews, in any language, and you can mix languages in one book.
- **Organisation**: the order of a saved book is kept, with its chapters and subtitle. You can move articles and chapters, add chapters, find related articles from the links of a page, and add your own images, PDF files or any web page.
- **Editing**: title, subtitle, author, introduction and conclusion; a cover and a last page with a background image or colour; page format (A4, Letter, Legal and others), orientation and margins; table of contents at the start or the end, with clickable links; a number on every page.
- **The PDF**: a cover, a table of contents, each article, and a license page that names every source article with a link to its history, so the book respects the CC BY-SA license. Bookmarks let you jump from article to article.
- **A real printed book**: this is probably the most exciting part. The PDF is made to be printed (page formats, margins for binding, cover and last page), so you can send it to any print-on-demand service and buy a real printed, bound book, just as Special:Book used to offer.
- **Volumes**: large books are split automatically (300 articles per volume at most), each volume with its own cover, table of contents and numbering.
- **Languages**: the interface is translated into 12 languages (English, French, German, Spanish, Italian, Portuguese, Dutch, Turkish, Chinese, Japanese, Persian and Arabic, the last two right to left), and the pages added to the PDF are written in the chosen language.
- **Links**: everything the interface does is also available as a simple web address: a link such as `https://wikipedia2book.toolforge.org/api/pdf/from-source?source=<address of a book>` downloads the PDF directly, so a wiki page can offer its own "Download as PDF" link.

## How it works, and what it does not do

The content of the articles is never rebuilt. For each page, Wikipedia2Book asks Wikimedia for its official PDF, the one you get from the "Download as PDF" link of the article, and only adds what a book needs around it: cover, table of contents, chapter pages, page numbers and license. Text, images and references are exactly those of the wiki. Each page is only scaled and centred on the format chosen for the book.

The server keeps nothing. There is no account and no database: the book lives in your browser, and you save it yourself as a small JSON file that you can reopen, share, or publish so that others can rebuild the same book. The tool follows the Wikimedia User-Agent and API rules; it is free software (AGPL-3.0), hosted on Toolforge.

## What about mediawiki2latex?

While spreading the word about Wikipedia2Book, I discovered [mediawiki2latex](https://www.mediawiki.org/wiki/Mediawiki2latex), which I did not know. It is another really interesting tool, mentioned on many help pages of the wikis and used for years, especially for the printable versions of Wikibooks. The two tools share some features: starting from a page or a book of a wiki and turning it into a print-ready PDF. But their approach and their goals are different. mediawiki2latex converts the wiki content into LaTeX and rebuilds the whole layout, with LaTeX's fine typography, and also offers other formats. Wikipedia2Book rebuilds nothing: it assembles the official PDFs that Wikipedia already generates, as they are, and focuses on the book around them (cover, chapters, table of contents, license). They are two different answers to the same need, and everyone can choose the one that suits their book.

## How it was made

Wikipedia2Book is a very young project. The first line was written on 7 November 2026: I started from a written specification, first drafted with ChatGPT, and then built the application with Claude Code, an AI coding assistant, describing what I wanted and testing every step myself. The project is openly "vibe coded": the code is written and reviewed by AI agents, while I decide what the tool must do, check the results on real books, and keep a detailed specification and changelog in French and English.

- **7 November 2026**: first version, a single book in memory, chapters, PDF with bookmarks.
- **9 to 11 November**: import of saved Wikipedia books in their real order (the API returns links in alphabetical order, so the tool reads the wikitext), continuous page numbers, license page, the first interface languages, then twelve.
- **12 November**: version 1.0, online on Toolforge.
- **13 to 18 November**: one field for every kind of source, lists of pages, the other Wikimedia projects, Wikibooks and Wikisource contents pages, volumes, background images, web pages, and a lot of work so that big books do not make the server run out of memory.

In twelve days the tool went through more than 370 changes and 13 minor versions. Between 12 and 17 November it received about 12,000 requests on Toolforge.

That speed is the real story. Working with large language models inside a harness made for software development, an application in which the AI reads the code, edits it, runs the tests and checks the result in a browser, gave me a velocity I would never have imagined reaching alone: a feature I describe in the morning is usually written, tested, documented and online the same day. Speed does not mean shortcuts. Everything is in the open, in a [public repository](https://github.com/gmoulard/wikipedia2book/): every change is a readable commit, about thirty automated test files run before each deployment, security checks run on every change to the main branch, and the functional and technical specifications are kept in step with the code, so anyone can review what the tool does and how.

For me, vibe coding is not the end of the developer's job: it is another way of doing my work. I spend less time writing code and more time deciding what the tool must do, checking that it does it well and keeping the whole thing consistent: I do more software engineering than coding. With these tools, I really feel augmented. Of course, you have to learn how to use these new tools, but that has been my daily life as a computer scientist from the very beginning, back when HTML only existed in Tim Berners-Lee's lab at CERN in Geneva.

## What's next, and how you can help

The tool has limits: the fonts and layout of each article are those of the official Wikimedia PDF, where some scripts are not always displayed perfectly; a book is limited to 300 articles per volume.

You can help by trying it with your own saved books, reporting problems or ideas on [GitHub](https://github.com/gmoulard/wikipedia2book), improving a translation of the interface or of the help page, or simply adding a "Download as PDF" link on a book page of your wiki.

[[TO COMPLETE (optional): thanks, for example to the people who tested the tool or contributed to the code.]]
````

Version française (copie de [story.fr.md](story.fr.md) au 18/11/2026, qui fait foi en cas d'écart) :

````markdown
# Imprimer Wikipédia à nouveau : l'histoire de Wikipedia2Book

*Conflit d'intérêts : je suis le développeur de Wikipedia2Book. Ce billet raconte pourquoi je l'ai créé, ce qu'il fait et comment il a été fait.*

## Pourquoi je l'ai créé

Pendant des années, Wikipédia a proposé une fonction que beaucoup de lecteurs aimaient : rassembler des articles dans un « livre » avec Spécial:Livre, puis le télécharger en un seul PDF, ou en commander un exemplaire imprimé. En 2017, la production des PDF de livres a été arrêtée. Les livres enregistrés existent toujours, par milliers, et Spécial:Livre reçoit encore beaucoup de visites (voir la tâche Phabricator T224922), mais le bouton qui les transformait en PDF ne fonctionne plus. Les versions imprimables de Wikilivres et les œuvres de Wikisource ont le même problème : le texte est prêt à être lu sur papier, mais il n'existe pas de moyen simple d'en tirer un volume propre et imprimable.

Mon point de départ, c'était une série d'articles que j'avais commencés sur Wikipédia en français : les épaves de la rade de Saint-Pierre, en Martinique, les navires coulés lors de l'éruption de la montagne Pelée en 1902. Je les avais rassemblés dans une page de livre, [Les épaves de la rade de Saint-Pierre suite à l'éruption de la montagne Pelée en 1902](https://fr.wikipedia.org/wiki/Utilisateur:474D6F756C617264/Livres/Les_%C3%A9paves_de_la_rade_de_Saint-Pierre_suite_a_l'%C3%A9ruption_de_la_montagne_Pel%C3%A9e_en_1902), et je voulais simplement les avoir ensemble, dans un seul PDF.

J'ai donc écrit un petit outil pour retrouver ce bouton : [Wikipedia2Book](https://wikipedia2book.toolforge.org/).

L'idée de départ était très modeste une sort "$ cat pdf2 >> pdf1" : prendre les fichiers PDF que Wikipédia génère déjà pour chaque article, et les mettre bout à bout dans un seul PDF de plusieurs pages. C'est tout. Mais avec les outils de développement modernes, ajouter une fonctionnalité de plus était si facile que j'en ai ajouté plein: une couverture, une table des matières, des chapitres, les autres wikis, douze langues, des volumes… Oups ! c'est peut etre trop !!!

## Ce qu'il fait

On colle ce qu'on veut lire, on obtient un PDF.

- **Les PDF officiels de Wikipédia, sans modification** : chaque article est le PDF généré par l'outil de Wikipédia lui-même (celui du lien « Télécharger en PDF »), repris tel quel ; Wikipedia2Book ne touche ni au texte, ni aux images, ni aux références.
- **Sources** : l'adresse d'un article, un livre Wikipédia enregistré (Spécial:Livre, pages « Livre: »), un livre de Wikilivres ou sa version imprimable, une œuvre de Wikisource, une liste de pages (une par ligne : liens wiki, adresses ou titres), ou une simple recherche. Les pages peuvent venir de huit projets Wikimédia : Wikipédia, Wikisource, Wikilivres, Wikivoyage, Wikiversité, Wikiquote, Wiktionnaire et Wikinews, dans toutes les langues, et on peut mélanger les langues dans un même livre.
- **Organisation** : l'ordre d'un livre enregistré est conservé, avec ses chapitres et son sous-titre. On peut déplacer articles et chapitres, ajouter des chapitres, trouver des articles liés à partir des liens d'une page, et ajouter ses propres images, fichiers PDF ou n'importe quelle page web.
- **Édition** : titre, sous-titre, auteur, introduction et conclusion ; une couverture et une dernière page avec une image ou une couleur de fond ; format de page (A4, Letter, Legal et d'autres), orientation et marges ; table des matières au début ou à la fin, avec des liens cliquables ; numéro sur chaque page.
- **Le PDF** : une couverture, une table des matières, chaque article, et une page de licence qui cite chaque article source avec un lien vers son historique, pour que le livre respecte la licence CC BY-SA. Des signets permettent de passer d'un article à l'autre.
- **Un vrai livre imprimé** : c'est sûrement le plus intéressant, le PDF est fait pour l'impression (formats de page, marges pour la reliure, couverture et dernière page), on peut donc l'envoyer à n'importe quel service d'impression à la demande et acheter un vrai livre imprimé et relié, comme le proposait autrefois Spécial:Livre.
- **Volumes** : les gros livres sont découpés automatiquement (300 articles par volume maximum), chaque volume avec sa couverture, sa table des matières et sa numérotation.
- **Langues** : l'interface est traduite en 12 langues (anglais, français, allemand, espagnol, italien, portugais, néerlandais, turc, chinois, japonais, persan et arabe, ces deux dernières de droite à gauche), et les pages ajoutées au PDF sont écrites dans la langue choisie.
- **Liens** : tout ce que fait l'interface existe aussi sous forme d'une simple adresse web : un lien comme `https://wikipedia2book.toolforge.org/api/pdf/from-source?source=<adresse d'un livre>` télécharge directement le PDF, si bien qu'une page wiki peut proposer son propre lien « Télécharger en PDF ».

## Comment il fonctionne, et ce qu'il ne fait pas

Le contenu des articles n'est jamais reconstruit. Pour chaque page, Wikipedia2Book demande à Wikimédia son PDF officiel, celui qu'on obtient avec le lien « Télécharger en PDF » de l'article, et n'ajoute autour que ce dont un livre a besoin : couverture, table des matières, pages de chapitre, numéros de page et licence. Le texte, les images et les références sont exactement ceux du wiki. Chaque page est seulement mise à l'échelle et centrée sur le format choisi pour le livre.

Le serveur ne garde rien. Pas de compte, pas de base de données : le livre vit dans le navigateur, et on l'enregistre soi-même dans un petit fichier JSON qu'on peut rouvrir, partager ou publier pour que d'autres reconstruisent le même livre. L'outil respecte les règles de Wikimédia sur le User-Agent et l'API ; c'est un logiciel libre (AGPL-3.0), hébergé sur Toolforge.

## Et mediawiki2latex ?

En faisant connaître Wikipedia2Book, j'ai découvert [mediawiki2latex](https://www.mediawiki.org/wiki/Mediawiki2latex), que je ne connaissais pas. C'est un autre outil vraiment très intéressant, cité sur de nombreuses pages d'aide des wikis et utilisé depuis des années, notamment pour les versions imprimables de Wikilivres. Les deux outils ont des fonctionnalités communes : partir d'une page ou d'un livre d'un wiki et en faire un PDF prêt à imprimer. Mais leur démarche et leurs objectifs sont différents. mediawiki2latex convertit le contenu du wiki en LaTeX et recompose entièrement la mise en page, avec la typographie soignée de LaTeX, et propose aussi d'autres formats. Wikipedia2Book, lui, ne recompose rien : il assemble les PDF officiels que Wikipédia génère déjà, tels quels, et se concentre sur le livre qui les entoure (couverture, chapitres, table des matières, licence). Ce sont deux réponses différentes au même besoin, et chacun pourra choisir celle qui convient à son livre.

## Comment il a été fait

Wikipedia2Book est un projet très jeune. La première ligne a été écrite le 7 novembre 2026 : je suis parti d'une spécification écrite, d'abord rédigée avec ChatGPT, puis j'ai construit l'application avec Claude Code, un assistant de programmation par IA, en décrivant ce que je voulais et en testant moi-même chaque étape. Le projet est ouvertement « vibe codé » : le code est écrit et relu par des agents IA, tandis que je décide de ce que l'outil doit faire, vérifie les résultats sur de vrais livres et tiens une spécification et un historique détaillés, en français et en anglais.

- **7 novembre 2026** : première version, un seul livre en mémoire, des chapitres, un PDF avec signets.
- **9 au 11 novembre** : import des livres Wikipédia enregistrés dans leur ordre réel (l'API renvoie les liens par ordre alphabétique, l'outil lit donc le wikitexte), numérotation continue des pages, page de licence, les premières langues de l'interface, puis douze.
- **12 novembre** : version 1.0, en ligne sur Toolforge.
- **13 au 18 novembre** : un seul champ pour tous les types de sources, les listes de pages, les autres projets Wikimédia, les sommaires de Wikilivres et de Wikisource, les volumes, les images de fond, les pages web, et beaucoup de travail pour que les gros livres ne fassent pas manquer de mémoire au serveur.

En douze jours, l'outil a connu plus de 370 modifications et 13 versions mineures. Entre le 12 et le 17 novembre, il a reçu environ 12 000 requêtes sur Toolforge.

Cette vitesse, c'est la vraie histoire. Travailler avec des grands modèles de langage dans un environnement conçu pour le développement logiciel, une application dans laquelle l'IA lit le code, le modifie, lance les tests et vérifie le résultat dans un navigateur, m'a donné une vélocité que je n'aurais jamais immaginé atteinte seul : une fonctionnalité décrite le matin est en général écrite, testée, documentée et en ligne le jour même. Vitesse ne veut pas dire raccourcis. Tout est ouvert, dans un [dépôt public](https://github.com/gmoulard/wikipedia2book/) : chaque modification est un commit lisible, une trentaine de fichiers de tests automatiques tournent avant chaque déploiement, des contrôles de sécurité à chaque modification de la branche principale, et les spécifications fonctionnelle et technique suivent le code, si bien que chacun peut vérifier ce que fait l'outil et comment.

Pour moi, le vibe coding n'est pas la fin du métier de développeur : c'est une autre manière de faire mon travail. Je passe moins de temps à écrire du code et plus de temps à décider ce que l'outil doit faire, à vérifier qu'il le fait bien et à garder l'ensemble cohérent : je fais davantage de l'ingénierie logicielle que du code. Avec ces outils, je me sens vraiment augmenté. Bien sûr, il faut apprendre à se servir de ces nouveaux outils, mais c'est mon quotidien d'informaticien depuis le début quand le HTML n'existait que dans le laboratoire de Tim au CERN de Genève.

## La suite, et comment aider

L'outil a ses limites : la police et la mise en page de chaque article sont celles du PDF officiel de Wikimédia, où certaines écritures ne s'affichent pas toujours parfaitement ; un livre est limité à 300 articles par volume.

Vous pouvez aider en l'essayant avec vos propres livres enregistrés, en signalant problèmes et idées sur [GitHub](https://github.com/gmoulard/wikipedia2book), en améliorant une traduction de l'interface ou de la page d'aide, ou simplement en ajoutant un lien « Télécharger en PDF » sur une page de livre de votre wiki.

[[À COMPLÉTER (facultatif) : un remerciement, par exemple aux personnes qui ont testé ou contribué au code.]]
````


## 20. Présentations orales

20a. **WikiConvention francophone** : proposer une présentation courte (5 à 10 min) avec démo en direct (page de livre → PDF) dès l'appel à propositions sur Meta. [x] 18/11/2026 : fait par toi.

20b. **[Wikimania 2027](https://meta.wikimedia.org/wiki/Wikimania_2027)** (Santiago du Chili, 3e trimestre 2027, appel à propositions pas encore publié) : thème « Offline and print: PDF books from Wikimedia projects », en ligne si pas de déplacement. [x] 18/11/2026 : fait par toi.

## 21. Éducation et usage hors ligne — messages

21a. **Wikimédia France, programme éducation** : message à l'équipe éducation (formulaire de contact du site de Wikimédia France) pour proposer l'outil aux enseignants qui veulent imprimer un dossier d'articles, avec un PDF d'exemple.

21b. **Hors ligne** : page de discussion de [m:Offline](https://meta.wikimedia.org/wiki/Offline) (vérifier avant qu'elle est encore suivie) :

```
For offline and low-connectivity projects that need paper rather than files: [[toolforge:wikipedia2book/|Wikipedia2Book]] builds a printable PDF book from a list of articles or a saved book, from the official PDF of each page, in 12 interface languages and for eight Wikimedia projects. It may complement Kiwix where printed copies are needed (schools, libraries). Disclosure: I am its author. ~~~~
```
