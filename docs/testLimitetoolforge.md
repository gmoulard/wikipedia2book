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
