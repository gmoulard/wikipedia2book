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
FIELDS = ["date", "hits"]
DELIMITER = ";"
USER_AGENT = "Wikipedia2Book-stats/1.0 (https://github.com/gmoulard/wikipedia2book)"


def fetch(url):
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


class UnexpectedResponse(ValueError):
    pass


def daily(start, end, fetcher):
    url = f"{API}/tool/{TOOL}/daily/{start.isoformat()}/{end.isoformat()}"
    data = fetcher(url)
    if not isinstance(data, dict) or not isinstance(data.get("results"), dict):
        raise UnexpectedResponse(f"{url} : pas de dictionnaire « results » dans la réponse : {str(data)[:300]}")
    counts = {}
    for day, values in data["results"].items():
        try:
            date.fromisoformat(day)
        except (TypeError, ValueError):
            raise UnexpectedResponse(f"{url} : date invalide {day!r}") from None
        if not isinstance(values, dict) or (values and TOOL not in values):
            raise UnexpectedResponse(f"{url} : valeur inattendue pour {day} (clé « {TOOL} » absente) : {str(values)[:300]}")
        count = values.get(TOOL, 0)
        if isinstance(count, bool) or not isinstance(count, int) or count < 0:
            raise UnexpectedResponse(f"{url} : compte invalide pour {day} : {count!r}")
        counts[day] = count
    return counts


def read_rows(path):
    if not path.exists():
        return {}, False
    with path.open(newline="", encoding="utf-8") as handle:
        header = handle.readline()
        handle.seek(0)
        delimiter = "," if "," in header and DELIMITER not in header else DELIMITER
        reader = csv.DictReader(handle, delimiter=delimiter)
        rows = {row["date"]: row for row in reader}
        return rows, delimiter != DELIMITER or reader.fieldnames != FIELDS


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
    hits = daily(missing[0], missing[-1], fetcher)
    published = set(hits) | set(rows)
    if not published:
        return []
    last = max(published)
    added = []
    for day in missing:
        key = day.isoformat()
        if key <= last:
            rows[key] = {"date": key, "hits": hits.get(key, 0)}
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
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, UnexpectedResponse) as error:
        print(f"Erreur Toolviews : {error}", file=sys.stderr)
        return 1
    except PermissionError:
        print(f"Impossible d'écrire {args.csv} : fichier ouvert dans un autre programme (Excel ?). Fermez-le puis relancez.", file=sys.stderr)
        return 1
    print(f"{len(added)} jour(s) ajouté(s) à {args.csv}" + (f" : {', '.join(added)}" if added else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
