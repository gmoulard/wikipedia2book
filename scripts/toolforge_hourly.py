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
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

FIELDS = ["hour", "pod", "hits"]
DELIMITER = ";"
KEEP = timedelta(days=7)
LINE = re.compile(r"^(wikipedia2book-[A-Za-z0-9-]+);(\d{4}-\d{2}-\d{2}T\d{2});(\d+)$")


def parse(text):
    lines = [line.strip() for line in text.splitlines()]
    if "BEGIN-HOURLY" not in lines or "END-HOURLY" not in lines:
        raise ValueError("relevé incomplet : marqueurs BEGIN-HOURLY/END-HOURLY absents")
    body = lines[lines.index("BEGIN-HOURLY") + 1:lines.index("END-HOURLY")]
    captured = {}
    for line in filter(None, body):
        match = LINE.match(line)
        if not match:
            raise ValueError(f"ligne inattendue dans le relevé : {line[:200]!r}")
        pod, hour, hits = match.groups()
        datetime.strptime(hour, "%Y-%m-%dT%H")
        captured[(hour, pod)] = int(hits)
    return captured


def read_rows(path):
    if not path.exists():
        return {}
    with path.open(newline="", encoding="utf-8") as handle:
        return {(row["hour"], row["pod"]): int(row["hits"]) for row in csv.DictReader(handle, delimiter=DELIMITER)}


def merge(rows, captured, now):
    merged = dict(rows)
    for key, hits in captured.items():
        merged[key] = max(merged.get(key, 0), hits)
    oldest = (now - KEEP).strftime("%Y-%m-%dT%H")
    return {key: hits for key, hits in merged.items() if key[0] >= oldest}


def write_rows(path, rows):
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, delimiter=DELIMITER)
        writer.writerow(FIELDS)
        for (hour, pod), hits in sorted(rows.items()):
            writer.writerow([hour, pod, hits])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("csv", type=Path)
    parser.add_argument("capture", type=Path)
    args = parser.parse_args()
    try:
        captured = parse(args.capture.read_text(encoding="utf-8"))
        rows = merge(read_rows(args.csv), captured, datetime.now(timezone.utc))
        write_rows(args.csv, rows)
    except (OSError, ValueError, KeyError) as error:
        print(f"Erreur relevé horaire : {error}", file=sys.stderr)
        return 1
    print(f"{args.csv} : {len(captured)} heure(s) relevée(s), {len(rows)} ligne(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
