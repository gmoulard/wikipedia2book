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
import csv
import json
import sys
import urllib.error
import urllib.request
from datetime import date, timedelta
from pathlib import Path

API = "https://toolviews.toolforge.org/api/v1"
TOOL = "wikipedia2book"
START = date(2026, 11, 1)
FIELDS = ["date", "hits", "unique_visitors"]
DELIMITER = ";"
USER_AGENT = "Wikipedia2Book-stats/1.0 (https://github.com/gmoulard/wikipedia2book)"


def fetch(url):
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def daily(kind, start, end, fetcher):
    prefix = f"{API}/unique/tool" if kind == "unique" else f"{API}/tool"
    data = fetcher(f"{prefix}/{TOOL}/daily/{start.isoformat()}/{end.isoformat()}")
    return {day: values.get(TOOL, 0) for day, values in data.get("results", {}).items()}


def read_rows(path):
    if not path.exists():
        return {}, False
    with path.open(newline="", encoding="utf-8") as handle:
        header = handle.readline()
        handle.seek(0)
        delimiter = "," if "," in header and DELIMITER not in header else DELIMITER
        return {row["date"]: row for row in csv.DictReader(handle, delimiter=delimiter)}, delimiter != DELIMITER


def write_rows(path, rows):
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, delimiter=DELIMITER)
        writer.writeheader()
        for day in sorted(rows):
            writer.writerow({field: rows[day][field] for field in FIELDS})


def update(path, today, fetcher=fetch):
    rows, outdated = read_rows(path)
    end = today - timedelta(days=1)
    missing = [START + timedelta(days=i) for i in range((end - START).days + 1)]
    missing = [day for day in missing if day.isoformat() not in rows]
    if not missing:
        if outdated:
            write_rows(path, rows)
        return []
    hits = daily("hits", missing[0], missing[-1], fetcher)
    unique = daily("unique", missing[0], missing[-1], fetcher)
    published = set(hits) | set(unique) | set(rows)
    if not published:
        return []
    last = max(published)
    added = []
    for day in missing:
        key = day.isoformat()
        if key <= last:
            rows[key] = {"date": key, "hits": hits.get(key, 0), "unique_visitors": unique.get(key, 0)}
            added.append(key)
    if added or outdated:
        write_rows(path, rows)
    return added


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("csv", nargs="?", default="toolviews.csv", type=Path)
    args = parser.parse_args()
    try:
        added = update(args.csv, date.today())
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as error:
        print(f"Erreur Toolviews : {error}", file=sys.stderr)
        return 1
    except PermissionError:
        print(f"Impossible d'écrire {args.csv} : fichier ouvert dans un autre programme (Excel ?). Fermez-le puis relancez.", file=sys.stderr)
        return 1
    print(f"{len(added)} jour(s) ajouté(s) à {args.csv}" + (f" : {', '.join(added)}" if added else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
