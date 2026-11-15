# This file is part of Wikipedia2Book
# <https://github.com/gmoulard/wikipedia2book>.
# Copyright (c) 2026 Guillaume Moulard.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, version 3.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import argparse
import math
import sys
from collections import defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path

import toolforge_hourly
from toolviews_stats import read_rows

DAILY_DAYS = 31
HOURLY_HOURS = 36
HOUR = "%Y-%m-%dT%H"
SOURCE = "https://github.com/gmoulard/wikipedia2book/blob/main/docs/toolviews.csv"


def xychart(title, labels, values, width):
    axis = ", ".join(f'"{label}"' for label in labels)
    return "\n".join([
        "```mermaid",
        f'%%{{init: {{"xyChart": {{"width": {width}, "showDataLabel": true, "showDataLabelOutsideBar": true}}, '
        '"themeVariables": {"xyChart": {"plotColorPalette": "#3366cc"}}}}%%',
        "xychart-beta",
        f'    title "{title}"',
        f"    x-axis [{axis}]",
        f'    y-axis "Hits" 0 --> {math.ceil(max(max(values), 1) * 1.15)}',
        f"    bar [{', '.join(str(value) for value in values)}]",
        "```",
    ])


def hourly_section(hourly):
    totals = defaultdict(int)
    for (hour, _), hits in hourly.items():
        totals[hour] += hits
    if not totals:
        return []
    end = datetime.strptime(max(totals), HOUR)
    first = max(end - timedelta(hours=HOURLY_HOURS - 1), datetime.strptime(min(totals), HOUR))
    hours = [first + timedelta(hours=i) for i in range((end - first) // timedelta(hours=1) + 1)]
    return [
        f"## Hourly hits / Hits par heure ({len(hours)} hours, UTC)",
        "Source: Toolforge webservice logs, read every day and just before each deployment, since they are "
        "erased at each restart. Every request seen by the application counts, static files included; "
        "an hour whose logs were lost before being read shows 0.",
        "Source : journaux du webservice Toolforge, relevés chaque jour et juste avant chaque déploiement. "
        "Une heure dont les journaux ont été perdus avant d'être relevés vaut 0.",
        xychart(
            f"Hourly hits (UTC) {hours[0]:%d/%m %Hh} - {hours[-1]:%d/%m %Hh}",
            [f"{hour:%H}" for hour in hours],
            [totals.get(hour.strftime(HOUR), 0) for hour in hours],
            1000,
        ),
    ]


def build_page(rows, hourly=None):
    if not rows:
        raise ValueError("toolviews.csv ne contient aucun jour")
    days = sorted(rows)
    hits = {day: int(rows[day]["hits"]) for day in days}
    recent = days[-DAILY_DAYS:]
    monthly = defaultdict(int)
    for day in days:
        monthly[day[:7]] += hits[day]
    months = sorted(monthly)
    return "\n\n".join([
        "# Usage statistics / Statistiques d'utilisation",
        f"Wikipedia2Book on Toolforge, {days[0]} → {days[-1]}: **{sum(hits.values())}** hits.",
        "Source: [Toolviews](https://toolviews.toolforge.org/), updated daily "
        f"([toolviews.csv]({SOURCE})). Hits are HTTP requests, not people (page, static files, API calls).",
        "Les hits sont des requêtes HTTP, pas des personnes. Mise à jour quotidienne.",
        *hourly_section(hourly or {}),
        f"## Daily hits / Hits par jour ({len(recent)} days)",
        xychart(
            f"Daily hits {date.fromisoformat(recent[0]):%d/%m/%Y} - {date.fromisoformat(recent[-1]):%d/%m/%Y}",
            [str(date.fromisoformat(day).day) for day in recent],
            [hits[day] for day in recent],
            1000,
        ),
        "## Monthly hits / Hits par mois",
        xychart("Monthly hits", months, [monthly[month] for month in months], 700),
    ]) + "\n"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("csv", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--hourly", type=Path)
    args = parser.parse_args()
    try:
        if not args.csv.exists():
            raise ValueError(f"{args.csv} introuvable")
        rows, _ = read_rows(args.csv)
        hourly = toolforge_hourly.read_rows(args.hourly) if args.hourly else {}
        args.output.write_text(build_page(rows, hourly), encoding="utf-8")
    except (ValueError, KeyError) as error:
        print(f"Erreur statistiques : {error}", file=sys.stderr)
        return 1
    print(f"{args.output} : {len(rows)} jour(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
