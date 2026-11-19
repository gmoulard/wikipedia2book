# Aiuto: cosa si può inserire nel campo «Costruisci il libro»?

<!-- {% raw %} -->

Il campo del primo passo accetta molto più di un titolo di voce: un indirizzo, un libro intero, un elenco di pagine o il testo di una pagina di libro. Digita o incolla ciò che vuoi aggiungere, poi clicca su «Aggiungi». Le pagine aggiunte compaiono sotto il campo; le ordinerai nel passo successivo.

## In breve

| Vuoi aggiungere… | Inserisci… | Esempio |
|---|---|---|
| una voce di cui conosci il titolo | il suo titolo | `Montagne Pelée` |
| una pagina precisa | il suo indirizzo | `https://fr.wikipedia.org/wiki/Épaves_de_la_rade_de_Saint-Pierre` |
| una voce in un'altra lingua | il codice della lingua, due punti, il titolo | `nl:Rotterdam` |
| una pagina di un altro progetto Wikimedia | il prefisso del progetto, poi il titolo | `voy:en:Lyon` |
| un libro intero | l'indirizzo del suo indice o della sua pagina di libro | `https://fr.wikibooks.org/wiki/Cosmologie` |
| più pagine insieme | una pagina per riga | vedi «Più pagine insieme» |
| un libro preparato su una pagina «Libro:» | il testo di quella pagina | vedi «Incollare il testo di una pagina di libro» |

## Cercare una voce

- Digita qualche lettera: sotto il campo compaiono dei suggerimenti.
- L'elenco accanto al campo sceglie in quale lingua di Wikipedia cercare. Con «Tutte», il titolo viene cercato in tutte le lingue dell'elenco e ogni risultato indica la sua lingua.
- Se il titolo corrisponde esattamente a una voce, questa viene aggiunta subito. Un titolo che rimanda a un'altra voce aggiunge la voce di destinazione: `Napoléon Bonaparte` aggiunge «Napoléon Ier».
- Altrimenti, i risultati della ricerca compaiono sotto il campo: clicca su quello che vuoi.
- Per la prima voce aggiunta, la sua introduzione e il creatore della pagina sono proposti come introduzione e autore del libro, nel passo Modifica. Puoi cambiarli.

## Pagine in un'altra lingua o di un altro progetto

Un indirizzo completo funziona sempre, per esempio `https://fr.wikivoyage.org/wiki/Lyon`. Con un titolo, metti davanti un prefisso di lingua, di progetto o entrambi:

| Progetto | Prefisso | Esempio |
|---|---|---|
| Wikipedia in un'altra lingua | codice della lingua | `nl:Rotterdam` |
| Wikisource | `s:` | `s:Les Misérables` |
| Wikibooks | `b:` | `b:Cosmologie` |
| Wikivoyage | `voy:` | `voy:en:Lyon` |
| Wikiversità | `v:` | `v:Python` |
| Wikiquote | `q:` | `q:Victor Hugo` |
| Wikizionario | `wikt:` | `fr:wikt:chat` |
| Wikinotizie | `n:` | `n:Accueil` |

Senza codice di lingua vale la lingua scelta accanto al campo. L'ordine dei prefissi non conta. Ogni pagina mantiene sulla sua scheda il nome del suo progetto e la sua lingua.

## Libri interi

- **Pagina di libro di Wikipedia**: inserisci il suo indirizzo o il suo nome, per esempio `Utilisateur:Alexbzh972/Livres/Martinique`. Tutte le sue voci vengono aggiunte nell'ordine della pagina, con capitoli, titolo e sottotitolo.
- **Raccolta di Wikibooks**: inserisci l'indirizzo della raccolta, per esempio `https://fr.wikibooks.org/wiki/Wikilivres:Compilations/Programmation_C`. Le sue pagine vengono aggiunte nell'ordine dell'elenco, come per una pagina di libro di Wikipedia.
- **Libro di Wikibooks od opera di Wikisource**: inserisci l'indirizzo o il titolo del suo indice, per esempio `https://fr.wikibooks.org/wiki/Cosmologie` o `s:Les Misérables`. Una finestra ti chiede cosa vuoi:
  - «L'intero libro»: tutte le sue pagine, ordinate in capitoli;
  - «L'intero libro e il suo indice»: lo stesso, con la pagina dell'indice in testa;
  - «Solo questa pagina»: solo l'indice;
  - «Annulla»: non viene aggiunto nulla.
- **Versione stampabile di Wikibooks**: inserisci l'indirizzo della pagina «versione stampabile» del libro, per esempio `https://fr.wikibooks.org/wiki/Programmation_C/Version_imprimable`. Se quella pagina è scritta a mano, le sue pagine vengono aggiunte con un capitolo per titolo; se è generata dall'indice, si apre la finestra di scelta del libro.

## Più pagine insieme

Incolla un elenco, una pagina per riga (per andare a capo mentre scrivi, usa Maiusc+Invio). Ogni riga può essere un titolo, un indirizzo o una pagina con prefisso, e può anche essere scritta come link wiki, link Markdown o voce di un elenco numerato o puntato:

```
[[Brest]]
[[nl:Amsterdam]]
[Suchet](https://fr.wikipedia.org/wiki/Suchet_(navire))
1. Lorient
* Concarneau
[[voy:en:Lyon]]
fr:wikt:chat
```

Alla fine un messaggio indica quante pagine sono state aggiunte, quante erano già nel libro e quante non sono state trovate. Le righe non trovate restano nel campo, così puoi correggerle. Un indice di libro nell'elenco apre la finestra di scelta descritta sopra.

## Incollare il testo di una pagina di libro

Puoi incollare il contenuto di una pagina «Libro:» di Wikipedia: `== … ==` dà il titolo, `=== … ===` il sottotitolo, ogni riga `;` apre un capitolo e ogni link `[[…]]` aggiunge una voce.

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

Il testo di una versione stampabile di Wikibooks, fatto di inclusioni `{{:…}}`, è accettato allo stesso modo: ogni titolo `= … =` diventa un capitolo.

## Aprire un libro salvato o condiviso

- Il pulsante «Salva» scarica il tuo libro in un file; il pulsante «Apri» lo ricarica in seguito. Sul server non resta nulla: quel file è la tua unica copia.
- Un link della forma `https://wikipedia2book.toolforge.org/?json=https://…` apre un libro salvato online (solo indirizzi `https://`).
- Un link della forma `https://wikipedia2book.toolforge.org/?source=…` aggiunge le sue fonti come se le avessi digitate: comodo per condividere una selezione di pagine.

## Cosa il campo rifiuta

- i siti che non sono progetti Wikimedia;
- le pagine che non sono pagine di contenuto (discussioni, pagine di aiuto o della comunità);
- i file di Wikimedia Commons: aggiungili invece come documenti nel passo Organizzazione, o come immagini di sfondo nel passo Modifica;
- le pagine che non esistono.

Il messaggio d'errore spiega cosa non va. Viene dal server e resta in francese, qualunque sia la lingua dell'interfaccia.

## E poi?

- **Organizzazione**: ordina le pagine, crea capitoli, aggiungi immagini o PDF tuoi, dividi il libro in volumi. Oltre 300 voci, il libro viene diviso in volumi automaticamente.
- **Modifica**: titolo, copertina, immagini di sfondo, indice, formato e margini.
- **Genera il PDF**: ogni voce viene ripresa così come Wikipedia la stampa, e il tutto forma un unico libro pronto da stampare.

<!-- {% endraw %} -->
