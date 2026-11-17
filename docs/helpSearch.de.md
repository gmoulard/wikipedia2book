# Hilfe zum Feld „Buch erstellen“: alles, was Wikipedia2Book annimmt

Diese Seite listet alles auf, was Wikipedia2Book annimmt, mit jeweils einem Beispiel zum Ausprobieren **im Browser** und demselben Fall **über die API**. Sie dient zwei Zwecken: die Möglichkeiten zeigen und vor einer Veröffentlichung eine Prüfung von Hand durchführen. Sie ist eine Übersetzung der [französischen Referenzseite](helpSearch.fr.md).

Das maßgebliche Verhalten ist in der [funktionalen Spezifikation](FunctionalSpec.en.md) (Abschnitt 3.1 für die Quellen) und der [technischen Spezifikation](TechnicalSpec.en.md) (Abschnitt 13.3 für die API) beschrieben.

## So wird sie benutzt

- **Browser**: https://wikipedia2book.toolforge.org/ öffnen, das Beispiel in das Feld des Schritts „Buch erstellen“ einfügen und auf „Hinzufügen“ klicken. Eine Adresse, die mit `https://wikipedia2book.toolforge.org/?` beginnt, wird direkt geöffnet.
- **API**: die Adresse im Browser öffnen (das PDF wird heruntergeladen) oder an `curl -OJ` übergeben. `POST`-Aufrufe sind als `curl`-Befehle angegeben.
- **Version**: Version der Anwendung, ab der der Fall funktioniert. Die laufende Version zeigt https://wikipedia2book.toolforge.org/api/version.
- Die Spalte „Version“ gilt für den Browser. Auf der API-Seite gibt es `GET /api/pdf/from-source` (Abschnitte 1 bis 4) und den Parameter `?source=` der Seite seit 1.12.0 (in Produktion seit dem Abend des 16. November 2026, bevor sie diese Nummer erhielten): bei einer älteren Version das Buch als JSON an `POST /api/pdf` senden (9.3), nachdem jede Eingabe mit `POST /api/sources/resolve` erkannt wurde (9.1).
- Die Beispiele wurden am 17. November 2026 mit dem Code zur Erkennung der Quellen gegen die echten Wikis geprüft; eine seitdem umbenannte oder gelöschte Seite kann das Ergebnis ändern.

Abkürzungen: **T** = https://wikipedia2book.toolforge.org. In API-Adressen ist `language` die Sprache der im PDF erzeugten Titel (Umschlag, Inhaltsverzeichnis, Lizenz) und `wiki` die Sprache der Titel ohne Präfix.

## 1. Eine einzelne Seite

| Nr. | Fall | Browser: einzugeben | API | Erwartetes Ergebnis | Version |
|---|---|---|---|---|---|
| 1.1 | URL eines Wikipedia-Artikels | `https://fr.wikipedia.org/wiki/Épaves_de_la_rade_de_Saint-Pierre` | `T/api/pdf/from-source?source=https://fr.wikipedia.org/wiki/%C3%89paves_de_la_rade_de_Saint-Pierre` | Der Artikel wird hinzugefügt; Einleitung und Autor werden beim ersten Artikel vorgeschlagen | ≤ 1.9.7 |
| 1.2 | Genauer Titel | `Montagne Pelée` (Sprache FR neben dem Feld) | `T/api/pdf/from-source?source=Montagne%20Pel%C3%A9e&wiki=fr` | Der Artikel „Montagne Pelée“ wird hinzugefügt | ≤ 1.9.7 |
| 1.3 | Weitergeleiteter Titel | `Napoléon Bonaparte` | `T/api/pdf/from-source?source=Napol%C3%A9on%20Bonaparte&wiki=fr` | Der Weiterleitung wird gefolgt: „Napoléon Ier“ wird hinzugefügt | ≤ 1.9.7 |
| 1.4 | Titel ohne genaue Seite | `volcan martinique` | `T/api/sources/resolve` als `POST` (siehe 9.1): `kind` = `search` | Suchergebnisse erscheinen unter dem Feld und lassen sich mit einem Klick hinzufügen; die Erstellungs-API antwortet 404 mit dem betroffenen Text | ≤ 1.9.7 |
| 1.5 | Suche beim Tippen | `Saint-Pie` tippen, ohne zu bestätigen | `T/api/search?query=Saint-Pie&language=fr` | Vorschläge unter dem Feld | ≤ 1.9.7 |
| 1.6 | Titel in einer anderen Sprache | `nl:Rotterdam` | `T/api/pdf/from-source?source=nl:Rotterdam` | Der niederländische Artikel wird hinzugefügt, mit „NL“ markiert | 1.7.0 |
| 1.7 | Alle Sprachen | `Paris`, mit „Alle“ neben dem Feld gewählt | `T/api/search?query=Paris&language=all&limit=3` | Ergebnisse in jeder Sprache der Liste, jeweils mit ihrer Sprache markiert; der gewählte Artikel behält seine Sprache | 1.12.4 |

## 2. Andere Wikimedia-Projekte

| Nr. | Fall | Browser: einzugeben | API | Erwartetes Ergebnis | Version |
|---|---|---|---|---|---|
| 2.1 | Wikivoyage-Seite | `https://fr.wikivoyage.org/wiki/Lyon` | `T/api/pdf/from-source?source=https://fr.wikivoyage.org/wiki/Lyon` | Seite hinzugefügt, Karte mit „Wikivoyage“ markiert | 1.8.0 |
| 2.2 | Projekt- und Sprachpräfix | `[[voy:en:Lyon]]` | `T/api/pdf/from-source?source=voy:en:Lyon` | Englische Wikivoyage-Seite hinzugefügt | 1.8.0 |
| 2.3 | Wikiversity | `https://fr.wikiversity.org/wiki/Python` | `T/api/pdf/from-source?source=v:Python&wiki=fr` | Seite hinzugefügt, mit „Wikiversity“ markiert | 1.8.0 |
| 2.4 | Wikiquote | `https://fr.wikiquote.org/wiki/Victor_Hugo` | `T/api/pdf/from-source?source=q:Victor%20Hugo&wiki=fr` | Seite hinzugefügt, mit „Wikiquote“ markiert | 1.8.0 |
| 2.5 | Wiktionary, Präfixe in umgekehrter Reihenfolge | `fr:wikt:chat` | `T/api/pdf/from-source?source=fr:wikt:chat` | Seite hinzugefügt, mit „Wiktionary“ markiert | 1.8.0 |
| 2.6 | Wikinews | `https://fr.wikinews.org/wiki/Accueil` | `T/api/pdf/from-source?source=https://fr.wikinews.org/wiki/Accueil` | Seite hinzugefügt, mit „Wikinews“ markiert | 1.8.0 |
| 2.7 | Wikisource-Text (eine Seite) | `https://zh.wikisource.org/wiki/論語/學而第一` | `T/api/pdf/from-source?source=https://zh.wikisource.org/wiki/%E8%AB%96%E8%AA%9E/%E5%AD%B8%E8%80%8C%E7%AC%AC%E4%B8%80` | Seite hinzugefügt; chinesische Titel im PDF lesbar | 1.7.8 |
| 2.8 | Wikisource-Autorenseite | `https://fr.wikisource.org/wiki/Auteur:François_Rabelais` | `T/api/pdf/from-source?source=https://fr.wikisource.org/wiki/Auteur:Fran%C3%A7ois_Rabelais` | Seite unverändert hinzugefügt (Biografie und Werkliste) | 1.8.1 |

## 3. Bücher

| Nr. | Fall | Browser: einzugeben | API | Erwartetes Ergebnis | Version |
|---|---|---|---|---|---|
| 3.1 | Wikipedia-Buchseite per URL | `https://fr.wikipedia.org/wiki/Utilisateur:Alexbzh972/Livres/Martinique` | `T/api/books/generate-from-wikipedia-book?url=https://fr.wikipedia.org/wiki/Utilisateur:Alexbzh972/Livres/Martinique` | 113 Artikel in der Reihenfolge der Seite, Kapitel `;`, Untertitel `===`; Titel „Martinique“ | 1.3.0 |
| 3.2 | Buchseite über ihren Namen | `Utilisateur:Alexbzh972/Livres/Martinique` | `T/api/pdf/from-source?source=Utilisateur:Alexbzh972/Livres/Martinique` | Gleiches Ergebnis wie 3.1 | 1.3.0 |
| 3.3 | Inhaltsverzeichnis eines Wikibooks-Buchs | `https://fr.wikibooks.org/wiki/Cosmologie` | `T/api/pdf/from-source?source=b:Cosmologie&wiki=fr` | Fenster „Das ganze Buch / Das ganze Buch mit seinem Inhaltsverzeichnis / Nur diese Seite / Abbrechen“; „Das ganze Buch“ ergibt 27 Seiten in Kapiteln | 1.10.0 |
| 3.4 | Ganzes Buch mit Inhaltsverzeichnis | Wie 3.3, „Das ganze Buch mit seinem Inhaltsverzeichnis“ wählen | `T/api/pdf/from-source?source=b:Cosmologie&wiki=fr&summary=1` | Das Inhaltsverzeichnis zuerst, vor dem ersten Kapitel | 1.10.0 |
| 3.5 | Nur die Inhaltsverzeichnisseite | Wie 3.3, „Nur diese Seite“ wählen | `POST /api/pdf` mit nur der Inhaltsverzeichnisseite (siehe 9.3) | Die Inhaltsverzeichnisseite allein | 1.10.0 |
| 3.6 | Wikisource-Werk | `s:Les Misérables` (Sprache FR) | `T/api/pdf/from-source?source=s:Les%20Mis%C3%A9rables&wiki=fr` | Auswahlfenster; „Das ganze Buch“ ergibt 365 Kapitel in 5 Teilen, ohne „Texte entier“ | 1.11.0 |
| 3.7 | Von Hand geschriebene Druckversion (Adresse) | `https://fr.wikibooks.org/wiki/Hélices_de_navires_à_déplacement/Version_imprimable` | `T/api/pdf/from-source?source=https://fr.wikibooks.org/wiki/H%C3%A9lices_de_navires_%C3%A0_d%C3%A9placement/Version_imprimable` | 13 Seiten, ein Kapitel pro Überschrift `= … =`, Umschlag weggelassen, Titel „Hélices de navires à déplacement“ | 1.12.0 |
| 3.8 | Druckversion über `{{imprimable}}` (Adresse) | `https://fr.wikibooks.org/wiki/Programmation_C/Version_imprimable` | `T/api/pdf/from-source?source=https://fr.wikibooks.org/wiki/Programmation_C/Version_imprimable` | Das Auswahlfenster für das Inhaltsverzeichnis „Programmation C“ (21 Seiten) | 1.12.0 |

## 4. Seitenlisten (mehrere Zeilen)

Alle Zeilen auf einmal in das Feld einfügen (oder mit Umschalt+Eingabe trennen). Auf der API-Seite `source=` wiederholen (höchstens 50).

| Nr. | Fall | Einzugebende Zeile | Erwartetes Ergebnis | Version |
|---|---|---|---|---|
| 4.1 | Wiki-Link | `[[Brest]]` | „Brest“ hinzugefügt | 1.7.0 |
| 4.2 | Wiki-Link mit Sprache | `[[nl:Amsterdam]]` | Niederländischer Artikel hinzugefügt | 1.7.0 |
| 4.3 | Wiki-Link mit Beschriftung | `[[Frégate (bateau)\|Frégate]]` | „Frégate (bateau)“ hinzugefügt | 1.7.0 |
| 4.4 | Markdown-Link, Klammern in der URL | `[Suchet](https://fr.wikipedia.org/wiki/Suchet_(navire))` | „Suchet (navire)“ hinzugefügt | 1.7.0 |
| 4.5 | Nummer am Zeilenanfang | `1. Lorient` | „Lorient“ hinzugefügt | 1.7.0 |
| 4.6 | Aufzählungszeichen am Zeilenanfang | `* Concarneau` (auch `-`, `•`, `#`) | „Concarneau“ hinzugefügt | 1.7.0 |
| 4.7 | Nicht gefundene Zeile | `Xyzzy inexistant` | Die Zeile bleibt im Feld, die Schlussmeldung zählt sie als „nicht gefunden“ | 1.7.0 |
| 4.8 | Inhaltsverzeichnis in einer Liste | `b:Programmation Python` | Das Auswahlfenster öffnet sich für dieses Inhaltsverzeichnis; seine Kapitel werden nicht übernommen | 1.10.0 |

Vollständige Liste zum Einfügen im Browser:

```
[[Brest]]
[[nl:Amsterdam]]
[Suchet](https://fr.wikipedia.org/wiki/Suchet_(navire))
1. Lorient
* Concarneau
[[voy:en:Lyon]]
fr:wikt:chat
```

Erwartetes Ergebnis: „7 Seite(n) hinzugefügt, 0 bereits im Buch, 0 nicht gefunden.“

API, gleiche Liste: `T/api/pdf/from-source?source=[[Brest]]&source=[[nl:Amsterdam]]&source=1.%20Lorient&source=*%20Concarneau&source=[[voy:en:Lyon]]&source=fr:wikt:chat&wiki=fr`

## 5. Eingefügter Buchtext

| Nr. | Fall | Einzufügender Text | API | Erwartetes Ergebnis | Version |
|---|---|---|---|---|---|
| 5.1 | Wikipedia-Syntax „Buch:“ | Block 5.1 unten | `curl` 5.1 unten | Titel „Ports bretons“, Untertitel „Guide des ports“, Kapitel „Finistère“ und „Morbihan“, „Brest“ vorne ohne Kapitel | 1.12.0 |
| 5.2 | Wikibooks-Druckversion | Block 5.2 unten | `curl` 5.2 unten | 3 Wikibooks-Seiten in 3 Kapiteln, Lizenz weggelassen | 1.12.0 |

Block 5.1:

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

Block 5.2:

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

Nur die Struktur lesen, ohne PDF: gleicher Inhalt an `POST /api/books/from-wikitext`.

## 6. Ein gespeichertes Buch öffnen (JSON)

| Nr. | Fall | Browser | API | Erwartetes Ergebnis | Version |
|---|---|---|---|---|---|
| 6.1 | JSON-Buch per Adresse | `T/?json=https://gmoulard.github.io/wikipedia2book/static/Wrecks-of-Saint-Pierre-harbor.json` | `T/api/pdf/from-json?url=https://gmoulard.github.io/wikipedia2book/static/Wrecks-of-Saint-Pierre-harbor.json&language=en` | Das Buch öffnet sich („Buch importiert.“) mit seinen Hintergrundbildern und seinem Dokument | 1.9.6 |
| 6.2 | Wikibooks-Buch als JSON | `T/?json=https://gmoulard.github.io/wikipedia2book/static/Cosmologie.json` | `T/api/pdf/from-json?url=https://gmoulard.github.io/wikipedia2book/static/Cosmologie.json` | 27 Seiten in 8 Kapiteln | 1.9.6 |
| 6.3 | Lokale JSON-Datei | Schaltfläche „Öffnen“, eine mit „Speichern“ exportierte Datei wählen | `curl -OJ -X POST 'T/api/pdf/from-json' -H 'Content-Type: application/json' --data @buch.json` | Das Buch öffnet sich / das PDF wird erstellt | ≤ 1.9.7 (Browser), 1.12.0 (API) |
| 6.4 | JSON, dann weitere Quellen | `T/?json=https://gmoulard.github.io/wikipedia2book/static/Cosmologie.json&source=b:Programmation%20Python` | — | Das JSON-Buch öffnet sich, dann das Auswahlfenster für das hinzugefügte Inhaltsverzeichnis | 1.12.0 |
| 6.5 | Quellen in der Adresse der Seite | `T/?source=https://fr.wikibooks.org/wiki/Cosmologie&source=Montagne%20Pel%C3%A9e&wiki=fr` | Siehe 3.3 und 1.2 | Jede Quelle wird hinzugefügt, als wäre sie eingegeben worden, Rückfrage inbegriffen | 1.12.0 |
| 6.6 | Abgelehnte Adresse | `T/?json=http://example.com/livre.json` | `T/api/pdf/from-json?url=http://example.com/livre.json` | Fehlermeldung, nichts wird importiert; die API antwortet 422 „doit commencer par https://“ | 1.9.6 |

## 7. Dokumente und Hintergrundbilder

| Nr. | Fall | Browser | API (Feld des JSON-Buchs) | Erwartetes Ergebnis | Version |
|---|---|---|---|---|---|
| 7.1 | Bild oder PDF vom Computer | Schritt Organisation, „Datei auswählen +“ | `uploaded_documents[]` mit `data_base64` | Dokument wie ein Artikel im Buch platziert, höchstens 15 MB | ≤ 1.9.7 |
| 7.2 | Dokument per Adresse | Schritt Organisation, Adressfeld: `https://upload.wikimedia.org/wikipedia/commons/1/16/La_Pel%C3%A9e_vue_du_Carbet.jpg` | `uploaded_documents[]` mit `"url": "https://upload.wikimedia.org/…"` | Nur die Adresse wird gespeichert; der Server lädt das Bild bei jeder Erstellung herunter | 1.10.0 |
| 7.3 | Dokument per Commons-Dateiseite | `https://commons.wikimedia.org/wiki/File:La_Pelée_vue_du_Carbet.jpg` | `"url": "https://commons.wikimedia.org/wiki/File:La_Pel%C3%A9e_vue_du_Carbet.jpg"` | Das Bild (Vorschau mit 2 000 px) wird verwendet; bei einem PDF das Original | 1.10.0 (Browser), 1.12.0 (API) |
| 7.4 | PDF per Dateiseite | `https://commons.wikimedia.org/wiki/File:Interpersonal_communication_and_coordination_in_Wikipedia_Working_Paper_30_June_2020.pdf` | Gleiche Adresse in `uploaded_documents[].url` | Das Original-PDF wird eingebunden, Seiten an das Buchformat angepasst | 1.10.0 (Browser), 1.12.0 (API) |
| 7.5 | Hintergrundbild des Umschlags | Schritt Bearbeitung, „Hintergrundbild des Umschlags“, Datei oder Adresse (7.2 oder 7.3) | `cover_image`: `{"title": "…", "url": "…"}` oder `data_base64` | Hintergrund des Umschlags, ohne Verzerrung | 1.9.6 |
| 7.6 | Bild der letzten Seite | Schritt Bearbeitung, „Hintergrundbild der letzten Seite“ | `back_image` | Eigene Seite nach der Lizenz | 1.9.6 |
| 7.7 | Nicht erreichbare Adresse | Dokument `https://example.org/inexistant.png` | Gleiche Adresse | Erstellung abgebrochen, die betroffene Adresse wird genannt; 502 über die API | 1.10.0 |

## 8. Organisation und Layout

| Nr. | Fall | Browser | API (JSON-Buch an `POST /api/pdf`) | Erwartetes Ergebnis | Version |
|---|---|---|---|---|---|
| 8.1 | Verwandte Artikel | Schaltfläche „Verwandte Artikel“ eines Artikels | `POST /api/explore` | Links des Artikels vorgeschlagen, in der Reihenfolge der Seite | ≤ 1.9.7 |
| 8.2 | Kapitel und Reihenfolge | Schritt Organisation, „Kapitel erstellen“, Ziehen und Ablegen | `chapters`, `article_order`, `unassigned_first` | Das PDF folgt der angezeigten Reihenfolge | ≤ 1.9.7 |
| 8.3 | Inhaltsverzeichnis | Schritt Bearbeitung: keines, Anfang, Ende | `table_of_contents`, `toc_position` (`start`, `end`, `before:<Schlüssel>`) | Verzeichnis an der richtigen Stelle, anklickbare Links | 1.9.6 |
| 8.4 | Format, Ausrichtung, Ränder | Schritt Bearbeitung | `page_format`, `orientation`, `margin_*_mm`, `custom_width_mm` | Alle Seiten im gewählten Format | ≤ 1.9.7 |
| 8.5 | Seitennummern | „Seiten nummerieren“ | `page_numbers` | Nummern unten auf der Seite, außer auf dem Umschlag | ≤ 1.9.7 |
| 8.6 | Sprache der PDF-Titel | Sprachauswahl oben | Parameter `language` (12 Sprachen) | Umschlag, Verzeichnis, Lizenz in der gewählten Sprache | ≤ 1.9.7 |
| 8.7 | Manuelle Bandtrennung | Schritt Organisation, „Neuer Band“ | `volume_breaks`: `["before:<Schlüssel>"]`, dann `?volume=N` | Ein PDF pro Band, Nummerierung beginnt wieder bei 1 | 1.9.2 (Browser), 1.12.0 (API) |
| 8.8 | Mehr als 300 Artikel | Buch 3.1 + weitere Seiten bis über 300 | `POST /api/books/volumes` für den Plan, dann `POST /api/pdf?volume=1`, `?volume=2`… | Automatische Teilung zwischen Kapiteln, „Band 1/2“…; ohne `volume` Ablehnung 413 mit der Zahl der Bände | 1.9.0 (Browser), 1.12.0 (API) |

## 9. API-Aufrufe ohne PDF

| Nr. | Fall | Aufruf | Erwartetes Ergebnis |
|---|---|---|---|
| 9.1 | Eine Eingabe erkennen | `curl -X POST 'T/api/sources/resolve' -H 'Content-Type: application/json' --data '{"input":"volcan martinique","language":"fr"}'` | `kind`: `article`, `book`, `subpages` oder `search` |
| 9.2 | Struktur einer Buchseite | `curl -X POST 'T/api/books/structure' -H 'Content-Type: application/json' --data '{"url":"https://fr.wikipedia.org/wiki/Utilisateur:Alexbzh972/Livres/Martinique"}'` | Artikel, Untertitel, Kapitel |
| 9.3 | PDF eines als JSON beschriebenen Buchs | `curl -OJ -X POST 'T/api/pdf?language=fr' -H 'Content-Type: application/json' --data '{"name":"Test","main_articles":[{"title":"Cosmologie","language":"fr","site":"wikibooks","url":"https://fr.wikibooks.org/wiki/Cosmologie","selected":true}]}'` | PDF einer einzigen Inhaltsverzeichnisseite |
| 9.4 | Die Erstellung verfolgen | Gleicher Inhalt an `POST /api/pdf/stream` | NDJSON-Zeilen `progress`, `wait`, dann `done` und das PDF |
| 9.5 | Vorgeschlagene Einleitung und Autor | `T/api/articles/intro?title=Montagne%20Pel%C3%A9e&language=fr` | Erster Absatz und Ersteller der Seite |
| 9.6 | Laufende Version | `T/api/version` | Version, Commit, Artikelgrenze |

## 10. Abgelehnte Eingaben

Die Fehlermeldungen kommen vom Server und bleiben auf Französisch, unabhängig von der Sprache der Oberfläche.

| Nr. | Eingabe | Erwartetes Ergebnis |
|---|---|---|
| 10.1 | `https://example.com/wiki/Chat` | „L'URL doit pointer vers une page HTTPS d'un projet Wikimédia…“; 422 |
| 10.2 | `https://fr.wikibooks.org/wiki/Wikilivres:Le_Bistro` | „Seules les pages de contenu de fr.wikibooks.org…“; 422 |
| 10.3 | `https://commons.wikimedia.org/wiki/File:La_Pelée_vue_du_Carbet.jpg` im Feld Quellen | Als Quelle abgelehnt (Commons hat keine Adresse `<Sprache>.<Projekt>.org`); als Dokument oder Hintergrundbild angenommen (7.3) |
| 10.4 | `https://fr.wikipedia.org/wiki/Page_qui_n_existe_pas` | „La page … est introuvable“; 404 |
| 10.5 | Leeres Feld | „Saisissez …“; 422 |
| 10.6 | Buch ohne ausgewählten Artikel, dann „PDF erstellen“ | Meldung „Wähle mindestens einen Artikel aus, bevor du das PDF erstellst.“; 400 |
