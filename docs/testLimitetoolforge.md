# Test aux limites sur Toolforge

Taille maximale d'un livre que l'instance Toolforge (`https://wikipedia2book.toolforge.org`) sait générer, version par version. Procédure, script et précautions : section 13.12 des [spécifications](SPECIFICATIONS.fr.md).

Réglages communs à toutes les mesures : `scripts/limit_check.py`, pages liées depuis l'article *France* en français (pages existantes, par ordre alphabétique), format A4, numérotation et table des matières, génération depuis un poste client par `POST /api/pdf/stream`. Un échec signifie que le flux s'est interrompu pendant la génération : le serveur a redémarré.

## Synthèse

| Version | Limite constatée | Premier palier en échec |
|---------|------------------|-------------------------|
| 1.7.5   | 100 articles     | 150                     |
| 1.7.7   | 200 articles     | 300                     |
| 1.7.9   | non mesurée en dessous de 300 | 300        |
| 1.7.10  | 100 articles     | 150                     |
| 1.8.0   | 100 articles     | 150                     |
| 1.8.2   | 100 articles     | 150                     |
| 1.8.3   | 150 articles     | 200                     |
| 1.8.5   | au moins 150 articles | test arrêté avant 200 |
| 1.8.6   | 800 articles     | 1 000 (erreur sans redémarrage) |
| 1.8.9   | au moins 1 000 articles | aucun échec (900 et 1 000 réussis) |

## Version 1.8.9, 1 000 articles (16/11/2026, 09:42 UTC)

Deuxième palier sur la 1.8.9, lancé dès la fin de celui de 900 articles, avec `--save-pdf ./tmp` (le PDF reçu est gardé dans `./tmp/limite-1000-articles.pdf`, ignoré par git). Même serveur, toujours démarré à 08:40:01 UTC. Les 1 000 premiers liens de l'article *France* contiennent les deux titres de même clé, « France Info » (n° 900) et « France info » (n° 907) : ce palier met à l'épreuve le correctif de la 1.8.9.

### Résultat

| Articles | Pages  | Taille du PDF | Wikipédia | Application | Transfert | Total     | Résultat |
|----------|--------|---------------|-----------|-------------|-----------|-----------|----------|
| 1 000    | 17 518 | 949,2 Mo      | 1 104,6 s | 986,9 s     | 2 061,8 s | 4 153,3 s | réussi   |

Aucun redémarrage du serveur : 403 relevés de `GET /api/health/details`, de 09:42:24 à 10:52:06 UTC, sans interruption de plus de 30 s, tous avec l'heure de démarrage 08:40:01 UTC. **Le correctif des parties en double fonctionne** : la fusion des 1 021 parties passe sans `FileNotFoundError`, contrairement à la 1.8.6.

### Journal de la génération

Génération n° 6 (`GET /api/health/generations`), en Mo, mêmes colonnes que pour 900 articles :

| Temps     | Étape                 | Processus  | Assemblage (pic) | Serveur | Conteneur | Détail |
|-----------|-----------------------|------------|------------------|---------|-----------|--------|
| 0,0 s     | `start`               | serveur    | —                | 304     | 373       | 1 000 articles, A4 portrait, numérotation et table des matières, français |
| 1 103,5 s | `downloads_done`      | serveur    | —                | 346     | 1 436     | 17 403 pages d'articles |
| 1 103,6 s | `assembly_start`      | assemblage | 89               | 346     | 1 447     | |
| 1 103,7 s | `render_cover`        | assemblage | 102              | 346     | 1 459     | |
| 1 107,2 s | `render_toc_count`    | assemblage | 119 (120)        | 346     | 1 504     | 10 blocs, 30 pages de table des matières |
| 1 112,3 s | `render_toc`          | assemblage | 123 (124)        | 346     | 1 508     | 10 blocs |
| 1 113,4 s | `render_chapters`     | assemblage | 125              | 346     | 1 510     | aucun chapitre |
| 1 155,9 s | `render_license`      | assemblage | 174              | 346     | 1 559     | 10 blocs |
| 1 388,9 s | `merge_parts`         | assemblage | 321 (389)        | 346     | 1 610     | 1 021 parties, 17 518 pages |
| 1 389,0 s | `merge_reopen`        | assemblage | 321 (389)        | 346     | 1 609     | |
| 1 444,1 s | `outline_and_links`   | assemblage | 384 (389)        | 346     | 1 673     | |
| 2 071,7 s | `stamp_page_numbers`  | assemblage | 1 504            | 346     | 2 048     | |
| 2 089,2 s | `save`                | assemblage | 1 530            | 346     | 2 048     | 949 212 479 octets |
| 4 149,7 s | fin (`done`)          |            |                  |         |           | durée côté serveur |

Durée de chaque étape de l'assemblage : pages générées 52 s ; fusion des 1 021 parties 233 s ; signets et liens 55 s ; **numérotation des 17 518 pages 628 s** ; écriture 18 s.

### Mémoire du conteneur

| Heure (UTC) | Générations | Conteneur | Serveur | Fichiers | Phase |
|-------------|-------------|-----------|---------|----------|-------|
| 09:42:24    | 0           | 373       | 304     | 0        | avant le palier (cache du livre de 900 articles) |
| 09:50:04    | 1           | 851       | 328     | 437      | téléchargements |
| 10:00:02    | 1           | 1 387     | 340     | 943      | téléchargements |
| 10:03:09    | 1           | 2 048     | 346     | 1 453    | fin des téléchargements, fusion |
| 10:05:02    | 1           | 2 048     | 346     | 1 808    | fusion |
| 10:07:07    | 1           | 1 836     | 346     | 904      | fusion terminée, parties supprimées |
| 10:15:06    | 1           | 2 048     | 346     | 904      | numérotation |
| 10:20:06    | 1           | 652       | 346     | 1 809    | PDF écrit, processus d'assemblage terminé, envoi |
| 10:35:07    | 1           | 1 052     | 346     | 1 809    | envoi |
| 10:50:02    | 1           | 1 419     | 347     | 1 809    | fin de l'envoi |

- Conteneur à 100 % dans 65 relevés, de 10:02:59 à 10:17:20 UTC (fusion puis numérotation, 14 minutes), sans être arrêté.
- Fichiers temporaires au plus haut : 1 873 Mo ; mémoire du serveur au plus haut : 357 Mo.

### Générations simultanées

Une seule génération en cours dans 399 relevés, aucune dans 4 : aucun autre livre n'a été généré pendant ce palier, au plus 1 génération à la fois.

### PDF obtenu

Vérifié avec PyMuPDF sur `./tmp/limite-1000-articles.pdf` : 17 518 pages, dernier numéro de page « 17518 » ; 1 003 signets (livre, table des matières, 1 000 articles, licence) ; « France Info » en page 15 572 et « France info » en page 15 729 ; 4 014 liens internes dans les 30 pages de table des matières, aucun lien provisoire restant. Les deux entrées « France Info » de la table des matières pointent vers la même page, la première : elles partagent la clé d'article, d'où 999 pages visées pour 1 000 entrées.

### Comparaison

| Étape (assemblage, Mo) | 800 (1.8.6) | 900 (1.8.9) | 1 000 (1.8.9) |
|------------------------|-------------|-------------|---------------|
| fusion des parties     | 283         | 325         | 321 (pic 389) |
| numérotation           | 1 295 (428 s) | 1 390 (565 s) | 1 504 (628 s) |
| écriture               | 1 316       | 1 415       | 1 530         |
| pic du conteneur       | 2 048       | 2 048       | 2 048         |
| total côté client      | 3 468,8 s   | 3 608,6 s   | 4 153,3 s     |

**Conclusion** : 1 000 articles passent (17 518 pages, 949 Mo de PDF, 69 minutes), sans redémarrage, seul sur le serveur. Le processus d'assemblage culmine à 1,5 Go pendant la numérotation, et le conteneur reste à sa limite pendant 14 minutes : la marge est mince, et un autre gros livre généré en même temps la ferait dépasser. Pour la numérotation, environ 0,086 Mo par page.

## Version 1.8.9 (16/11/2026, 08:41 UTC)

Correctif des parties en double (deux titres de même clé d'article supprimaient deux fois la même partie, cause de l'échec à 1 000 articles en 1.8.6) et limite de Toolforge relevée de 300 à 2 000 articles par livre. Un seul palier, 900 articles, lancé 64 s après le démarrage du serveur (08:40:01 UTC, redémarrage du déploiement de la 1.8.9). Suivi par `GET /api/health/generations` (journal enregistré toutes les 15 s) et `GET /api/health/details` (348 relevés, toutes les 10 s, de 08:41:01 à 09:41:24 UTC).

Les 900 premiers liens de l'article *France* (n° 0 à 899) ne contiennent pas les deux titres de même clé, « France Info » et « France info », qui sont les liens n° 900 et 907 : ce palier ne met pas encore le correctif à l'épreuve, celui de 1 000 articles si.

### Résultat

| Articles | Pages  | Taille du PDF | Wikipédia | Application | Transfert | Total     | Résultat |
|----------|--------|---------------|-----------|-------------|-----------|-----------|----------|
| 900      | 15 641 | 855,8 Mo      | 1 021,2 s | 897,5 s     | 1 689,9 s | 3 608,6 s | réussi   |

Aucun redémarrage du serveur pendant tout le test : l'heure de démarrage reste 08:40:01 UTC dans les 348 relevés. Une seule requête de surveillance a échoué (09:48:49, heure du poste, délai de connexion TLS dépassé), suivie d'une réponse normale 13 s plus tard : incident réseau passager, sans redémarrage.

### Journal de la génération

Étapes de la génération n° 1 (`GET /api/health/generations`). *Assemblage* : mémoire (RSS) du processus d'assemblage ; *serveur* : mémoire du serveur ; *conteneur* : mémoire totale du conteneur, cache des fichiers compris (limite 2 048 Mo). En Mo.

| Temps    | Étape                 | Processus  | Assemblage (pic) | Serveur | Conteneur | Détail |
|----------|-----------------------|------------|------------------|---------|-----------|--------|
| 0,0 s    | `start`               | serveur    | —                | 124     | 96        | 900 articles, A4 portrait, numérotation et table des matières, français |
| 1 018,8 s | `downloads_done`     | serveur    | —                | 310     | 1 188     | 15 540 pages d'articles |
| 1 020,2 s | `assembly_start`     | assemblage | 89               | 311     | 1 286     | |
| 1 020,4 s | `render_cover`       | assemblage | 100              | 311     | 1 296     | |
| 1 023,4 s | `render_toc_count`   | assemblage | 119              | 310     | 1 332     | 9 blocs, 27 pages de table des matières |
| 1 027,9 s | `render_toc`         | assemblage | 123              | 310     | 1 333     | 9 blocs |
| 1 029,0 s | `render_chapters`    | assemblage | 124              | 310     | 1 332     | aucun chapitre |
| 1 067,0 s | `render_license`     | assemblage | 173              | 310     | 1 369     | 9 blocs |
| 1 291,6 s | `merge_parts`        | assemblage | 325 (345)        | 308     | 1 482     | 919 parties, 15 641 pages |
| 1 291,6 s | `merge_reopen`       | assemblage | 325 (345)        | 308     | 1 481     | |
| 1 336,6 s | `outline_and_links`  | assemblage | 358              | 308     | 1 514     | |
| 1 901,4 s | `stamp_page_numbers` | assemblage | 1 390            | 308     | 2 048     | |
| 1 916,3 s | `save`               | assemblage | 1 415            | 308     | 2 048     | 855 777 235 octets |
| 3 605,4 s | fin (`done`)         |            |                  |         |           | durée côté serveur |

Durée de chaque étape de l'assemblage : pages générées (couverture, table des matières en 2 rendus de 9 blocs, licence en 9 blocs) 47 s ; fusion des 919 parties 225 s ; signets et liens de la table des matières 45 s ; **numérotation des 15 641 pages 565 s** ; écriture 15 s.

### Mémoire du conteneur

Relevés de `GET /api/health/details` aux moments clés (Mo ; *fichiers* = dossier temporaire de la génération) :

| Heure (UTC) | Générations | Conteneur | Serveur | Fichiers | Phase |
|-------------|-------------|-----------|---------|----------|-------|
| 08:41:01    | 0           | 95        | 123     | 0        | avant le test |
| 08:45:00    | 1           | 453       | 267     | 205      | téléchargements |
| 08:50:06    | 1           | 784       | 289     | 502      | téléchargements |
| 08:55:07    | 1           | 1 046     | 296     | 755      | téléchargements |
| 09:00:00    | 1           | 1 802     | 308     | 1 270    | fin des téléchargements |
| 09:02:03    | 1           | 2 048     | 308     | 1 612    | fusion |
| 09:03:08    | 1           | 1 512     | 308     | 814      | fusion terminée, parties supprimées |
| 09:10:01    | 1           | 2 048     | 308     | 814      | numérotation |
| 09:15:03    | 1           | 729       | 308     | 1 630    | PDF écrit, processus d'assemblage terminé, envoi |
| 09:30:00    | 2           | 1 229     | 308     | 1 677    | envoi, plus une autre génération |
| 09:40:09    | 1           | 1 421     | 308     | 1 630    | fin de l'envoi |

- Le conteneur a été à 100 % de sa mémoire dans 47 relevés, de 09:01:12 à 09:13:00 UTC (fusion puis numérotation), sans être arrêté : une partie de cette mémoire est du cache de fichiers, que le système reprend.
- Fichiers temporaires au plus haut : 1 692 Mo (parties de 900 articles, puis fichier fusionné et PDF final).
- Mémoire du serveur au plus haut : 311 Mo ; elle reste stable pendant tout l'assemblage, qui tourne dans son propre processus.
- Pendant l'envoi, la mémoire du conteneur remonte de 729 à 1 421 Mo : c'est le cache du PDF final (816 Mio) lu pour l'envoi.

### Générations simultanées

Nombre de générations en cours dans les 348 relevés : 0 dans 3 relevés, 1 dans 310, 2 dans 35 (au plus 2 à la fois, de 09:28:17 à 09:37:44 UTC). Quatre autres livres ont été générés pendant l'envoi du nôtre, tous en allemand, A4, avec numérotation et table des matières :

| Génération | Début (UTC) | Articles | Durée côté serveur | Taille | Résultat |
|------------|-------------|----------|--------------------|--------|----------|
| n° 2       | 09:28:14    | 133      | 188,5 s            | 23,5 Mio | réussi |
| n° 3       | 09:31:54    | 5        | 7,8 s              | 1,4 Mio  | réussi |
| n° 4       | 09:33:38    | 70       | 61,0 s             | 13,5 Mio | réussi |
| n° 5       | 09:36:08    | 107      | 95,9 s             | 19,2 Mio | réussi |

Aucune n'a chevauché l'assemblage du livre de 900 articles, terminé avant 09:15 UTC.

### Comparaison avec la 1.8.6

| Étape (assemblage, Mo)  | 800 articles (1.8.6) | 900 articles (1.8.9) |
|-------------------------|----------------------|----------------------|
| fusion des parties      | 283                  | 325                  |
| numérotation            | 1 295 (428 s)        | 1 390 (565 s)        |
| écriture                | 1 316                | 1 415                |
| pic du conteneur        | 2 048                | 2 048                |
| total côté client       | 3 468,8 s            | 3 608,6 s            |

**Conclusion** : 900 articles passent (15 641 pages, 856 Mo de PDF, une heure de bout en bout), sans redémarrage, avec au plus 2 générations simultanées. La numérotation reste l'étape la plus lourde : environ 0,09 Mo par page et 9 minutes et demie à 900 articles. Le conteneur travaille à sa limite de mémoire pendant 12 minutes : 1 000 articles sont au bord de la limite, et un autre gros livre en même temps la dépasserait.

## Version 1.8.6 (16/11/2026, 04:35 UTC)

Assemblage par PyMuPDF : fusion par lots de 20 en mise à jour incrémentale, signets, liens, numéros par `insert_text`, écriture. Test en deux temps (paliers 100 à 600, puis 800 à 1 500), suivi par `GET /api/health/generations` et `GET /api/health/details`. Le serveur n'a redémarré à aucun moment (démarré à 04:34:06 UTC). Pendant le test, d'autres utilisateurs ont généré des livres (7 générations de 12 à 200 articles) : la mémoire du conteneur additionne leurs livres et les nôtres.

| Articles | Pages  | Taille du PDF | Wikipédia | Application | Transfert  | Total      | Résultat |
|----------|--------|---------------|-----------|-------------|------------|------------|----------|
| 100      | 1 637  | 93,2 Mo       | 127,5 s   | 25,4 s      | 58,8 s     | 211,8 s    | réussi   |
| 200      | 3 435  | 195,7 Mo      | 215,6 s   | 62,1 s      | 365,4 s    | 643,0 s    | réussi   |
| 300      | 5 119  | 290,0 Mo      | 264,0 s   | 117,3 s     | 570,4 s    | 951,8 s    | réussi   |
| 400      | 7 305  | 420,6 Mo      | 246,5 s   | 216,0 s     | 960,2 s    | 1 422,7 s  | réussi   |
| 600      | 10 629 | 603,6 Mo      | 663,4 s   | 425,0 s     | 1 323,2 s  | 2 411,6 s  | réussi   |
| 800      | 14 092 | 778,6 Mo      | 886,0 s   | 670,7 s     | 1 912,1 s  | 3 468,8 s  | réussi   |
| 1 000    | —      | —             | —         | —           | —          | 1 403,8 s  | échec    |

Journal de l'assemblage, mémoire du processus d'assemblage (RSS), en Mo :

| Étape                 | 100 | 300 | 400 | 600   | 800   |
|-----------------------|-----|-----|-----|-------|-------|
| page de licence       | 160 | 162 | 169 | 173   | 173   |
| fusion des parties    | 222 | 231 | 253 | 264   | 283   |
| numérotation          | 292 | 551 | 719 | 1 010 | 1 295 |
| écriture              | 292 | 559 | 730 | 1 022 | 1 316 |
| pic du conteneur      | 740 | 1 448 | 1 936 | 2 048 | 2 048 |

**Limite : environ 800 articles (14 000 pages, 780 Mo de PDF), contre 150 en 1.8.5.** La fusion par PyMuPDF ne coûte presque plus rien (283 Mo à 800 articles, contre plus de 1 Go à 100 articles avec qpdf). Le nouveau poste est la numérotation : `insert_text` garde chaque page modifiée en mémoire (environ 0,09 Mo par page) et prend 7 minutes à 800 articles. Le conteneur touche sa limite de 2 Gio dès 600 articles sans être arrêté, une partie étant du cache de fichiers récupérable.

À 1 000 articles, la génération échoue avec un message d'erreur, sans redémarrage du serveur : `FileNotFoundError` juste après la fusion, avant l'étape `merge_parts` du journal. Cause probable : une même partie figure deux fois dans la liste à fusionner (deux titres de même clé d'article), et la suppression des fichiers des parties après la fusion échoue sur la seconde. À corriger ; la numérotation aurait de toute façon dépassé la mémoire (1 806 Mo pour le conteneur dès la page de licence).

Pistes suivantes : numéroter les pages pendant la fusion, lot par lot, pour libérer la mémoire tous les 20 articles ; corriger la double suppression des parties.

## Mesures locales de l'assemblage (16/11/2026)

Pour comprendre le pic de la fusion vu sur Toolforge en 1.8.5, mesure sur ce poste (Windows, pikepdf 10.18.1, qpdf 12.4.2) avec de vrais PDF d'articles : les 100 premières pages liées depuis l'article *France*, téléchargées par `MediaWikiClient` et recomposées par `fit_pdf_to_format` comme dans l'application (97,7 Mo de parties, 1 625 pages). Chaque variante tourne dans un processus neuf ; mémoire = mémoire privée du processus. Sous Windows, la mémoire libérée est rendue au système aussitôt, contrairement à l'allocateur de Linux.

Fusion par qpdf, pic de mémoire :

| Variante (100 articles)                                   | Pic     | Durée  |
|-----------------------------------------------------------|---------|--------|
| actuelle (`--stream-data=preserve`)                       | 938 Mo  | 9,6 s  |
| `--remove-unreferenced-resources=no`                      | 941 Mo  | 9,9 s  |
| `--keep-files-open=y`                                     | 939 Mo  | 10,0 s |
| `--object-streams=disable`                                | 938 Mo  | 9,6 s  |
| options par défaut                                        | 938 Mo  | 9,9 s  |
| par lots de 20 fichiers, puis fusion des lots             | 938 Mo  | 15,7 s |
| copie des pages par pikepdf (`pages.extend`)              | 756 Mo  | 6,2 s  |
| parties compressées (`compress_content_streams`)          | sans objet : les parties pèsent 97,7 Mo compressées ou non | |

Le pic croît avec le livre, environ 10 fois sa taille : 141 Mo pour 25 articles (10,6 Mo), 411 Mo pour 50 (36 Mo), 938 Mo pour 100 (95,6 Mo). qpdf garde en mémoire tous les objets de toutes les pages (93 000 objets pour 100 articles, environ 3,4 ko chacun une fois lus) ; aucune option de qpdf, ni la fusion par lots, n'y change rien. Les PDF de Wikipédia sont déjà au format A4 et compressés : la recomposition les laisse tels quels, il n'y a rien à compresser.

Numérotation des pages (après la fusion, 100 articles) :

| Méthode                                                         | Taille du PDF | Mémoire après | Durée |
|-----------------------------------------------------------------|---------------|---------------|-------|
| superposition d'une page de numéros (`add_overlay`, jusqu'à 1.8.5) | 173,2 Mo   | 418 Mo        | 1,6 s |
| deux petits flux autour du contenu existant (depuis cette mesure) | 96,0 Mo    | 378 Mo        | 1,0 s |

La superposition réécrivait le contenu de chaque page sans le compresser : **les livres numérotés pesaient presque deux fois leur taille réelle** (d'où les 182 Mo de Toolforge pour 100 articles). La nouvelle méthode ne relit ni ne réécrit le contenu des pages. Le gain de mémoire est faible (le coût vient de la lecture de toutes les pages, pas de leur contenu), et le pic de la fusion reste le facteur limitant.

Pistes restantes pour la fusion : écrire soi-même le livre en flux, partie par partie (objets renumérotés, une seule partie en mémoire à la fois), ou donner plus de mémoire au conteneur Toolforge (`--mem`).

### PyMuPDF à la place de qpdf (16/11/2026)

Même banc, PyMuPDF 2.1 (MuPDF 1.28.6), installé seulement dans l'environnement local pour l'essai.

Fusion seule :

| Variante (100 articles)                                     | Pic     | Durée  | Taille fusionnée |
|-------------------------------------------------------------|---------|--------|------------------|
| qpdf (actuel)                                               | 938 Mo  | 9,6 s  | 95,6 Mo          |
| PyMuPDF, `insert_pdf` de toutes les parties puis écriture   | 211 Mo  | 10,1 s | 88,7 Mo          |
| PyMuPDF, par lots de 20, écriture incrémentale après chaque lot | 119 Mo | 10,5 s | 88,7 Mo       |
| PyMuPDF, par lots de 20, réécriture complète après chaque lot | 162 Mo | 11,8 s | 88,7 Mo        |

Avec PyMuPDF tout d'un coup, le pic suit le livre environ 4,5 fois moins vite qu'avec qpdf : 67 Mo pour 25 articles, 113 Mo pour 50, 211 Mo pour 100.

Assemblage complet avec PyMuPDF (fusion par lots incrémentale, signets par `set_toc`, 40 liens internes par `insert_link`, numéros par `insert_text`, écriture) :

| Étape                    | qpdf + pikepdf (actuel) | PyMuPDF                     |
|--------------------------|-------------------------|-----------------------------|
| fusion                   | pic 957 Mo              | pic 131 Mo                  |
| signets et liens         | 80 Mo                   | 72 Mo                       |
| numérotation             | 378 Mo                  | 193 Mo                      |
| écriture                 | 382 Mo                  | 62 Mo                       |
| **pic de l'assemblage**  | **957 Mo**              | **196 Mo**                  |
| durée                    | 11,6 s                  | 15,0 s                      |
| taille du livre          | 96,0 Mo                 | 89,3 Mo                     |

Livre produit vérifié : ouvert sans erreur par pikepdf, 1 625 pages, 100 signets, numéros « 2 », « 501 » et « 1625 » retrouvés dans le texte des pages correspondantes. Non vérifié : rendu visuel, conservation des liens et annotations internes des articles par `insert_pdf`, comportement sous Linux. PyMuPDF est sous licence AGPL-3.0, compatible avec Wikipedia2Book ; roues binaires disponibles pour Linux (Docker, Toolforge).

## Version 1.8.5 (15/11/2026, 22:58 UTC)

Table des matières et licence rendues par blocs, sans boîte flexible ni `overflow-wrap: anywhere`, polices DejaVu imposées ; premier test avec le journal `GET /api/health/generations`. Test arrêté à la demande après le palier de 150 articles (le palier de 200 n'a pas commencé).

| Articles | Pages | Taille du PDF | Durée côté serveur | Résultat |
|----------|-------|---------------|--------------------|----------|
| 100      | —     | 182,2 Mo      | 176,1 s            | réussi   |
| 150      | —     | 280,4 Mo      | 168,7 s            | réussi   |

Journal de l'assemblage (mémoire du processus d'assemblage, RSS ; mémoire du conteneur entre parenthèses), en Mo :

| Étape                          | 100 articles  | 150 articles  |
|--------------------------------|---------------|---------------|
| fin des téléchargements (serveur) | 267 (340)  | 341 (546)     |
| début de l'assemblage          | 76 (422)      | 76 (554)      |
| couverture et table des matières | 101 (471)   | 101 (602)     |
| page de licence                | 149 (519)     | 150 (653)     |
| **fusion (qpdf `--pages`)**    | **1 042 (1 407)** | **1 538 (1 933)** |
| signets et liens               | 1 042 (1 407) | 1 538 (2 022) |
| numérotation                   | 1 043 (1 408) | 1 539 (2 022) |
| écriture du PDF final          | 1 043 (1 585) | 1 537 (2 048) |

**Le pic vient de la fusion, pas de WeasyPrint** : tous les rendus WeasyPrint tiennent en 150 Mo, et la fusion ajoute environ 900 Mo pour 100 articles et 1 390 Mo pour 150, soit environ 5 fois la taille du livre. Le diagnostic de la 1.8.2 (« bond au début de la phase *Application*, WeasyPrint suspecté ») confondait les rendus et la fusion, qui se suivent en quelques secondes : seul le journal par étape les sépare. À 150 articles, le conteneur atteint sa limite de 2 Gio pendant l'écriture (cache du PDF final de 280 Mo) sans être arrêté. Piste suivante : réduire la mémoire de la fusion (option `--remove-unreferenced-resources=no` de qpdf, parties compressées, un seul passage qpdf), à mesurer d'abord en local.

## Version 1.8.3 (15/11/2026, 22:17 UTC)

Une fois les articles téléchargés, l'assemblage (rendus WeasyPrint, fusion, signets, numérotation, écriture) se fait dans un processus séparé qui rend sa mémoire en se terminant. Test lancé 6 s après le démarrage du serveur (22:17:11 UTC), suivi par `GET /api/health/details` toutes les 10 s.

| Articles | Pages | Taille du PDF | Wikipédia | Application | Transfert | Total   | Résultat |
|----------|-------|---------------|-----------|-------------|-----------|---------|----------|
| 100      | 1 637 | 181,8 Mo      | 115,5 s   | 11,8 s      | 26,6 s    | 154,0 s | réussi   |
| 150      | 2 586 | 280,0 Mo      | 93,5 s    | 21,9 s      | 48,1 s    | 163,5 s | réussi   |
| 200      | —     | —             | —         | —           | —         | 217,2 s | échec    |

Mémoire relevée (Mo ; le conteneur compte le serveur, le processus d'assemblage et le cache des fichiers temporaires) :

| Heure (UTC) | Moment                                     | Conteneur | Serveur (RSS) | Fichiers temporaires |
|-------------|--------------------------------------------|-----------|---------------|----------------------|
| 22:19:19    | 100 articles, fin des téléchargements      | 311       | 248           | 88                   |
| 22:19:30    | 100 articles, assemblage                   | 1 472     | 258           | 183                  |
| 22:20:01    | génération terminée                        | 304       | 257           | 0                    |
| 22:21:37    | 150 articles, fin des téléchargements      | 605       | 348           | 149                  |
| 22:21:47    | 150 articles, assemblage                   | 2 048     | 348           | 186                  |
| 22:22:50    | génération terminée                        | 399       | 348           | 5                    |
| 22:26:07    | 200 articles, fin des téléchargements      | 627       | 374           | 200                  |
| 22:26:18    | 200 articles, assemblage (dernier relevé)  | 1 137     | 374           | 204                  |
| 22:26:28    | après redémarrage (22:26:26 UTC)           | 75        | 103           | 0                    |

Constats :

1. **La mémoire gardée entre deux générations a disparu** : le serveur reste entre 250 et 375 Mo pendant tout le test, contre 1,4 Go après chaque génération en 1.8.2, et le conteneur redescend à 300–400 Mo une fois le livre envoyé.
2. **La limite remonte de 100 à 150 articles**, sans encore retrouver les 200 articles de la 1.7.7.
3. **L'assemblage lui-même reste trop gourmand** : environ 1,2 Go dans le processus séparé pour 100 articles, et le conteneur touche sa limite de 2 Gio à 150 articles (il tient, une partie étant du cache de fichiers récupérable). À 200 articles, c'est **tout le conteneur** qui est arrêté, pas seulement le processus d'assemblage : le serveur redémarre (22:26:26 UTC) et le client ne reçoit pas le message « L'assemblage du livre s'est arrêté… ». Sur Toolforge, la séparation libère donc la mémoire entre deux générations, mais ne protège pas le serveur d'un assemblage qui dépasse la limite.

Prochaine piste : mesurer quelle étape de l'assemblage consomme ce pic (rendus WeasyPrint de la table des matières et de la licence, fusion par qpdf, ou numérotation).

## Version 1.8.2 (15/11/2026, 21:52 UTC)

Premier test suivi en direct par `GET /api/health/details` (relevé toutes les 10 s pendant le test ; mémoire du conteneur limitée à 2 Gio).

| Articles | Pages | Taille du PDF | Wikipédia | Application | Transfert | Total   | Résultat |
|----------|-------|---------------|-----------|-------------|-----------|---------|----------|
| 100      | 1 637 | 182,2 Mo      | 119,4 s   | 11,4 s      | 27,1 s    | 158,0 s | réussi   |
| 150      | —     | —             | —         | —           | —         | 105,3 s | échec    |

Mémoire relevée (Mo) :

| Heure (UTC) | Moment                                   | Conteneur | Processus (RSS) | Fichiers temporaires |
|-------------|------------------------------------------|-----------|-----------------|----------------------|
| 21:52:43    | avant le test                            | 572       | 589             | 0                    |
| 21:54:39    | 100 articles, fin des téléchargements    | 668       | 596             | 85                   |
| 21:54:55    | 100 articles, assemblage                 | 1 585     | 1 399           | 191                  |
| 21:55:05    | 100 articles, pic                        | 1 664     | 1 399           | 270                  |
| 21:55:26    | génération terminée                      | 1 382     | 1 396           | 0                    |
| 21:57:01    | 150 articles, dernier relevé avant l'arrêt | 1 540   | 1 402           | 147                  |

Deux constats :

1. **Pendant les téléchargements, la mémoire du processus reste stable** (environ 590 Mo, la recomposition des articles ne la fait pas monter). Elle **bondit d'environ 800 Mo en moins de 16 s au début de la phase *Application*** (pages générées par WeasyPrint, fusion, numérotation).
2. **Cette mémoire n'est pas rendue au système après la génération** : le processus reste à 1,4 Go une fois le livre envoyé, sans cache de l'application qui l'explique ; c'est vraisemblablement l'allocateur (glibc `malloc` : fragmentation, une réserve par fil d'exécution de `asyncio.to_thread`) et les caches des bibliothèques en C (WeasyPrint, Pango, fontconfig, qpdf). Pendant le palier de 150 articles, le processus reste à 1,4 Go pendant les téléchargements : cette mémoire est réutilisée, elle ne s'ajoute pas. Le conteneur est arrêté pendant ce palier (HTTP 503 à 21:57:10 UTC, redémarrage à 21:57:12 UTC). Rien ne permet encore de dire si 150 articles échouent aussi juste après un redémarrage : la part de la mémoire gardée entre deux générations dans la limite reste à mesurer.

## Version 1.8.0 (15/11/2026, 21:12 UTC)

Mesure prévue pour confirmer celle de la 1.7.10 ; entre-temps, Toolforge était passé en 1.8.0 (commit `94cb666`, serveur démarré à 21:03:32 UTC). La 1.8.0 ajoute d'autres projets Wikimédia et ne change pas l'assemblage du livre. Le réseau de Toolforge était lent, d'où un transfert long, sans lien avec l'application.

| Articles | Pages | Taille du PDF | Wikipédia | Application | Transfert | Total   | Résultat |
|----------|-------|---------------|-----------|-------------|-----------|---------|----------|
| 100      | 1 637 | 182,0 Mo      | 116,1 s   | 8,8 s       | 322,9 s   | 447,8 s | réussi   |
| 150      | —     | —             | —         | —           | —         | 94,2 s  | échec    |

**Limite : environ 100 articles**, comme en 1.7.10. À 150 articles, le serveur redémarre (heure de démarrage de `GET /api/stats/hourly` remise à 21:21:17 UTC), plus tôt qu'à 19 h (94 s au lieu de 159 s). Cause identifiée depuis dans les données Grafana : arrêt `OOMKilled` du conteneur, limité à 2 Gio (voir `todo.md`).

## Version 1.7.10 (15/11/2026)

Les fichiers temporaires des parties sont supprimés dès la fusion : l'espace temporaire d'une génération passe de trois à deux fois la taille du livre.

| Articles | Pages | Taille du PDF | Wikipédia | Application | Transfert | Total   | Résultat |
|----------|-------|---------------|-----------|-------------|-----------|---------|----------|
| 100      | 1 637 | 182,0 Mo      | 36,2 s    | 13,3 s      | 24,3 s    | 73,8 s  | réussi   |
| 150      | —     | —             | —         | —           | —         | 159,0 s | échec    |
| 200      | —     | —             | —         | —           | —         | 249,8 s | échec    |

**Limite : environ 100 articles, soit 1 600 pages et 180 Mo de PDF — régression par rapport à la 1.7.7**, qui passait 200 articles. À 150 et 200 articles, le serveur redémarre (heure de démarrage de `GET /api/stats/hourly` remise à 19:04:37 puis 19:09:07 UTC, réponse « no healthy upstream » juste après l'échec). La phase *Application* à 100 articles prend 13,3 s, contre 7,1 s en 1.7.7.

Les deux échecs surviennent vers la fin des téléchargements ou pendant l'assemblage (la phase *Wikipédia* durait 137 à 144 s pour 150 à 200 articles en 1.7.7). Les changements depuis la 1.7.7 sont la fusion par qpdf et le créneau de téléchargement gardé jusqu'à la recomposition (1.7.9), puis la suppression des parties après fusion (1.7.10). L'hypothèse de l'espace temporaire, retenue après l'échec de la 1.7.9, ne suffit pas : la 1.7.10 n'occupe pas plus d'espace temporaire que la 1.7.7. Cause à rechercher dans les journaux de Toolforge (`toolforge webservice logs`, événements Kubernetes du pod).

## Version 1.7.9 (15/11/2026)

Fusion par qpdf (`--pages`) au lieu de `pages.extend` ; mémoire au pic mesurée en local : 262 Mo pour 300 articles.

| Articles | Total | Résultat |
|----------|-------|----------|
| 300      | 347 s | échec    |

Le serveur redémarre encore à 300 articles. La mémoire mesurée en local restant basse, la piste retenue est l'espace temporaire : les fichiers des parties, le fichier fusionné et le PDF final coexistaient, soit environ trois fois la taille du livre. La cause exacte (mémoire ou quota d'espace temporaire du pod) n'a pas pu être lue dans les événements Kubernetes de Toolforge.

## Version 1.7.7 (15/11/2026)

Livre assemblé sur disque temporaire. Le réseau de Toolforge était lent ce jour-là, d'où des transferts longs, sans lien avec l'application.

| Articles | Pages | Taille du PDF | Wikipédia | Application | Transfert | Total     | Résultat |
|----------|-------|---------------|-----------|-------------|-----------|-----------|----------|
| 100      | 1 637 | 181,8 Mo      | 116,2 s   | 7,1 s       | 390,1 s   | 513,5 s   | réussi   |
| 150      | 2 586 | 280,0 Mo      | 144,3 s   | 9,0 s       | 814,2 s   | 967,5 s   | réussi   |
| 200      | 3 435 | 375,5 Mo      | 137,0 s   | 11,5 s      | 911,6 s   | 1 060,1 s | réussi   |
| 300      | —     | —             | —         | —           | —         | 174 s     | échec    |

**Limite : environ 200 articles, soit 3 400 pages et 375 Mo de PDF.**

## Version 1.7.5 (15/11/2026)

Livre assemblé entièrement en mémoire.

| Articles | Pages | Taille du PDF | Wikipédia | Application | Transfert | Total   | Résultat |
|----------|-------|---------------|-----------|-------------|-----------|---------|----------|
| 25       | 202   | 20,4 Mo       | 24,7 s    | 5,6 s       | 4,1 s     | 34,3 s  | réussi   |
| 50       | 684   | 73,6 Mo       | 33,2 s    | 17,1 s      | 15,1 s    | 65,3 s  | réussi   |
| 100      | 1 636 | 182,4 Mo      | 107,6 s   | 42,7 s      | 37,5 s    | 187,8 s | réussi   |
| 150      | —     | —             | —         | —           | —         | 181 s   | échec    |
| 200      | —     | —             | —         | —           | —         | 266 s   | échec    |

**Limite : environ 100 articles, soit 1 600 pages et 180 Mo de PDF.**
