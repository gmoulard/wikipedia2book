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

import csv
import io
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CSV_PATH = ROOT / "docs" / "benchmark-results.csv"
SPECS = {"fr": ROOT / "docs" / "SPECIFICATIONS.fr.md", "en": ROOT / "docs" / "SPECIFICATIONS.en.md"}
FIELDS = ["date", "version", "target", "level", "scenario", "pages", "wikipedia_s", "application_s", "transfer_s", "total_s", "app_per_page_delta_pct", "verdict"]
VERDICTS = ("ok", "watch", "regression", "failure", "new")
START = "<!-- benchmark-table:start -->"
END = "<!-- benchmark-table:end -->"
SCENARIOS = {
    "50-pages": ("50 p.", "50 p."),
    "200-pages": ("200 p.", "200 p."),
    "1-article": ("1 art.", "1 art."),
    "50-pages-sans-numerotation": ("50 p. sans n°", "50 p. no numbers"),
    "200-pages-chapitres": ("200 p. chapitres", "200 p. chapters"),
    "200-pages-a5-paysage": ("200 p. A5 paysage", "200 p. A5 landscape"),
    "20-articles": ("20 art.", "20 art."),
    "livre-exemple-images": ("Livre exemple", "Sample book"),
    "livre-reference-images": ("Livre de référence", "Reference book"),
}
LEVELS = {"trial": ("essai (1 génération)", "trial (1 generation)")}
TEXT = {
    "fr": {
        "header": ("Version", "Date", "Cible", "Niveau"),
        "new": '<span class="bench-new">nouveau</span>',
        "failure": "❌ échec",
        "legend": "Une ligne par passage, une colonne par scénario. ✅ ok ; <span class=\"bench-new\">nouveau</span> : premier passage du scénario, pas encore de référence ; ⚠️ à surveiller et ❌ régression, avec entre parenthèses l'écart du temps *application par page* à la référence ; ❌ échec : la génération n'a pas abouti ; case vide : scénario non joué. Toutes les mesures (pages, phases *Wikipédia*, *Application*, *Transfert*, *Total*, écart) sont dans [benchmark-results.csv](benchmark-results.csv), une ligne par scénario et par passage.",
    },
    "en": {
        "header": ("Version", "Date", "Target", "Level"),
        "new": '<span class="bench-new">new</span>',
        "failure": "❌ failed",
        "legend": "One row per run, one column per scenario. ✅ ok; <span class=\"bench-new\">new</span>: first run of the scenario, no reference yet; ⚠️ to watch and ❌ regression, with in brackets the gap of the *application per page* time to the reference; ❌ failed: the generation did not complete; empty cell: scenario not run. Every measurement (pages, *Wikipedia*, *Application*, *Transfer*, *Total* phases, gap) is in [benchmark-results.csv](benchmark-results.csv), one row per scenario and per run.",
    },
}


def read_rows(text: str) -> list[dict]:
    rows = list(csv.DictReader(io.StringIO(text)))
    for row in rows:
        if row["verdict"] not in VERDICTS:
            raise ValueError(f"verdict inconnu dans benchmark-results.csv : {row['verdict']!r}")
        if row["scenario"] not in SCENARIOS:
            raise ValueError(f"scénario inconnu dans benchmark-results.csv : {row['scenario']!r}")
    return rows


def passages(rows: list[dict]) -> list[tuple[tuple[str, str, str, str], dict[str, dict]]]:
    grouped: list[tuple[tuple[str, str, str, str], dict[str, dict]]] = []
    for row in rows:
        key = (row["version"], row["date"], row["target"], row["level"])
        if not grouped or grouped[-1][0] != key or row["scenario"] in grouped[-1][1]:
            grouped.append((key, {}))
        grouped[-1][1][row["scenario"]] = row
    return grouped


def percent(value: str, lang: str) -> str:
    number = int(round(float(value)))
    sign = "+" if number > 0 else "−" if number < 0 else ""
    return f"{sign}{abs(number)} %" if lang == "fr" else f"{sign}{abs(number)}%"


def cell(row: dict | None, lang: str) -> str:
    if row is None:
        return ""
    verdict = row["verdict"]
    if verdict == "ok":
        return "✅"
    if verdict == "new":
        return TEXT[lang]["new"]
    if verdict == "failure":
        return TEXT[lang]["failure"]
    mark = "⚠️" if verdict == "watch" else "❌"
    return f"{mark} ({percent(row['app_per_page_delta_pct'], lang)})" if row["app_per_page_delta_pct"] else mark


def table(rows: list[dict], lang: str) -> str:
    index = 0 if lang == "fr" else 1
    scenarios = [name for name in SCENARIOS if any(row["scenario"] == name for row in rows)]
    lines = [
        "| " + " | ".join([*TEXT[lang]["header"], *(SCENARIOS[name][index] for name in scenarios)]) + " |",
        "|" + "---|" * (4 + len(scenarios)),
    ]
    for (version, date, target, level), results in passages(rows):
        level_text = LEVELS.get(level, (level, level))[index]
        lines.append("| " + " | ".join([version, date, target, level_text, *(cell(results.get(name), lang) for name in scenarios)]) + " |")
    return "\n".join(lines)


def block(rows: list[dict], lang: str) -> str:
    body = "\n".join("  " + line for line in table(rows, lang).split("\n"))
    return f"  {START}\n{body}\n\n  {TEXT[lang]['legend']}\n  {END}"


def update_spec(text: str, lang: str, rows: list[dict]) -> str:
    crlf = "\r\n" in text
    text = text.replace("\r\n", "\n")
    start = text.index("  " + START)
    end = text.index(END, start) + len(END)
    text = text[:start] + block(rows, lang) + text[end:]
    return text.replace("\n", "\r\n") if crlf else text


def main() -> int:
    rows = read_rows(CSV_PATH.read_text(encoding="utf-8"))
    for lang, path in SPECS.items():
        original = path.read_bytes().decode("utf-8")
        path.write_bytes(update_spec(original, lang, rows).encode("utf-8"))
    print(f"{len(rows)} mesures, {len(passages(rows))} passages")
    return 0


if __name__ == "__main__":
    sys.exit(main())
