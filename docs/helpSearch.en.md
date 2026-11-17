# Help: what can you enter in the "Build the book" field?

The field of the first step accepts much more than an article title: an address, a whole book, a list of pages or the text of a book page. Type or paste what you want to add, then click "Add". The pages you add appear below the field; you will arrange them in the next step.

## At a glance

| You want to add… | Enter… | Example |
|---|---|---|
| an article whose title you know | its title | `Montagne Pelée` |
| a specific page | its address | `https://fr.wikipedia.org/wiki/Épaves_de_la_rade_de_Saint-Pierre` |
| an article in another language | the language code, a colon, the title | `nl:Rotterdam` |
| a page from another Wikimedia project | the project prefix, then the title | `voy:en:Lyon` |
| a whole book | the address of its contents page or book page | `https://fr.wikibooks.org/wiki/Cosmologie` |
| several pages at once | one page per line | see "Several pages at once" |
| a book prepared on a "Book:" page | the text of that page | see "Pasting the text of a book page" |

## Searching for an article

- Type a few letters: suggestions appear below the field.
- The list next to the field chooses which Wikipedia language to search. With "All", the title is searched in every language of the list and each result shows its language.
- If the title exactly matches an article, it is added straight away. A title that redirects to another article adds the target article: `Napoléon Bonaparte` adds "Napoléon Ier".
- Otherwise, the search results appear below the field: click the one you want.
- For the first article you add, its introduction and the creator of the page are suggested as the book's introduction and author, in the Editing step. You can change them.

## Pages in another language or from another project

A full address always works, for example `https://fr.wikivoyage.org/wiki/Lyon`. With a title, put a language prefix, a project prefix, or both in front of it:

| Project | Prefix | Example |
|---|---|---|
| Wikipedia in another language | language code | `nl:Rotterdam` |
| Wikisource | `s:` | `s:Les Misérables` |
| Wikibooks | `b:` | `b:Cosmologie` |
| Wikivoyage | `voy:` | `voy:en:Lyon` |
| Wikiversity | `v:` | `v:Python` |
| Wikiquote | `q:` | `q:Victor Hugo` |
| Wiktionary | `wikt:` | `fr:wikt:chat` |
| Wikinews | `n:` | `n:Accueil` |

Without a language code, the language chosen next to the field is used. The order of the prefixes does not matter. Each page keeps the name of its project and its language on its card.

## Whole books

- **Wikipedia book page**: enter its address or name, for example `Utilisateur:Alexbzh972/Livres/Martinique`. All its articles are added in the order of the page, with its chapters, title and subtitle.
- **Wikibooks book or Wikisource work**: enter the address or title of its contents page, for example `https://fr.wikibooks.org/wiki/Cosmologie` or `s:Les Misérables`. A window asks what you want:
  - "The whole book": all its pages, arranged in chapters;
  - "The whole book and its table of contents": the same, with the contents page first;
  - "Only this page": the contents page alone;
  - "Cancel": nothing is added.
- **Wikibooks printable version**: enter the address of the book's "printable version" page, for example `https://fr.wikibooks.org/wiki/Programmation_C/Version_imprimable`. If that page is written by hand, its pages are added with one chapter per heading; if it is generated from the contents page, the book's choice window opens.

## Several pages at once

Paste a list, one page per line (to start a new line while typing, use Shift+Enter). Each line can be a title, an address or a prefixed page, and can also be written as a wiki link, a Markdown link or a numbered or bulleted list item:

```
[[Brest]]
[[nl:Amsterdam]]
[Suchet](https://fr.wikipedia.org/wiki/Suchet_(navire))
1. Lorient
* Concarneau
[[voy:en:Lyon]]
fr:wikt:chat
```

A message at the end tells you how many pages were added, how many were already in the book and how many were not found. Lines that were not found stay in the field so you can correct them. A book contents page in the list opens the choice window described above.

## Pasting the text of a book page

You can paste the content of a Wikipedia "Book:" page: `== … ==` gives the title, `=== … ===` the subtitle, each `;` line starts a chapter and each `[[…]]` link adds an article.

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

The text of a Wikibooks printable version, made of `{{:…}}` inclusions, is accepted in the same way: each `= … =` heading becomes a chapter.

## Opening a saved or shared book

- The "Save" button downloads your book to a file; the "Open" button loads it again later. Nothing is kept on the server: this file is your only backup.
- A link of the form `https://wikipedia2book.toolforge.org/?json=https://…` opens a book saved online (`https://` addresses only).
- A link of the form `https://wikipedia2book.toolforge.org/?source=…` adds its sources as if you had typed them: handy for sharing a selection of pages.

## What the field refuses

- sites that are not Wikimedia projects;
- pages that are not content pages (talk pages, help or community pages);
- Wikimedia Commons files: add them instead as documents in the Organization step, or as background images in the Editing step;
- pages that do not exist.

The error message explains what is wrong. It comes from the server and stays in French, whatever the interface language.

## What next?

- **Organization**: arrange the pages, create chapters, add your own images or PDFs, split the book into volumes. Beyond 300 articles, the book is split into volumes automatically.
- **Editing**: title, cover, background images, table of contents, page format and margins.
- **Generate PDF**: each article is taken as Wikipedia prints it, and everything forms a single book ready to print.
