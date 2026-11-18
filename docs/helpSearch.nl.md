# Hulp: wat kunt u invoeren in het veld „Het boek samenstellen”?

Het veld van de eerste stap accepteert veel meer dan een artikeltitel: een adres, een heel boek, een lijst van pagina's of de tekst van een boekpagina. Typ of plak wat u wilt toevoegen en klik op „Toevoegen”. De toegevoegde pagina's verschijnen onder het veld; in de volgende stap zet u ze in volgorde.

## In het kort

| U wilt toevoegen… | Voer in… | Voorbeeld |
|---|---|---|
| een artikel waarvan u de titel kent | de titel | `Montagne Pelée` |
| een bepaalde pagina | het adres | `https://fr.wikipedia.org/wiki/Épaves_de_la_rade_de_Saint-Pierre` |
| een artikel in een andere taal | de taalcode, een dubbele punt, de titel | `nl:Rotterdam` |
| een pagina van een ander Wikimedia-project | het projectvoorvoegsel en dan de titel | `voy:en:Lyon` |
| een heel boek | het adres van de inhoudsopgave of de boekpagina | `https://fr.wikibooks.org/wiki/Cosmologie` |
| meerdere pagina's tegelijk | één pagina per regel | zie „Meerdere pagina's tegelijk” |
| een boek dat op een pagina „Boek:” is voorbereid | de tekst van die pagina | zie „De tekst van een boekpagina plakken” |

## Een artikel zoeken

- Typ een paar letters: onder het veld verschijnen suggesties.
- De lijst naast het veld kiest in welke taal van Wikipedia wordt gezocht. Met „Alle” wordt de titel in alle talen van de lijst gezocht en toont elk resultaat zijn taal.
- Komt de titel precies overeen met een artikel, dan wordt het meteen toegevoegd. Een titel die doorverwijst naar een ander artikel voegt het doelartikel toe: `Napoléon Bonaparte` voegt „Napoléon Ier” toe.
- Anders verschijnen de zoekresultaten onder het veld: klik op het gewenste resultaat.
- Bij het eerste toegevoegde artikel worden de inleiding en de maker van de pagina voorgesteld als inleiding en auteur van het boek, in de stap Opmaak. U kunt ze wijzigen.

## Pagina's in een andere taal of van een ander project

Een volledig adres werkt altijd, bijvoorbeeld `https://fr.wikivoyage.org/wiki/Lyon`. Zet bij een titel een taalvoorvoegsel, een projectvoorvoegsel of beide ervoor:

| Project | Voorvoegsel | Voorbeeld |
|---|---|---|
| Wikipedia in een andere taal | taalcode | `nl:Rotterdam` |
| Wikisource | `s:` | `s:Les Misérables` |
| Wikibooks | `b:` | `b:Cosmologie` |
| Wikivoyage | `voy:` | `voy:en:Lyon` |
| Wikiversity | `v:` | `v:Python` |
| Wikiquote | `q:` | `q:Victor Hugo` |
| WikiWoordenboek | `wikt:` | `fr:wikt:chat` |
| Wikinieuws | `n:` | `n:Accueil` |

Zonder taalcode geldt de taal die naast het veld is gekozen. De volgorde van de voorvoegsels maakt niet uit. Elke pagina houdt op haar kaart de naam van haar project en haar taal.

## Hele boeken

- **Boekpagina op Wikipedia**: voer het adres of de naam in, bijvoorbeeld `Utilisateur:Alexbzh972/Livres/Martinique`. Alle artikelen worden toegevoegd in de volgorde van de pagina, met hoofdstukken, titel en ondertitel.
- **Wikibooks-compilatie**: voer het adres van de compilatie in, bijvoorbeeld `https://fr.wikibooks.org/wiki/Wikilivres:Compilations/Programmation_C`. De pagina's worden toegevoegd in de volgorde van de lijst, zoals bij een boekpagina op Wikipedia.
- **Boek op Wikibooks of werk op Wikisource**: voer het adres of de titel van de inhoudsopgave in, bijvoorbeeld `https://fr.wikibooks.org/wiki/Cosmologie` of `s:Les Misérables`. Een venster vraagt wat u wilt:
  - „Het hele boek”: alle pagina's, in hoofdstukken geordend;
  - „Het hele boek en de inhoudsopgave”: hetzelfde, met de inhoudsopgave vooraan;
  - „Alleen deze pagina”: alleen de inhoudsopgave;
  - „Annuleren”: er wordt niets toegevoegd.
- **Afdrukversie van Wikibooks**: voer het adres in van de pagina „afdrukversie” van het boek, bijvoorbeeld `https://fr.wikibooks.org/wiki/Programmation_C/Version_imprimable`. Is die pagina met de hand geschreven, dan worden haar pagina's toegevoegd met één hoofdstuk per kop; wordt ze uit de inhoudsopgave gemaakt, dan opent het keuzevenster van het boek.

## Meerdere pagina's tegelijk

Plak een lijst, één pagina per regel (voor een nieuwe regel tijdens het typen: Shift+Enter). Elke regel kan een titel, een adres of een pagina met voorvoegsel zijn, en kan ook geschreven worden als wikilink, Markdown-link of element van een genummerde lijst of opsomming:

```
[[Brest]]
[[nl:Amsterdam]]
[Suchet](https://fr.wikipedia.org/wiki/Suchet_(navire))
1. Lorient
* Concarneau
[[voy:en:Lyon]]
fr:wikt:chat
```

Een melding aan het eind zegt hoeveel pagina's zijn toegevoegd, hoeveel al in het boek stonden en hoeveel niet zijn gevonden. Niet gevonden regels blijven in het veld zodat u ze kunt verbeteren. Een inhoudsopgave in de lijst opent het hierboven beschreven keuzevenster.

## De tekst van een boekpagina plakken

U kunt de inhoud van een Wikipedia-pagina „Boek:” plakken: `== … ==` geeft de titel, `=== … ===` de ondertitel, elke regel `;` begint een hoofdstuk en elke link `[[…]]` voegt een artikel toe.

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

De tekst van een afdrukversie van Wikibooks, opgebouwd uit invoegingen `{{:…}}`, wordt op dezelfde manier aanvaard: elke kop `= … =` wordt een hoofdstuk.

## Een opgeslagen of gedeeld boek openen

- De knop „Opslaan” downloadt uw boek naar een bestand; de knop „Openen” laadt het later weer. Op de server wordt niets bewaard: dat bestand is uw enige reservekopie.
- Een link van de vorm `https://wikipedia2book.toolforge.org/?json=https://…` opent een online opgeslagen boek (alleen adressen met `https://`).
- Een link van de vorm `https://wikipedia2book.toolforge.org/?source=…` voegt zijn bronnen toe alsof u ze had ingevoerd: handig om een selectie van pagina's te delen.

## Wat het veld weigert

- websites die geen Wikimedia-projecten zijn;
- pagina's die geen inhoudspagina's zijn (overlegpagina's, hulp- of gemeenschapspagina's);
- bestanden van Wikimedia Commons: voeg ze in plaats daarvan toe als documenten in de stap Ordening, of als achtergrondafbeeldingen in de stap Opmaak;
- pagina's die niet bestaan.

De foutmelding legt uit wat er mis is. Ze komt van de server en blijft in het Frans, ongeacht de taal van de interface.

## En daarna?

- **Ordening**: zet de pagina's in volgorde, maak hoofdstukken, voeg eigen afbeeldingen of PDF's toe, splits het boek in delen. Boven 300 artikelen wordt het boek automatisch in delen gesplitst.
- **Opmaak**: titel, omslag, achtergrondafbeeldingen, inhoudsopgave, formaat en marges.
- **PDF maken**: elk artikel wordt overgenomen zoals Wikipedia het afdrukt, en alles samen vormt één boek dat klaar is om te drukken.
