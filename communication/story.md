# Printing Wikipedia again: the story of Wikipedia2Book

Billet pour [Diff](https://diff.wikimedia.org/?p=223381) (action 19 de [communication-brouillons.md](communication-brouillons.md), relecture de Junko Nakayama le 18/11/2026).

Les passages entre `[[À COMPLÉTER : …]]` sont ta propre histoire, à écrire avec tes mots (ou à supprimer). Le reste vient du dépôt (historique Git, CHANGELOG, statistiques Toolviews).

**Attribution de l'image demandée par la relectrice** : dans Diff, cliquer sur l'image → « Replace » → « Open Media Library », puis à droite remplir : *Author* = l'auteur indiqué sur la page Commons de [File:Wikipedia2book Logo.png](https://commons.wikimedia.org/wiki/File:Wikipedia2book_Logo.png) ; *License* = la licence indiquée sur cette même page (à recopier telle quelle) ; *Link* = `https://commons.wikimedia.org/wiki/File:Wikipedia2book_Logo.png`. Même chose pour chaque capture ajoutée (une capture du PDF contient des images Wikipédia : citer leurs fichiers Commons, ou choisir une page sans image). Voir la [checklist de publication](https://diff.wikimedia.org/publishing-checklist/).

---

*Disclosure: I am the developer of Wikipedia2Book. This post tells why I built it, what it does, and how it was made.*

## Why I built it

For years, Wikipedia had a feature that many readers loved: you could gather articles into a "book" with Special:Book, and download it as a single PDF, or order a printed copy. In 2017 the PDF rendering of books was switched off. The saved books are still there, thousands of them, and Special:Book still receives a lot of visits (see Phabricator task T224922), but the button that turned them into a PDF no longer works. The printable versions of Wikibooks and the works of Wikisource have the same problem: the text is ready to be read on paper, but there is no simple way to get one clean, printable volume.

[[À COMPLÉTER : ton point de départ personnel. Par exemple : quel livre tu voulais imprimer, pour qui (classe, famille, association, lecture hors ligne), ce que tu as essayé avant (Special:Book, mediawiki2latex, export article par article), et pourquoi tu as décidé de l'écrire toi-même. Le livre d'exemple, « Les épaves de la rade de Saint-Pierre », sur les navires coulés lors de l'éruption de la montagne Pelée en 1902, peut servir de fil rouge si c'est lui qui t'a lancé.]]

So I built a small tool to give that button back: [Wikipedia2Book](https://wikipedia2book.toolforge.org/).

The original idea was very modest: take the PDF files that Wikipedia already generates for each article, and put them end to end in a single PDF of many pages. That's all. But with modern development tools, adding one more feature was so easy that I kept adding them: a cover, a table of contents, chapters, other wikis, twelve languages, volumes… Oops!

## What it does

You paste what you want to read, and you get one PDF book.

- **Sources**: the address of an article, a saved Wikipedia book (Special:Book / "Book:" pages), a Wikibooks book or its printable version, a Wikisource work, a list of pages (one per line, wiki links, URLs or titles), or a plain search. Pages can come from eight Wikimedia projects: Wikipedia, Wikisource, Wikibooks, Wikivoyage, Wikiversity, Wikiquote, Wiktionary and Wikinews, in any language, and you can mix languages in one book.
- **Organisation**: the order of a saved book is kept, with its chapters and subtitle. You can move articles and chapters, add chapters, find related articles from the links of a page, and add your own images, PDF files or any web page.
- **Editing**: title, subtitle, author, introduction and conclusion; a cover and a last page with a background image or colour; page format (A4, Letter, Legal and others), orientation and margins; table of contents at the start or the end, with clickable links; page numbers on every page.
- **The PDF**: a cover, a table of contents, each article, and a license page that names every source article with a link to its history, so the book respects CC BY-SA. Bookmarks let you jump from article to article.
- **Volumes**: large books are split automatically (300 articles per volume), each volume with its own cover, contents and numbering.
- **Languages**: the interface is translated into 12 languages (English, French, German, Spanish, Italian, Portuguese, Dutch, Turkish, Chinese, Japanese, Persian and Arabic, the last two right to left), and the pages added to the PDF are written in the chosen language.
- **Links**: everything the interface does is also available as a simple web address: a link such as `https://wikipedia2book.toolforge.org/api/pdf/from-source?source=<address of a book>` downloads the PDF directly, so a wiki page can offer its own "Download as PDF" link.

## How it works, and what it does not do

The content of the articles is never rebuilt. For each page, Wikipedia2Book asks Wikimedia for its official PDF, the same one you get from the "Download as PDF" link of the article, and only adds what a book needs around it: cover, table of contents, chapter pages, page numbers and license. Text, images and references are exactly those of the wiki. Each page is only scaled and centred on the format chosen for the book.

The server keeps nothing. There is no account and no database: your book lives in your browser, and you save it yourself as a small JSON file that you can reopen, share, or publish so that others can rebuild the same book. The tool follows the Wikimedia User-Agent and API rules, and is free software (AGPL-3.0), hosted on Toolforge.

## How it was made

Wikipedia2Book is a very young project. The first line was written on 7 November 2026: I started from a written specification, first drafted with ChatGPT, and then built the application with Claude Code, an AI coding assistant, describing what I wanted and testing every step myself. The project is openly "vibe coded": the code is written and reviewed by AI agents, while I decide what the tool must do, check the results on real books, and keep a detailed specification and changelog in French and English.

- **7 November**: first version, a single book in memory, chapters, PDF with bookmarks.
- **9 to 11 November**: import of saved Wikipedia books in their real order (the API returns links in alphabetical order, so the tool reads the wikitext), continuous page numbers, license page, the first interface languages, then twelve.
- **12 November**: version 1.0, online on Toolforge.
- **13 to 18 November**: one field for every kind of source, lists of pages, the other Wikimedia projects, Wikibooks and Wikisource contents pages, volumes, background images, web pages, and a lot of work so that big books do not make the server run out of memory.

In twelve days the tool went through more than 370 changes and 13 minor versions. Between 12 and 17 November it received about 12,000 requests on Toolforge.

That speed is the real story. Working with large language models inside a harness made for software development, an application in which the AI reads the code, edits it, runs the tests and checks the result in a browser, gave me a velocity I could never have reached alone: a feature I describe in the morning is usually written, tested, documented and online the same day. Speed does not mean shortcuts. Everything is in the open, in a [public repository](https://github.com/gmoulard/wikipedia2book/): every change is a readable commit, about thirty automated test files run before each deployment, security checks run on every change to the main branch, and the functional and technical specifications are kept in step with the code, so anyone can review what the tool does and how.

[[À COMPLÉTER : ce que t'a appris ce mode de développement, ce qui a été difficile (par exemple l'ordre des articles, la mémoire sur Toolforge, les écritures rares en chinois), ce qui t'a surpris.]]

## What's next, and how you can help

The tool has limits: the fonts and layout of each article are those of the official Wikimedia PDF, and some scripts are not always displayed perfectly there; a book is limited to 300 articles per volume.

You can help by trying it with your own saved books, reporting problems or ideas on [GitHub](https://github.com/gmoulard/wikipedia2book), improving a translation of the interface or of the help page, or simply adding a "Download as PDF" link on a book page of your wiki.

[[À COMPLÉTER (facultatif) : un remerciement, par exemple aux personnes qui ont testé ou contribué au code.]]
