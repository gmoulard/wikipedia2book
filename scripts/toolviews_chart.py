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
from datetime import date
from pathlib import Path

from toolviews_stats import read_rows

DAILY_DAYS = 31
SOURCE = "https://github.com/gmoulard/wikipedia2book/blob/main/toolviews.csv"


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


def build_page(rows):
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
    args = parser.parse_args()
    try:
        if not args.csv.exists():
            raise ValueError(f"{args.csv} introuvable")
        rows, _ = read_rows(args.csv)
        args.output.write_text(build_page(rows), encoding="utf-8")
    except (ValueError, KeyError) as error:
        print(f"Erreur statistiques : {error}", file=sys.stderr)
        return 1
    print(f"{args.output} : {len(rows)} jour(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
