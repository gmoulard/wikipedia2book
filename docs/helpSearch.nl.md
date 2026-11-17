# Hulp bij het veld „Het boek samenstellen”: alles wat Wikipedia2Book accepteert

Deze pagina somt alles op wat Wikipedia2Book accepteert, met voor elk geval een voorbeeld om **in de browser** te proberen en hetzelfde geval **via de API**. Ze dient twee doelen: de mogelijkheden tonen en vóór een release met de hand controleren. Ze is een vertaling van de [Franse referentiepagina](helpSearch.fr.md).

Het referentiegedrag staat in de [functionele specificaties](FunctionalSpec.en.md) (paragraaf 3.1 voor de bronnen) en de [technische specificaties](TechnicalSpec.en.md) (paragraaf 13.3 voor de API).

## Hoe te gebruiken

- **Browser**: open https://wikipedia2book.toolforge.org/, plak het voorbeeld in het veld van de stap „Het boek samenstellen” en klik op „Toevoegen”. Een adres dat begint met `https://wikipedia2book.toolforge.org/?` opent direct.
- **API**: open het adres in de browser (de PDF wordt gedownload) of geef het aan `curl -OJ`. `POST`-aanroepen staan als `curl`-opdrachten.
- **Versie**: versie van de toepassing vanaf welke het geval werkt. De online versie staat op https://wikipedia2book.toolforge.org/api/version.
- De kolom „Versie” geldt voor de browser. Aan de API-kant bestaan `GET /api/pdf/from-source` (paragrafen 1 tot 4) en de parameter `?source=` van de pagina sinds 1.12.0 (in productie sinds de avond van 16 november 2026, voordat ze dat nummer kregen): stuur bij een oudere versie het boek als JSON naar `POST /api/pdf` (9.3), na elke invoer te hebben herkend met `POST /api/sources/resolve` (9.1).
- De voorbeelden zijn op 17 november 2026 gecontroleerd met de code voor het herkennen van bronnen tegen de echte wiki's; een pagina die sindsdien is hernoemd of verwijderd kan het resultaat veranderen.

Afkortingen: **T** = https://wikipedia2book.toolforge.org. In API-adressen is `language` de taal van de in de PDF gemaakte titels (omslag, inhoudsopgave, licentie) en `wiki` de taal van titels zonder voorvoegsel.

## 1. Eén pagina

| Nr. | Geval | Browser: in te voeren | API | Verwacht resultaat | Versie |
|---|---|---|---|---|---|
| 1.1 | URL van een Wikipedia-artikel | `https://fr.wikipedia.org/wiki/Épaves_de_la_rade_de_Saint-Pierre` | `T/api/pdf/from-source?source=https://fr.wikipedia.org/wiki/%C3%89paves_de_la_rade_de_Saint-Pierre` | Het artikel wordt toegevoegd; inleiding en auteur voorgesteld bij het eerste artikel | ≤ 1.9.7 |
| 1.2 | Exacte titel | `Montagne Pelée` (taal FR naast het veld) | `T/api/pdf/from-source?source=Montagne%20Pel%C3%A9e&wiki=fr` | Het artikel „Montagne Pelée” wordt toegevoegd | ≤ 1.9.7 |
| 1.3 | Doorverwezen titel | `Napoléon Bonaparte` | `T/api/pdf/from-source?source=Napol%C3%A9on%20Bonaparte&wiki=fr` | De doorverwijzing wordt gevolgd: „Napoléon Ier” wordt toegevoegd | ≤ 1.9.7 |
| 1.4 | Titel zonder exacte pagina | `volcan martinique` | `T/api/sources/resolve` als `POST` (zie 9.1): `kind` = `search` | Zoekresultaten verschijnen onder het veld en worden met één klik toegevoegd; de API voor het maken antwoordt 404 met de betreffende tekst | ≤ 1.9.7 |
| 1.5 | Zoeken tijdens het typen | `Saint-Pie` typen zonder te bevestigen | `T/api/search?query=Saint-Pie&language=fr` | Suggesties onder het veld | ≤ 1.9.7 |
| 1.6 | Titel in een andere taal | `nl:Rotterdam` | `T/api/pdf/from-source?source=nl:Rotterdam` | Het Nederlandse artikel wordt toegevoegd, gemarkeerd „NL” | 1.7.0 |
| 1.7 | Alle talen | `Paris`, met „Alle” gekozen naast het veld | `T/api/search?query=Paris&language=all&limit=3` | Resultaten in elke taal van de lijst, elk gemarkeerd met zijn taal; het gekozen artikel houdt de zijne | 1.12.4 |

## 2. Andere Wikimedia-projecten

| Nr. | Geval | Browser: in te voeren | API | Verwacht resultaat | Versie |
|---|---|---|---|---|---|
| 2.1 | Wikivoyage-pagina | `https://fr.wikivoyage.org/wiki/Lyon` | `T/api/pdf/from-source?source=https://fr.wikivoyage.org/wiki/Lyon` | Pagina toegevoegd, kaart gemarkeerd „Wikivoyage” | 1.8.0 |
| 2.2 | Project- en taalvoorvoegsel | `[[voy:en:Lyon]]` | `T/api/pdf/from-source?source=voy:en:Lyon` | Engelse Wikivoyage-pagina toegevoegd | 1.8.0 |
| 2.3 | Wikiversity | `https://fr.wikiversity.org/wiki/Python` | `T/api/pdf/from-source?source=v:Python&wiki=fr` | Pagina toegevoegd, gemarkeerd „Wikiversity” | 1.8.0 |
| 2.4 | Wikiquote | `https://fr.wikiquote.org/wiki/Victor_Hugo` | `T/api/pdf/from-source?source=q:Victor%20Hugo&wiki=fr` | Pagina toegevoegd, gemarkeerd „Wikiquote” | 1.8.0 |
| 2.5 | WikiWoordenboek, voorvoegsels omgekeerd | `fr:wikt:chat` | `T/api/pdf/from-source?source=fr:wikt:chat` | Pagina toegevoegd, gemarkeerd „WikiWoordenboek” | 1.8.0 |
| 2.6 | Wikinieuws | `https://fr.wikinews.org/wiki/Accueil` | `T/api/pdf/from-source?source=https://fr.wikinews.org/wiki/Accueil` | Pagina toegevoegd, gemarkeerd „Wikinieuws” | 1.8.0 |
| 2.7 | Wikisource-tekst (één pagina) | `https://zh.wikisource.org/wiki/論語/學而第一` | `T/api/pdf/from-source?source=https://zh.wikisource.org/wiki/%E8%AB%96%E8%AA%9E/%E5%AD%B8%E8%80%8C%E7%AC%AC%E4%B8%80` | Pagina toegevoegd; Chinese titels leesbaar in de PDF | 1.7.8 |
| 2.8 | Auteurspagina op Wikisource | `https://fr.wikisource.org/wiki/Auteur:François_Rabelais` | `T/api/pdf/from-source?source=https://fr.wikisource.org/wiki/Auteur:Fran%C3%A7ois_Rabelais` | Pagina ongewijzigd toegevoegd (biografie en lijst van werken) | 1.8.1 |

## 3. Boeken

| Nr. | Geval | Browser: in te voeren | API | Verwacht resultaat | Versie |
|---|---|---|---|---|---|
| 3.1 | Wikipedia-boekpagina via URL | `https://fr.wikipedia.org/wiki/Utilisateur:Alexbzh972/Livres/Martinique` | `T/api/books/generate-from-wikipedia-book?url=https://fr.wikipedia.org/wiki/Utilisateur:Alexbzh972/Livres/Martinique` | 113 artikelen in de volgorde van de pagina, hoofdstukken `;`, ondertitel `===`; titel „Martinique” | 1.3.0 |
| 3.2 | Boekpagina via haar naam | `Utilisateur:Alexbzh972/Livres/Martinique` | `T/api/pdf/from-source?source=Utilisateur:Alexbzh972/Livres/Martinique` | Zelfde resultaat als 3.1 | 1.3.0 |
| 3.3 | Inhoudsopgave van een Wikibooks-boek | `https://fr.wikibooks.org/wiki/Cosmologie` | `T/api/pdf/from-source?source=b:Cosmologie&wiki=fr` | Venster „Het hele boek / Het hele boek en de inhoudsopgave / Alleen deze pagina / Annuleren”; „Het hele boek” geeft 27 pagina's in hoofdstukken | 1.10.0 |
| 3.4 | Heel boek met inhoudsopgave | Zoals 3.3, kies „Het hele boek en de inhoudsopgave” | `T/api/pdf/from-source?source=b:Cosmologie&wiki=fr&summary=1` | De inhoudsopgave eerst, vóór het eerste hoofdstuk | 1.10.0 |
| 3.5 | Alleen de inhoudsopgavepagina | Zoals 3.3, kies „Alleen deze pagina” | `POST /api/pdf` met alleen de inhoudsopgavepagina (zie 9.3) | De inhoudsopgavepagina alleen | 1.10.0 |
| 3.6 | Werk op Wikisource | `s:Les Misérables` (taal FR) | `T/api/pdf/from-source?source=s:Les%20Mis%C3%A9rables&wiki=fr` | Keuzevenster; „Het hele boek” geeft 365 hoofdstukken in 5 delen, zonder „Texte entier” | 1.11.0 |
| 3.7 | Met de hand geschreven afdrukversie (adres) | `https://fr.wikibooks.org/wiki/Hélices_de_navires_à_déplacement/Version_imprimable` | `T/api/pdf/from-source?source=https://fr.wikibooks.org/wiki/H%C3%A9lices_de_navires_%C3%A0_d%C3%A9placement/Version_imprimable` | 13 pagina's, één hoofdstuk per titel `= … =`, omslag weggelaten, titel „Hélices de navires à déplacement” | 1.12.0 |
| 3.8 | Afdrukversie via `{{imprimable}}` (adres) | `https://fr.wikibooks.org/wiki/Programmation_C/Version_imprimable` | `T/api/pdf/from-source?source=https://fr.wikibooks.org/wiki/Programmation_C/Version_imprimable` | Het keuzevenster voor de inhoudsopgave „Programmation C” (21 pagina's) | 1.12.0 |

## 4. Paginalijsten (meerdere regels)

Plak alle regels tegelijk in het veld (of scheid ze met Shift+Enter). Herhaal aan de API-kant `source=` (hoogstens 50).

| Nr. | Geval | In te voeren regel | Verwacht resultaat | Versie |
|---|---|---|---|---|
| 4.1 | Wikilink | `[[Brest]]` | „Brest” toegevoegd | 1.7.0 |
| 4.2 | Wikilink met taal | `[[nl:Amsterdam]]` | Nederlands artikel toegevoegd | 1.7.0 |
| 4.3 | Wikilink met tekst | `[[Frégate (bateau)\|Frégate]]` | „Frégate (bateau)” toegevoegd | 1.7.0 |
| 4.4 | Markdown-link, haakjes in de URL | `[Suchet](https://fr.wikipedia.org/wiki/Suchet_(navire))` | „Suchet (navire)” toegevoegd | 1.7.0 |
| 4.5 | Nummer aan het begin van de regel | `1. Lorient` | „Lorient” toegevoegd | 1.7.0 |
| 4.6 | Opsommingsteken aan het begin van de regel | `* Concarneau` (ook `-`, `•`, `#`) | „Concarneau” toegevoegd | 1.7.0 |
| 4.7 | Niet gevonden regel | `Xyzzy inexistant` | De regel blijft in het veld, de slotmelding telt hem als „niet gevonden” | 1.7.0 |
| 4.8 | Inhoudsopgave in een lijst | `b:Programmation Python` | Het keuzevenster opent voor die inhoudsopgave; haar hoofdstukken worden niet overgenomen | 1.10.0 |

Volledige lijst om in de browser te plakken:

```
[[Brest]]
[[nl:Amsterdam]]
[Suchet](https://fr.wikipedia.org/wiki/Suchet_(navire))
1. Lorient
* Concarneau
[[voy:en:Lyon]]
fr:wikt:chat
```

Verwacht resultaat: „7 pagina('s) toegevoegd, 0 al in het boek, 0 niet gevonden.”

API, zelfde lijst: `T/api/pdf/from-source?source=[[Brest]]&source=[[nl:Amsterdam]]&source=1.%20Lorient&source=*%20Concarneau&source=[[voy:en:Lyon]]&source=fr:wikt:chat&wiki=fr`

## 5. Geplakte boektekst

| Nr. | Geval | Te plakken tekst | API | Verwacht resultaat | Versie |
|---|---|---|---|---|---|
| 5.1 | Wikipedia-syntaxis „Boek:” | Blok 5.1 hieronder | `curl` 5.1 hieronder | Titel „Ports bretons”, ondertitel „Guide des ports”, hoofdstukken „Finistère” en „Morbihan”, „Brest” vooraan zonder hoofdstuk | 1.12.0 |
| 5.2 | Afdrukversie van Wikibooks | Blok 5.2 hieronder | `curl` 5.2 hieronder | 3 Wikibooks-pagina's in 3 hoofdstukken, licentie weggelaten | 1.12.0 |

Blok 5.1:

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

Blok 5.2:

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

Alleen de structuur lezen, zonder PDF: zelfde inhoud naar `POST /api/books/from-wikitext`.

## 6. Een opgeslagen boek openen (JSON)

| Nr. | Geval | Browser | API | Verwacht resultaat | Versie |
|---|---|---|---|---|---|
| 6.1 | JSON-boek via adres | `T/?json=https://gmoulard.github.io/wikipedia2book/static/Wrecks-of-Saint-Pierre-harbor.json` | `T/api/pdf/from-json?url=https://gmoulard.github.io/wikipedia2book/static/Wrecks-of-Saint-Pierre-harbor.json&language=en` | Het boek opent („Boek geïmporteerd.”) met zijn achtergrondafbeeldingen en zijn document | 1.9.6 |
| 6.2 | Wikibooks-boek als JSON | `T/?json=https://gmoulard.github.io/wikipedia2book/static/Cosmologie.json` | `T/api/pdf/from-json?url=https://gmoulard.github.io/wikipedia2book/static/Cosmologie.json` | 27 pagina's in 8 hoofdstukken | 1.9.6 |
| 6.3 | Lokaal JSON-bestand | Knop „Openen”, kies een bestand dat met „Opslaan” is geëxporteerd | `curl -OJ -X POST 'T/api/pdf/from-json' -H 'Content-Type: application/json' --data @boek.json` | Het boek opent / de PDF wordt gemaakt | ≤ 1.9.7 (browser), 1.12.0 (API) |
| 6.4 | JSON, daarna andere bronnen | `T/?json=https://gmoulard.github.io/wikipedia2book/static/Cosmologie.json&source=b:Programmation%20Python` | — | Het JSON-boek opent, daarna het keuzevenster voor de toegevoegde inhoudsopgave | 1.12.0 |
| 6.5 | Bronnen in het adres van de pagina | `T/?source=https://fr.wikibooks.org/wiki/Cosmologie&source=Montagne%20Pel%C3%A9e&wiki=fr` | Zie 3.3 en 1.2 | Elke bron wordt toegevoegd alsof ze was ingevoerd, vraag inbegrepen | 1.12.0 |
| 6.6 | Geweigerd adres | `T/?json=http://example.com/livre.json` | `T/api/pdf/from-json?url=http://example.com/livre.json` | Foutmelding, niets geïmporteerd; de API antwoordt 422 „doit commencer par https://” | 1.9.6 |

## 7. Documenten en achtergrondafbeeldingen

| Nr. | Geval | Browser | API (veld van het JSON-boek) | Verwacht resultaat | Versie |
|---|---|---|---|---|---|
| 7.1 | Afbeelding of PDF van de computer | Stap Ordening, „Een bestand kiezen +” | `uploaded_documents[]` met `data_base64` | Document als een artikel in het boek geplaatst, hoogstens 15 MB | ≤ 1.9.7 |
| 7.2 | Document via adres | Stap Ordening, adresveld: `https://upload.wikimedia.org/wikipedia/commons/1/16/La_Pel%C3%A9e_vue_du_Carbet.jpg` | `uploaded_documents[]` met `"url": "https://upload.wikimedia.org/…"` | Alleen het adres wordt bewaard; de server downloadt de afbeelding bij elke keer maken | 1.10.0 |
| 7.3 | Document via een Commons-bestandspagina | `https://commons.wikimedia.org/wiki/File:La_Pelée_vue_du_Carbet.jpg` | `"url": "https://commons.wikimedia.org/wiki/File:La_Pel%C3%A9e_vue_du_Carbet.jpg"` | De afbeelding (voorvertoning van 2 000 px) wordt gebruikt; bij een PDF het origineel | 1.10.0 (browser), 1.12.0 (API) |
| 7.4 | PDF via bestandspagina | `https://commons.wikimedia.org/wiki/File:Interpersonal_communication_and_coordination_in_Wikipedia_Working_Paper_30_June_2020.pdf` | Zelfde adres in `uploaded_documents[].url` | De originele PDF wordt ingevoegd, pagina's aangepast aan het boekformaat | 1.10.0 (browser), 1.12.0 (API) |
| 7.5 | Achtergrondafbeelding van de omslag | Stap Opmaak, „Achtergrondafbeelding van de omslag”, bestand of adres (7.2 of 7.3) | `cover_image`: `{"title": "…", "url": "…"}` of `data_base64` | Achtergrond van de omslag, zonder vervorming | 1.9.6 |
| 7.6 | Afbeelding van de laatste pagina | Stap Opmaak, „Achtergrondafbeelding van de laatste pagina” | `back_image` | Eigen pagina na de licentie | 1.9.6 |
| 7.7 | Onbereikbaar adres | Document `https://example.org/inexistant.png` | Zelfde adres | Maken afgebroken, het betreffende adres wordt genoemd; 502 via de API | 1.10.0 |

## 8. Ordening en opmaak

| Nr. | Geval | Browser | API (JSON-boek naar `POST /api/pdf`) | Verwacht resultaat | Versie |
|---|---|---|---|---|---|
| 8.1 | Verwante artikelen | Knop „Verwante artikelen” van een artikel | `POST /api/explore` | Links van het artikel voorgesteld, in de volgorde van de pagina | ≤ 1.9.7 |
| 8.2 | Hoofdstukken en volgorde | Stap Ordening, „Een hoofdstuk maken”, slepen en neerzetten | `chapters`, `article_order`, `unassigned_first` | De PDF volgt de getoonde volgorde | ≤ 1.9.7 |
| 8.3 | Inhoudsopgave | Stap Opmaak: geen, begin, einde | `table_of_contents`, `toc_position` (`start`, `end`, `before:<sleutel>`) | Inhoudsopgave op de juiste plaats, klikbare links | 1.9.6 |
| 8.4 | Formaat, oriëntatie, marges | Stap Opmaak | `page_format`, `orientation`, `margin_*_mm`, `custom_width_mm` | Alle pagina's in het gekozen formaat | ≤ 1.9.7 |
| 8.5 | Paginanummers | „Pagina's nummeren” | `page_numbers` | Nummers onderaan de pagina, behalve op de omslag | ≤ 1.9.7 |
| 8.6 | Taal van de PDF-titels | Taalkeuze bovenaan | Parameter `language` (12 talen) | Omslag, inhoudsopgave, licentie in de gekozen taal | ≤ 1.9.7 |
| 8.7 | Handmatige splitsing in delen | Stap Ordening, „Nieuw deel” | `volume_breaks`: `["before:<sleutel>"]`, daarna `?volume=N` | Eén PDF per deel, nummering begint opnieuw bij 1 | 1.9.2 (browser), 1.12.0 (API) |
| 8.8 | Meer dan 300 artikelen | Boek 3.1 + andere pagina's tot boven 300 | `POST /api/books/volumes` voor het plan, daarna `POST /api/pdf?volume=1`, `?volume=2`… | Automatische splitsing tussen hoofdstukken, „Deel 1/2”…; zonder `volume` weigering 413 met het aantal delen | 1.9.0 (browser), 1.12.0 (API) |

## 9. API-aanroepen zonder PDF

| Nr. | Geval | Aanroep | Verwacht resultaat |
|---|---|---|---|
| 9.1 | Een invoer herkennen | `curl -X POST 'T/api/sources/resolve' -H 'Content-Type: application/json' --data '{"input":"volcan martinique","language":"fr"}'` | `kind`: `article`, `book`, `subpages` of `search` |
| 9.2 | Structuur van een boekpagina | `curl -X POST 'T/api/books/structure' -H 'Content-Type: application/json' --data '{"url":"https://fr.wikipedia.org/wiki/Utilisateur:Alexbzh972/Livres/Martinique"}'` | Artikelen, ondertitel, hoofdstukken |
| 9.3 | PDF van een in JSON beschreven boek | `curl -OJ -X POST 'T/api/pdf?language=fr' -H 'Content-Type: application/json' --data '{"name":"Test","main_articles":[{"title":"Cosmologie","language":"fr","site":"wikibooks","url":"https://fr.wikibooks.org/wiki/Cosmologie","selected":true}]}'` | PDF van één inhoudsopgavepagina |
| 9.4 | Het maken volgen | Zelfde inhoud naar `POST /api/pdf/stream` | NDJSON-regels `progress`, `wait`, daarna `done` en de PDF |
| 9.5 | Voorgestelde inleiding en auteur | `T/api/articles/intro?title=Montagne%20Pel%C3%A9e&language=fr` | Eerste alinea en maker van de pagina |
| 9.6 | Online versie | `T/api/version` | Versie, commit, artikellimiet |

## 10. Geweigerde invoer

De foutmeldingen komen van de server en blijven in het Frans, ongeacht de taal van de interface.

| Nr. | Invoer | Verwacht resultaat |
|---|---|---|
| 10.1 | `https://example.com/wiki/Chat` | „L'URL doit pointer vers une page HTTPS d'un projet Wikimédia…”; 422 |
| 10.2 | `https://fr.wikibooks.org/wiki/Wikilivres:Le_Bistro` | „Seules les pages de contenu de fr.wikibooks.org…”; 422 |
| 10.3 | `https://commons.wikimedia.org/wiki/File:La_Pelée_vue_du_Carbet.jpg` in het bronnenveld | Geweigerd als bron (Commons heeft geen adres `<taal>.<project>.org`); aanvaard als document of achtergrondafbeelding (7.3) |
| 10.4 | `https://fr.wikipedia.org/wiki/Page_qui_n_existe_pas` | „La page … est introuvable”; 404 |
| 10.5 | Leeg veld | „Saisissez …”; 422 |
| 10.6 | Boek zonder geselecteerd artikel, daarna „PDF maken” | Melding „Selecteer minstens één artikel voordat je de PDF maakt.”; 400 |
