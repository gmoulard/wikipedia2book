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
