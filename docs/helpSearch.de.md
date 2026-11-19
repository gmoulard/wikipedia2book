# Hilfe: Was kann man in das Feld „Buch erstellen“ eingeben?

<!-- {% raw %} -->

Das Feld des ersten Schritts nimmt viel mehr an als einen Artikeltitel: eine Adresse, ein ganzes Buch, eine Liste von Seiten oder den Text einer Buchseite. Tippen oder fügen Sie ein, was Sie hinzufügen möchten, und klicken Sie dann auf „Hinzufügen“. Die hinzugefügten Seiten erscheinen unter dem Feld; im nächsten Schritt ordnen Sie sie.

## Auf einen Blick

| Sie möchten hinzufügen… | Geben Sie ein… | Beispiel |
|---|---|---|
| einen Artikel, dessen Titel Sie kennen | seinen Titel | `Montagne Pelée` |
| eine bestimmte Seite | ihre Adresse | `https://fr.wikipedia.org/wiki/Épaves_de_la_rade_de_Saint-Pierre` |
| einen Artikel in einer anderen Sprache | Sprachcode, Doppelpunkt, Titel | `nl:Rotterdam` |
| eine Seite eines anderen Wikimedia-Projekts | das Projektpräfix, dann den Titel | `voy:en:Lyon` |
| ein ganzes Buch | die Adresse seines Inhaltsverzeichnisses oder seiner Buchseite | `https://fr.wikibooks.org/wiki/Cosmologie` |
| mehrere Seiten auf einmal | eine Seite pro Zeile | siehe „Mehrere Seiten auf einmal“ |
| ein auf einer Seite „Buch:“ vorbereitetes Buch | den Text dieser Seite | siehe „Den Text einer Buchseite einfügen“ |

## Einen Artikel suchen

- Tippen Sie ein paar Buchstaben: Vorschläge erscheinen unter dem Feld.
- Die Liste neben dem Feld wählt die Sprache der Wikipedia, in der gesucht wird. Mit „Alle“ wird der Titel in allen Sprachen der Liste gesucht, und jedes Ergebnis zeigt seine Sprache.
- Entspricht der Titel genau einem Artikel, wird dieser direkt hinzugefügt. Ein Titel, der auf einen anderen Artikel weiterleitet, fügt den Zielartikel hinzu: `Napoléon Bonaparte` fügt „Napoléon Ier“ hinzu.
- Andernfalls erscheinen die Suchergebnisse unter dem Feld: Klicken Sie auf das gewünschte.
- Beim ersten hinzugefügten Artikel werden seine Einleitung und der Ersteller der Seite als Einleitung und Autor des Buchs im Schritt Bearbeitung vorgeschlagen. Sie können sie ändern.

## Seiten in einer anderen Sprache oder aus einem anderen Projekt

Eine vollständige Adresse funktioniert immer, zum Beispiel `https://fr.wikivoyage.org/wiki/Lyon`. Setzen Sie vor einen Titel ein Sprachpräfix, ein Projektpräfix oder beides:

| Projekt | Präfix | Beispiel |
|---|---|---|
| Wikipedia in einer anderen Sprache | Sprachcode | `nl:Rotterdam` |
| Wikisource | `s:` | `s:Les Misérables` |
| Wikibooks | `b:` | `b:Cosmologie` |
| Wikivoyage | `voy:` | `voy:en:Lyon` |
| Wikiversity | `v:` | `v:Python` |
| Wikiquote | `q:` | `q:Victor Hugo` |
| Wiktionary | `wikt:` | `fr:wikt:chat` |
| Wikinews | `n:` | `n:Accueil` |

Ohne Sprachcode gilt die neben dem Feld gewählte Sprache. Die Reihenfolge der Präfixe spielt keine Rolle. Jede Seite behält auf ihrer Karte den Namen ihres Projekts und ihre Sprache.

## Ganze Bücher

- **Wikipedia-Buchseite**: Geben Sie ihre Adresse oder ihren Namen ein, zum Beispiel `Utilisateur:Alexbzh972/Livres/Martinique`. Alle Artikel werden in der Reihenfolge der Seite hinzugefügt, mit Kapiteln, Titel und Untertitel.
- **Wikibooks-Sammlung**: Geben Sie die Adresse der Sammlung ein, zum Beispiel `https://fr.wikibooks.org/wiki/Wikilivres:Compilations/Programmation_C`. Ihre Seiten werden in der Reihenfolge der Liste hinzugefügt, wie bei einer Wikipedia-Buchseite.
- **Wikibooks-Buch oder Wikisource-Werk**: Geben Sie die Adresse oder den Titel des Inhaltsverzeichnisses ein, zum Beispiel `https://fr.wikibooks.org/wiki/Cosmologie` oder `s:Les Misérables`. Ein Fenster fragt, was Sie möchten:
  - „Das ganze Buch“: alle seine Seiten, in Kapitel geordnet;
  - „Das ganze Buch mit seinem Inhaltsverzeichnis“: dasselbe, mit dem Inhaltsverzeichnis vorne;
  - „Nur diese Seite“: nur das Inhaltsverzeichnis;
  - „Abbrechen“: nichts wird hinzugefügt.
- **Druckversion von Wikibooks**: Geben Sie die Adresse der Seite „Druckversion“ des Buchs ein, zum Beispiel `https://fr.wikibooks.org/wiki/Programmation_C/Version_imprimable`. Ist diese Seite von Hand geschrieben, werden ihre Seiten mit einem Kapitel pro Überschrift hinzugefügt; wird sie aus dem Inhaltsverzeichnis erzeugt, öffnet sich das Auswahlfenster des Buchs.

## Mehrere Seiten auf einmal

Fügen Sie eine Liste ein, eine Seite pro Zeile (für eine neue Zeile beim Tippen Umschalt+Eingabe). Jede Zeile kann ein Titel, eine Adresse oder eine Seite mit Präfix sein und auch als Wiki-Link, Markdown-Link oder Element einer nummerierten oder Aufzählungsliste geschrieben werden:

```
[[Brest]]
[[nl:Amsterdam]]
[Suchet](https://fr.wikipedia.org/wiki/Suchet_(navire))
1. Lorient
* Concarneau
[[voy:en:Lyon]]
fr:wikt:chat
```

Eine Meldung am Ende sagt, wie viele Seiten hinzugefügt wurden, wie viele schon im Buch waren und wie viele nicht gefunden wurden. Nicht gefundene Zeilen bleiben im Feld, damit Sie sie korrigieren können. Ein Inhaltsverzeichnis in der Liste öffnet das oben beschriebene Auswahlfenster.

## Den Text einer Buchseite einfügen

Sie können den Inhalt einer Wikipedia-Seite „Buch:“ einfügen: `== … ==` ergibt den Titel, `=== … ===` den Untertitel, jede Zeile `;` beginnt ein Kapitel und jeder Link `[[…]]` fügt einen Artikel hinzu.

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

Der Text einer Wikibooks-Druckversion aus Einbindungen `{{:…}}` wird ebenso angenommen: Jede Überschrift `= … =` wird zu einem Kapitel.

## Ein gespeichertes oder geteiltes Buch öffnen

- Die Schaltfläche „Speichern“ lädt Ihr Buch in eine Datei herunter; die Schaltfläche „Öffnen“ lädt es später wieder. Auf dem Server wird nichts aufbewahrt: Diese Datei ist Ihre einzige Sicherung.
- Ein Link der Form `https://wikipedia2book.toolforge.org/?json=https://…` öffnet ein online gespeichertes Buch (nur Adressen mit `https://`).
- Ein Link der Form `https://wikipedia2book.toolforge.org/?source=…` fügt seine Quellen hinzu, als hätten Sie sie eingegeben: praktisch, um eine Auswahl von Seiten zu teilen.

## Was das Feld ablehnt

- Websites, die keine Wikimedia-Projekte sind;
- Seiten, die keine Inhaltsseiten sind (Diskussionen, Hilfe- oder Gemeinschaftsseiten);
- Dateien von Wikimedia Commons: Fügen Sie sie stattdessen im Schritt Organisation als Dokumente oder im Schritt Bearbeitung als Hintergrundbilder hinzu;
- Seiten, die nicht existieren.

Die Fehlermeldung erklärt, was nicht stimmt. Sie kommt vom Server und bleibt auf Französisch, unabhängig von der Sprache der Oberfläche.

## Und dann?

- **Organisation**: Seiten ordnen, Kapitel erstellen, eigene Bilder oder PDFs hinzufügen, das Buch in Bände teilen. Ab 300 Artikeln wird das Buch automatisch in Bände geteilt.
- **Bearbeitung**: Titel, Umschlag, Hintergrundbilder, Inhaltsverzeichnis, Format und Ränder.
- **PDF erstellen**: Jeder Artikel wird so übernommen, wie Wikipedia ihn druckt, und alles bildet ein einziges druckfertiges Buch.

<!-- {% endraw %} -->
