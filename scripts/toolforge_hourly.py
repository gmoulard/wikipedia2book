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
GENERATION_FIELDS = ["hour", "pod", "status", "generations"]
GENERATION_LINE = re.compile(r"^(wikipedia2book-[A-Za-z0-9-]+);(\d{4}-\d{2}-\d{2}T\d{2});(done|error|aborted);(\d+)$")


def _section(text, name, pattern):
    lines = [line.strip() for line in text.splitlines()]
    begin, end = f"BEGIN-{name}", f"END-{name}"
    if begin not in lines or end not in lines:
        raise ValueError(f"relevé incomplet : marqueurs {begin}/{end} absents")
    matches = []
    for line in filter(None, lines[lines.index(begin) + 1:lines.index(end)]):
        match = pattern.match(line)
        if not match:
            raise ValueError(f"ligne inattendue dans le relevé : {line[:200]!r}")
        datetime.strptime(match.group(2), "%Y-%m-%dT%H")
        matches.append(match.groups())
    return matches


def parse(text):
    return {(hour, pod): int(hits) for pod, hour, hits in _section(text, "HOURLY", LINE)}


def parse_generations(text):
    return {(hour, pod, status): int(count) for pod, hour, status, count in _section(text, "GENERATIONS", GENERATION_LINE)}


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


def read_generations(path):
    if not path.exists():
        return {}
    with path.open(newline="", encoding="utf-8") as handle:
        return {(row["hour"], row["pod"], row["status"]): int(row["generations"]) for row in csv.DictReader(handle, delimiter=DELIMITER)}


def merge_generations(rows, captured):
    merged = dict(rows)
    for key, count in captured.items():
        merged[key] = max(merged.get(key, 0), count)
    return merged


def write_generations(path, rows):
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, delimiter=DELIMITER)
        writer.writerow(GENERATION_FIELDS)
        for (hour, pod, status), count in sorted(rows.items()):
            writer.writerow([hour, pod, status, count])


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
    parser.add_argument("--generations", type=Path)
    args = parser.parse_args()
    try:
        text = args.capture.read_text(encoding="utf-8")
        captured = parse(text)
        generations = parse_generations(text) if args.generations else {}
        rows = merge(read_rows(args.csv), captured, datetime.now(timezone.utc))
        write_rows(args.csv, rows)
        if args.generations:
            write_generations(args.generations, merge_generations(read_generations(args.generations), generations))
    except (OSError, ValueError, KeyError) as error:
        print(f"Erreur relevé horaire : {error}", file=sys.stderr)
        return 1
    print(f"{args.csv} : {len(captured)} heure(s) relevée(s), {len(rows)} ligne(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
