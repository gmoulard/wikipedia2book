# Usage statistics / Statistiques d'utilisation

Wikipedia2Book on Toolforge, 2026-11-01 → 2026-11-15: **5017** hits.

Source: [Toolviews](https://toolviews.toolforge.org/), updated daily ([toolviews.csv](https://github.com/gmoulard/wikipedia2book/blob/main/docs/toolviews.csv)). Hits are HTTP requests, not people (page, static files, API calls).

Les hits sont des requêtes HTTP, pas des personnes. Mise à jour quotidienne.

## Hourly hits / Hits par heure (UTC, last 36 hours / 36 dernières heures)

Source: Toolforge webservice logs, read every day and just before each deployment, since they are erased at each restart. Every request seen by the application counts, static files included; an hour whose logs were lost before being read shows 0.

Source : journaux du webservice Toolforge, relevés chaque jour et juste avant chaque déploiement. Une heure dont les journaux ont été perdus avant d'être relevés vaut 0. À l'ouverture de la page, les heures plus récentes sont ajoutées en direct depuis l'application.

<div id="hourly-data" hidden data-hours='{"2026-11-14T20":20,"2026-11-14T21":52,"2026-11-14T22":1,"2026-11-14T23":10,"2026-11-15T00":17,"2026-11-15T01":1,"2026-11-15T02":1,"2026-11-15T03":8,"2026-11-15T04":68,"2026-11-15T05":70,"2026-11-15T07":13,"2026-11-15T08":14,"2026-11-15T09":21,"2026-11-15T10":21,"2026-11-15T11":89,"2026-11-15T13":17,"2026-11-15T14":1,"2026-11-15T15":2,"2026-11-15T16":11,"2026-11-15T17":1,"2026-11-15T18":32,"2026-11-15T19":20,"2026-11-15T20":32,"2026-11-15T21":26,"2026-11-15T22":267,"2026-11-15T23":50,"2026-11-16T01":16,"2026-11-16T02":1,"2026-11-16T03":22,"2026-11-16T04":279,"2026-11-16T05":661,"2026-11-16T06":571,"2026-11-16T07":349,"2026-11-16T08":180,"2026-11-16T12":62,"2026-11-16T13":93,"2026-11-16T14":341,"2026-11-16T15":197,"2026-11-16T16":116,"2026-11-16T17":128,"2026-11-16T18":45,"2026-11-16T19":41,"2026-11-16T20":34,"2026-11-16T21":4}'></div>

```mermaid
%%{init: {"xyChart": {"width": 1000, "showDataLabel": true, "showDataLabelOutsideBar": true}, "themeVariables": {"xyChart": {"plotColorPalette": "#3366cc"}}}}%%
xychart-beta
    title "Hourly hits (UTC) 15/11 10h - 16/11 21h"
    x-axis ["10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "22", "23", "00", "01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21"]
    y-axis "Hits" 0 --> 761
    bar [21, 89, 0, 17, 1, 2, 11, 1, 32, 20, 32, 26, 267, 50, 0, 16, 1, 22, 279, 661, 571, 349, 180, 0, 0, 0, 62, 93, 341, 197, 116, 128, 45, 41, 34, 4]
```

## Daily hits / Hits par jour (15 days)

```mermaid
%%{init: {"xyChart": {"width": 1000, "showDataLabel": true, "showDataLabelOutsideBar": true}, "themeVariables": {"xyChart": {"plotColorPalette": "#3366cc"}}}}%%
xychart-beta
    title "Daily hits 01/11/2026 - 15/11/2026"
    x-axis ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15"]
    y-axis "Hits" 0 --> 2476
    bar [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 287, 2153, 1433, 1144]
```

## Monthly hits / Hits par mois

```mermaid
%%{init: {"xyChart": {"width": 700, "showDataLabel": true, "showDataLabelOutsideBar": true}, "themeVariables": {"xyChart": {"plotColorPalette": "#3366cc"}}}}%%
xychart-beta
    title "Monthly hits"
    x-axis ["2026-11"]
    y-axis "Hits" 0 --> 5770
    bar [5017]
```
