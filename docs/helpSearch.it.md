# Aiuto del campo «Costruisci il libro»: tutto ciò che Wikipedia2Book accetta

Questa pagina elenca tutto ciò che Wikipedia2Book accetta, con per ogni caso un esempio da provare **nel browser** e lo stesso caso **tramite l'API**. Serve a due cose: mostrare le possibilità e fare una verifica manuale prima di una pubblicazione. È una traduzione della [pagina di riferimento in francese](helpSearch.fr.md).

Il comportamento di riferimento è descritto nelle [specifiche funzionali](FunctionalSpec.en.md) (sezione 3.1 per le fonti) e nelle [specifiche tecniche](TechnicalSpec.en.md) (sezione 13.3 per l'API).

## Come usarla

- **Browser**: aprire https://wikipedia2book.toolforge.org/, incollare l'esempio nel campo del passo «Costruisci il libro» e cliccare su «Aggiungi». Un indirizzo che inizia con `https://wikipedia2book.toolforge.org/?` si apre direttamente.
- **API**: aprire l'indirizzo nel browser (il PDF viene scaricato) oppure passarlo a `curl -OJ`. Le chiamate `POST` sono indicate come comandi `curl`.
- **Versione**: versione dell'applicazione da cui il caso funziona. Quella in linea è indicata da https://wikipedia2book.toolforge.org/api/version.
- La colonna «Versione» vale per il browser. Lato API, `GET /api/pdf/from-source` (sezioni da 1 a 4) e il parametro `?source=` della pagina esistono dalla 1.12.0 (in produzione dalla sera del 16 novembre 2026, prima di ricevere questo numero): con una versione precedente, inviare il libro in JSON a `POST /api/pdf` (9.3) dopo aver riconosciuto ogni voce con `POST /api/sources/resolve` (9.1).
- Gli esempi sono stati verificati il 17 novembre 2026 con il codice di riconoscimento delle fonti contro i veri wiki; una pagina rinominata o cancellata nel frattempo può cambiare il risultato.

Abbreviazioni: **T** = https://wikipedia2book.toolforge.org. Negli indirizzi dell'API, `language` è la lingua dei titoli generati nel PDF (copertina, indice, licenza) e `wiki` la lingua dei titoli senza prefisso.

## 1. Una singola pagina

| N. | Caso | Browser: da inserire | API | Risultato atteso | Versione |
|---|---|---|---|---|---|
| 1.1 | URL di una voce di Wikipedia | `https://fr.wikipedia.org/wiki/Épaves_de_la_rade_de_Saint-Pierre` | `T/api/pdf/from-source?source=https://fr.wikipedia.org/wiki/%C3%89paves_de_la_rade_de_Saint-Pierre` | La voce viene aggiunta; introduzione e autore proposti alla prima voce | ≤ 1.9.7 |
| 1.2 | Titolo esatto | `Montagne Pelée` (lingua FR accanto al campo) | `T/api/pdf/from-source?source=Montagne%20Pel%C3%A9e&wiki=fr` | La voce «Montagne Pelée» viene aggiunta | ≤ 1.9.7 |
| 1.3 | Titolo reindirizzato | `Napoléon Bonaparte` | `T/api/pdf/from-source?source=Napol%C3%A9on%20Bonaparte&wiki=fr` | Il redirect viene seguito: si aggiunge «Napoléon Ier» | ≤ 1.9.7 |
| 1.4 | Titolo senza pagina esatta | `volcan martinique` | `T/api/sources/resolve` in `POST` (vedi 9.1): `kind` = `search` | I risultati della ricerca appaiono sotto il campo e si aggiungono con un clic; l'API di generazione risponde 404 con il testo in questione | ≤ 1.9.7 |
| 1.5 | Ricerca durante la digitazione | Digitare `Saint-Pie` senza confermare | `T/api/search?query=Saint-Pie&language=fr` | Suggerimenti sotto il campo | ≤ 1.9.7 |
| 1.6 | Titolo in un'altra lingua | `nl:Rotterdam` | `T/api/pdf/from-source?source=nl:Rotterdam` | Viene aggiunta la voce in olandese, contrassegnata «NL» | 1.7.0 |
| 1.7 | Tutte le lingue | `Paris`, con «Tutte» scelto accanto al campo | `T/api/search?query=Paris&language=all&limit=3` | Risultati in ogni lingua dell'elenco, ciascuno contrassegnato con la sua lingua; la voce scelta mantiene la propria | 1.12.4 |

## 2. Altri progetti Wikimedia

| N. | Caso | Browser: da inserire | API | Risultato atteso | Versione |
|---|---|---|---|---|---|
| 2.1 | Pagina di Wikivoyage | `https://fr.wikivoyage.org/wiki/Lyon` | `T/api/pdf/from-source?source=https://fr.wikivoyage.org/wiki/Lyon` | Pagina aggiunta, scheda contrassegnata «Wikivoyage» | 1.8.0 |
| 2.2 | Prefisso di progetto e di lingua | `[[voy:en:Lyon]]` | `T/api/pdf/from-source?source=voy:en:Lyon` | Aggiunta la pagina di Wikivoyage in inglese | 1.8.0 |
| 2.3 | Wikiversità | `https://fr.wikiversity.org/wiki/Python` | `T/api/pdf/from-source?source=v:Python&wiki=fr` | Pagina aggiunta, contrassegnata «Wikiversità» | 1.8.0 |
| 2.4 | Wikiquote | `https://fr.wikiquote.org/wiki/Victor_Hugo` | `T/api/pdf/from-source?source=q:Victor%20Hugo&wiki=fr` | Pagina aggiunta, contrassegnata «Wikiquote» | 1.8.0 |
| 2.5 | Wikizionario, prefissi in ordine inverso | `fr:wikt:chat` | `T/api/pdf/from-source?source=fr:wikt:chat` | Pagina aggiunta, contrassegnata «Wikizionario» | 1.8.0 |
| 2.6 | Wikinotizie | `https://fr.wikinews.org/wiki/Accueil` | `T/api/pdf/from-source?source=https://fr.wikinews.org/wiki/Accueil` | Pagina aggiunta, contrassegnata «Wikinotizie» | 1.8.0 |
| 2.7 | Testo di Wikisource (una pagina) | `https://zh.wikisource.org/wiki/論語/學而第一` | `T/api/pdf/from-source?source=https://zh.wikisource.org/wiki/%E8%AB%96%E8%AA%9E/%E5%AD%B8%E8%80%8C%E7%AC%AC%E4%B8%80` | Pagina aggiunta; titoli cinesi leggibili nel PDF | 1.7.8 |
| 2.8 | Pagina d'autore di Wikisource | `https://fr.wikisource.org/wiki/Auteur:François_Rabelais` | `T/api/pdf/from-source?source=https://fr.wikisource.org/wiki/Auteur:Fran%C3%A7ois_Rabelais` | Pagina aggiunta così com'è (biografia ed elenco delle opere) | 1.8.1 |

## 3. Libri

| N. | Caso | Browser: da inserire | API | Risultato atteso | Versione |
|---|---|---|---|---|---|
| 3.1 | Pagina di libro di Wikipedia per URL | `https://fr.wikipedia.org/wiki/Utilisateur:Alexbzh972/Livres/Martinique` | `T/api/books/generate-from-wikipedia-book?url=https://fr.wikipedia.org/wiki/Utilisateur:Alexbzh972/Livres/Martinique` | 113 voci nell'ordine della pagina, capitoli `;`, sottotitolo `===`; titolo «Martinique» | 1.3.0 |
| 3.2 | Pagina di libro per nome | `Utilisateur:Alexbzh972/Livres/Martinique` | `T/api/pdf/from-source?source=Utilisateur:Alexbzh972/Livres/Martinique` | Stesso risultato di 3.1 | 1.3.0 |
| 3.3 | Indice di un libro di Wikibooks | `https://fr.wikibooks.org/wiki/Cosmologie` | `T/api/pdf/from-source?source=b:Cosmologie&wiki=fr` | Finestra «L'intero libro / L'intero libro e il suo indice / Solo questa pagina / Annulla»; «L'intero libro» dà 27 pagine in capitoli | 1.10.0 |
| 3.4 | Libro intero con il suo indice | Come 3.3, scegliere «L'intero libro e il suo indice» | `T/api/pdf/from-source?source=b:Cosmologie&wiki=fr&summary=1` | L'indice per primo, prima del primo capitolo | 1.10.0 |
| 3.5 | Solo la pagina dell'indice | Come 3.3, scegliere «Solo questa pagina» | `POST /api/pdf` con la sola pagina dell'indice (vedi 9.3) | La pagina dell'indice da sola | 1.10.0 |
| 3.6 | Opera di Wikisource | `s:Les Misérables` (lingua FR) | `T/api/pdf/from-source?source=s:Les%20Mis%C3%A9rables&wiki=fr` | Finestra di scelta; «L'intero libro» dà 365 capitoli in 5 parti, senza «Texte entier» | 1.11.0 |
| 3.7 | Versione stampabile scritta a mano (indirizzo) | `https://fr.wikibooks.org/wiki/Hélices_de_navires_à_déplacement/Version_imprimable` | `T/api/pdf/from-source?source=https://fr.wikibooks.org/wiki/H%C3%A9lices_de_navires_%C3%A0_d%C3%A9placement/Version_imprimable` | 13 pagine, un capitolo per titolo `= … =`, copertina omessa, titolo «Hélices de navires à déplacement» | 1.12.0 |
| 3.8 | Versione stampabile tramite `{{imprimable}}` (indirizzo) | `https://fr.wikibooks.org/wiki/Programmation_C/Version_imprimable` | `T/api/pdf/from-source?source=https://fr.wikibooks.org/wiki/Programmation_C/Version_imprimable` | La finestra di scelta dell'indice «Programmation C» (21 pagine) | 1.12.0 |

## 4. Elenchi di pagine (più righe)

Incollare tutte le righe insieme nel campo (o separarle con Maiusc+Invio). Lato API, ripetere `source=` (al massimo 50).

| N. | Caso | Riga da inserire | Risultato atteso | Versione |
|---|---|---|---|---|
| 4.1 | Link wiki | `[[Brest]]` | «Brest» aggiunta | 1.7.0 |
| 4.2 | Link wiki con lingua | `[[nl:Amsterdam]]` | Voce in olandese aggiunta | 1.7.0 |
| 4.3 | Link wiki con testo | `[[Frégate (bateau)\|Frégate]]` | «Frégate (bateau)» aggiunta | 1.7.0 |
| 4.4 | Link Markdown, parentesi nell'URL | `[Suchet](https://fr.wikipedia.org/wiki/Suchet_(navire))` | «Suchet (navire)» aggiunta | 1.7.0 |
| 4.5 | Numero a inizio riga | `1. Lorient` | «Lorient» aggiunta | 1.7.0 |
| 4.6 | Punto elenco a inizio riga | `* Concarneau` (anche `-`, `•`, `#`) | «Concarneau» aggiunta | 1.7.0 |
| 4.7 | Riga non trovata | `Xyzzy inexistant` | La riga resta nel campo, il messaggio finale la conta come «non trovata» | 1.7.0 |
| 4.8 | Indice in un elenco | `b:Programmation Python` | Si apre la finestra di scelta per quell'indice; i suoi capitoli non vengono ripresi | 1.10.0 |

Elenco completo da incollare nel browser:

```
[[Brest]]
[[nl:Amsterdam]]
[Suchet](https://fr.wikipedia.org/wiki/Suchet_(navire))
1. Lorient
* Concarneau
[[voy:en:Lyon]]
fr:wikt:chat
```

Risultato atteso: «7 pagina/e aggiunta/e, 0 già nel libro, 0 non trovata/e.»

API, stesso elenco: `T/api/pdf/from-source?source=[[Brest]]&source=[[nl:Amsterdam]]&source=1.%20Lorient&source=*%20Concarneau&source=[[voy:en:Lyon]]&source=fr:wikt:chat&wiki=fr`

## 5. Testo di un libro incollato

| N. | Caso | Testo da incollare | API | Risultato atteso | Versione |
|---|---|---|---|---|---|
| 5.1 | Sintassi Wikipedia «Libro:» | Blocco 5.1 qui sotto | `curl` 5.1 qui sotto | Titolo «Ports bretons», sottotitolo «Guide des ports», capitoli «Finistère» e «Morbihan», «Brest» in testa senza capitolo | 1.12.0 |
| 5.2 | Versione stampabile di Wikibooks | Blocco 5.2 qui sotto | `curl` 5.2 qui sotto | 3 pagine di Wikibooks in 3 capitoli, licenza omessa | 1.12.0 |

Blocco 5.1:

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

Blocco 5.2:

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

Leggere solo la struttura, senza PDF: stesso contenuto verso `POST /api/books/from-wikitext`.

## 6. Aprire un libro salvato (JSON)

| N. | Caso | Browser | API | Risultato atteso | Versione |
|---|---|---|---|---|---|
| 6.1 | Libro JSON per indirizzo | `T/?json=https://gmoulard.github.io/wikipedia2book/static/Wrecks-of-Saint-Pierre-harbor.json` | `T/api/pdf/from-json?url=https://gmoulard.github.io/wikipedia2book/static/Wrecks-of-Saint-Pierre-harbor.json&language=en` | Il libro si apre («Libro importato.») con le sue immagini di sfondo e il suo documento | 1.9.6 |
| 6.2 | Libro di Wikibooks in JSON | `T/?json=https://gmoulard.github.io/wikipedia2book/static/Cosmologie.json` | `T/api/pdf/from-json?url=https://gmoulard.github.io/wikipedia2book/static/Cosmologie.json` | 27 pagine in 8 capitoli | 1.9.6 |
| 6.3 | File JSON locale | Pulsante «Apri», scegliere un file esportato con «Salva» | `curl -OJ -X POST 'T/api/pdf/from-json' -H 'Content-Type: application/json' --data @libro.json` | Il libro si apre / il PDF viene generato | ≤ 1.9.7 (browser), 1.12.0 (API) |
| 6.4 | JSON, poi altre fonti | `T/?json=https://gmoulard.github.io/wikipedia2book/static/Cosmologie.json&source=b:Programmation%20Python` | — | Si apre il libro JSON, poi la finestra di scelta per l'indice aggiunto | 1.12.0 |
| 6.5 | Fonti nell'indirizzo della pagina | `T/?source=https://fr.wikibooks.org/wiki/Cosmologie&source=Montagne%20Pel%C3%A9e&wiki=fr` | Vedi 3.3 e 1.2 | Ogni fonte viene aggiunta come se fosse stata digitata, domanda compresa | 1.12.0 |
| 6.6 | Indirizzo rifiutato | `T/?json=http://example.com/livre.json` | `T/api/pdf/from-json?url=http://example.com/livre.json` | Messaggio d'errore, nulla viene importato; l'API risponde 422 «doit commencer par https://» | 1.9.6 |

## 7. Documenti e immagini di sfondo

| N. | Caso | Browser | API (campo del libro JSON) | Risultato atteso | Versione |
|---|---|---|---|---|---|
| 7.1 | Immagine o PDF dal computer | Passo Organizzazione, «Scegli un file +» | `uploaded_documents[]` con `data_base64` | Documento collocato nel libro come una voce, 15 MB al massimo | ≤ 1.9.7 |
| 7.2 | Documento per indirizzo | Passo Organizzazione, campo indirizzo: `https://upload.wikimedia.org/wikipedia/commons/1/16/La_Pel%C3%A9e_vue_du_Carbet.jpg` | `uploaded_documents[]` con `"url": "https://upload.wikimedia.org/…"` | Viene salvato solo l'indirizzo; il server scarica l'immagine a ogni generazione | 1.10.0 |
| 7.3 | Documento per pagina di file di Commons | `https://commons.wikimedia.org/wiki/File:La_Pelée_vue_du_Carbet.jpg` | `"url": "https://commons.wikimedia.org/wiki/File:La_Pel%C3%A9e_vue_du_Carbet.jpg"` | Si usa l'immagine (anteprima a 2 000 px); per un PDF, l'originale | 1.10.0 (browser), 1.12.0 (API) |
| 7.4 | PDF per pagina di file | `https://commons.wikimedia.org/wiki/File:Interpersonal_communication_and_coordination_in_Wikipedia_Working_Paper_30_June_2020.pdf` | Stesso indirizzo in `uploaded_documents[].url` | Il PDF originale viene inserito, pagine adattate al formato del libro | 1.10.0 (browser), 1.12.0 (API) |
| 7.5 | Immagine di sfondo della copertina | Passo Modifica, «Immagine di sfondo della copertina», file o indirizzo (7.2 o 7.3) | `cover_image`: `{"title": "…", "url": "…"}` oppure `data_base64` | Sfondo della copertina, senza deformazione | 1.9.6 |
| 7.6 | Immagine dell'ultima pagina | Passo Modifica, «Immagine di sfondo dell'ultima pagina» | `back_image` | Pagina a sé dopo la licenza | 1.9.6 |
| 7.7 | Indirizzo irraggiungibile | Documento `https://example.org/inexistant.png` | Stesso indirizzo | Generazione interrotta, viene indicato l'indirizzo in questione; 502 tramite l'API | 1.10.0 |

## 8. Organizzazione e impaginazione

| N. | Caso | Browser | API (libro JSON verso `POST /api/pdf`) | Risultato atteso | Versione |
|---|---|---|---|---|---|
| 8.1 | Voci collegate | Pulsante «Voci collegate» di una voce | `POST /api/explore` | Link della voce proposti, nell'ordine della pagina | ≤ 1.9.7 |
| 8.2 | Capitoli e ordine | Passo Organizzazione, «Crea un capitolo», trascinamento | `chapters`, `article_order`, `unassigned_first` | Il PDF segue l'ordine visualizzato | ≤ 1.9.7 |
| 8.3 | Indice | Passo Modifica: nessuno, inizio, fine | `table_of_contents`, `toc_position` (`start`, `end`, `before:<chiave>`) | Indice al posto giusto, link cliccabili | 1.9.6 |
| 8.4 | Formato, orientamento, margini | Passo Modifica | `page_format`, `orientation`, `margin_*_mm`, `custom_width_mm` | Tutte le pagine nel formato scelto | ≤ 1.9.7 |
| 8.5 | Numeri di pagina | «Numera le pagine» | `page_numbers` | Numeri in fondo alla pagina, tranne sulla copertina | ≤ 1.9.7 |
| 8.6 | Lingua dei titoli del PDF | Selettore di lingua in alto | Parametro `language` (12 lingue) | Copertina, indice, licenza nella lingua scelta | ≤ 1.9.7 |
| 8.7 | Divisione manuale in volumi | Passo Organizzazione, «Nuovo volume» | `volume_breaks`: `["before:<chiave>"]`, poi `?volume=N` | Un PDF per volume, numerazione che riparte da 1 | 1.9.2 (browser), 1.12.0 (API) |
| 8.8 | Più di 300 voci | Libro 3.1 + altre pagine fino a superare 300 | `POST /api/books/volumes` per il piano, poi `POST /api/pdf?volume=1`, `?volume=2`… | Divisione automatica tra capitoli, «Volume 1/2»…; senza `volume`, rifiuto 413 con il numero di volumi | 1.9.0 (browser), 1.12.0 (API) |

## 9. Chiamate API senza PDF

| N. | Caso | Chiamata | Risultato atteso |
|---|---|---|---|
| 9.1 | Riconoscere una voce | `curl -X POST 'T/api/sources/resolve' -H 'Content-Type: application/json' --data '{"input":"volcan martinique","language":"fr"}'` | `kind`: `article`, `book`, `subpages` o `search` |
| 9.2 | Struttura di una pagina di libro | `curl -X POST 'T/api/books/structure' -H 'Content-Type: application/json' --data '{"url":"https://fr.wikipedia.org/wiki/Utilisateur:Alexbzh972/Livres/Martinique"}'` | Voci, sottotitolo, capitoli |
| 9.3 | PDF di un libro descritto in JSON | `curl -OJ -X POST 'T/api/pdf?language=fr' -H 'Content-Type: application/json' --data '{"name":"Test","main_articles":[{"title":"Cosmologie","language":"fr","site":"wikibooks","url":"https://fr.wikibooks.org/wiki/Cosmologie","selected":true}]}'` | PDF di una sola pagina di indice |
| 9.4 | Seguire la generazione | Stesso contenuto verso `POST /api/pdf/stream` | Righe NDJSON `progress`, `wait`, poi `done` e il PDF |
| 9.5 | Introduzione e autore proposti | `T/api/articles/intro?title=Montagne%20Pel%C3%A9e&language=fr` | Primo paragrafo e creatore della pagina |
| 9.6 | Versione in linea | `T/api/version` | Versione, commit, limite di voci |

## 10. Voci rifiutate

I messaggi d'errore vengono dal server e restano in francese, qualunque sia la lingua dell'interfaccia.

| N. | Voce | Risultato atteso |
|---|---|---|
| 10.1 | `https://example.com/wiki/Chat` | «L'URL doit pointer vers une page HTTPS d'un projet Wikimédia…»; 422 |
| 10.2 | `https://fr.wikibooks.org/wiki/Wikilivres:Le_Bistro` | «Seules les pages de contenu de fr.wikibooks.org…»; 422 |
| 10.3 | `https://commons.wikimedia.org/wiki/File:La_Pelée_vue_du_Carbet.jpg` nel campo Fonti | Rifiutato come fonte (Commons non ha indirizzi `<lingua>.<progetto>.org`); accettato come documento o immagine di sfondo (7.3) |
| 10.4 | `https://fr.wikipedia.org/wiki/Page_qui_n_existe_pas` | «La page … est introuvable»; 404 |
| 10.5 | Campo vuoto | «Saisissez …»; 422 |
| 10.6 | Libro senza voci selezionate, poi «Genera il PDF» | Messaggio «Seleziona almeno un articolo prima di generare il PDF.»; 400 |
