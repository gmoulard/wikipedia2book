# Usage statistics / Statistiques d'utilisation

Wikipedia2Book on Toolforge, 2026-11-01 → 2026-11-18: **12641** hits.

Source: [Toolviews](https://toolviews.toolforge.org/), updated daily ([toolviews.csv](https://github.com/gmoulard/wikipedia2book/blob/main/docs/toolviews.csv)). Hits are HTTP requests, not people (page, static files, API calls).

Les hits sont des requêtes HTTP, pas des personnes. Mise à jour quotidienne.

## Hourly hits / Hits par heure (UTC, last 36 hours / 36 dernières heures)

Source: Toolforge webservice logs, read every day and just before each deployment, since they are erased at each restart. Every request seen by the application counts, static files included; an hour whose logs were lost before being read shows 0.

Source : journaux du webservice Toolforge, relevés chaque jour et juste avant chaque déploiement. Une heure dont les journaux ont été perdus avant d'être relevés vaut 0. À l'ouverture de la page, les heures plus récentes sont ajoutées en direct depuis l'application.

<div id="hourly-data" hidden data-hours='{"2026-11-14T20":20,"2026-11-14T21":52,"2026-11-14T22":1,"2026-11-14T23":10,"2026-11-15T00":17,"2026-11-15T01":1,"2026-11-15T02":1,"2026-11-15T03":8,"2026-11-15T04":68,"2026-11-15T05":70,"2026-11-15T07":13,"2026-11-15T08":14,"2026-11-15T09":21,"2026-11-15T10":21,"2026-11-15T11":89,"2026-11-15T13":17,"2026-11-15T14":1,"2026-11-15T15":2,"2026-11-15T16":11,"2026-11-15T17":1,"2026-11-15T18":32,"2026-11-15T19":20,"2026-11-15T20":32,"2026-11-15T21":26,"2026-11-15T22":267,"2026-11-15T23":50,"2026-11-16T01":16,"2026-11-16T02":1,"2026-11-16T03":22,"2026-11-16T04":279,"2026-11-16T05":661,"2026-11-16T06":571,"2026-11-16T07":349,"2026-11-16T08":180,"2026-11-16T12":62,"2026-11-16T13":93,"2026-11-16T14":341,"2026-11-16T15":197,"2026-11-16T16":116,"2026-11-16T17":128,"2026-11-16T18":45,"2026-11-16T19":41,"2026-11-16T20":34,"2026-11-16T21":43,"2026-11-16T23":9,"2026-11-17T00":55,"2026-11-17T01":233,"2026-11-17T02":587,"2026-11-17T03":20,"2026-11-17T04":18,"2026-11-17T05":35,"2026-11-17T06":6,"2026-11-17T07":2,"2026-11-17T08":2,"2026-11-17T09":25,"2026-11-17T10":25,"2026-11-17T11":221,"2026-11-17T12":127,"2026-11-17T13":42,"2026-11-17T14":94,"2026-11-17T15":216,"2026-11-17T16":142,"2026-11-17T17":110,"2026-11-17T18":2,"2026-11-17T19":9,"2026-11-17T20":1,"2026-11-17T21":18,"2026-11-17T22":12,"2026-11-17T23":112,"2026-11-18T00":97,"2026-11-18T01":90,"2026-11-18T02":26,"2026-11-18T03":14,"2026-11-18T05":11,"2026-11-18T06":48,"2026-11-18T07":3,"2026-11-18T08":35,"2026-11-18T09":35,"2026-11-18T10":74,"2026-11-18T11":30,"2026-11-18T12":40,"2026-11-18T13":10,"2026-11-18T14":150,"2026-11-18T15":58,"2026-11-18T16":72,"2026-11-18T17":14,"2026-11-18T18":101,"2026-11-18T19":1,"2026-11-18T20":5,"2026-11-18T21":10,"2026-11-18T22":29,"2026-11-18T23":11,"2026-11-19T00":2,"2026-11-19T02":1129,"2026-11-19T03":34,"2026-11-19T04":8,"2026-11-19T05":4,"2026-11-19T06":28,"2026-11-19T08":54,"2026-11-19T09":1,"2026-11-19T10":30,"2026-11-19T11":5,"2026-11-19T12":17,"2026-11-19T13":26,"2026-11-19T14":16,"2026-11-19T15":15,"2026-11-19T16":12,"2026-11-19T17":12,"2026-11-19T18":69,"2026-11-19T19":11,"2026-11-19T20":1023,"2026-11-19T21":27}'></div>

```mermaid
%%{init: {"xyChart": {"width": 1000, "showDataLabel": true, "showDataLabelOutsideBar": true}, "themeVariables": {"xyChart": {"plotColorPalette": "#3366cc"}}}}%%
xychart-beta
    title "Hourly hits (UTC) 18/11 10h - 19/11 21h"
    x-axis ["10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "22", "23", "00", "01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21"]
    y-axis "Hits" 0 --> 1299
    bar [74, 30, 40, 10, 150, 58, 72, 14, 101, 1, 5, 10, 29, 11, 2, 0, 1129, 34, 8, 4, 28, 0, 54, 1, 30, 5, 17, 26, 16, 15, 12, 12, 69, 11, 1023, 27]
```

## Daily PDF generations / Générations de PDF par jour (1 days)

Since 2026-11-19: **8** generations, 8 finished, 0 with an error, 0 abandoned. A book in volumes counts one generation per volume.

Depuis le 19/11/2026 : **8** générations, 8 terminées, 0 en erreur, 0 abandonnées. Un livre en volumes compte une génération par volume. Source : journaux du webservice Toolforge, relevés comme les hits par heure.

```mermaid
%%{init: {"xyChart": {"width": 1000, "showDataLabel": true, "showDataLabelOutsideBar": true}, "themeVariables": {"xyChart": {"plotColorPalette": "#3366cc"}}}}%%
xychart-beta
    title "Daily generations 19/11/2026 - 19/11/2026"
    x-axis ["19"]
    y-axis "Generations" 0 --> 10
    bar [8]
```

## Daily hits / Hits par jour (18 days)

```mermaid
%%{init: {"xyChart": {"width": 1000, "showDataLabel": true, "showDataLabelOutsideBar": true}, "themeVariables": {"xyChart": {"plotColorPalette": "#3366cc"}}}}%%
xychart-beta
    title "Daily hits 01/11/2026 - 18/11/2026"
    x-axis ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18"]
    y-axis "Hits" 0 --> 5485
    bar [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 287, 2153, 1433, 1144, 4769, 2125, 730]
```

## Monthly hits / Hits par mois

```mermaid
%%{init: {"xyChart": {"width": 700, "showDataLabel": true, "showDataLabelOutsideBar": true}, "themeVariables": {"xyChart": {"plotColorPalette": "#3366cc"}}}}%%
xychart-beta
    title "Monthly hits"
    x-axis ["2026-11"]
    y-axis "Hits" 0 --> 14538
    bar [12641]
```
