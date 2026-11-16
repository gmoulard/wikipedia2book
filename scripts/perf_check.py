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
import io
import json
import os
import platform
import statistics
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SCENARIOS = ROOT / "perf" / "scenarios.json"
REFERENCE = ROOT / "perf" / "reference.json"
METRICS = ("total_s", "wikipedia_s", "app_s", "transfer_s")
DOWNLOAD_CODES = {"fetch_image", "fetch_article", "prepare_document"}
WATCH = 0.50
REGRESSION = 1.00
PAGES_DRIFT = 0.05
RETRY_PAUSE_S = 60


class GenerationError(RuntimeError):
    pass


def book_from_json(path):
    payload = json.loads((ROOT.parent / path).read_text(encoding="utf-8"))
    if isinstance(payload, dict) and payload.get("format") == "wikipedia2book-workspace":
        payload = payload["projects"]
    return payload[0] if isinstance(payload, list) else payload


def project(name, scenario, language):
    if "json_file" in scenario:
        body = book_from_json(scenario["json_file"])
        body.update(scenario.get("options", {}))
        return body
    titles = scenario["articles"]
    articles = [
        {"title": title, "language": language, "selected": True,
         "url": f"https://{language}.wikipedia.org/wiki/" + urllib.parse.quote(title.replace(" ", "_"))}
        for title in titles
    ]
    body = {"name": f"perf {name}", "book_title": f"Atelier de performance : {name}", "main_articles": articles}
    count = scenario.get("chapters", 0)
    if count:
        keys = [f"{language}:title:{title.lower()}" for title in titles]
        size = -(-len(keys) // count)
        body["chapters"] = [
            {"title": f"Chapitre {index + 1}", "article_keys": keys[start:start + size]}
            for index, start in enumerate(range(0, len(keys), size))
        ]
    body.update(scenario.get("options", {}))
    return body


def generate(base_url, body, language, timeout=900, save_to=None):
    request = urllib.request.Request(
        f"{base_url.rstrip('/')}/api/pdf/stream?language={language}",
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json", "User-Agent": "Wikipedia2Book-perf/1.0"},
        method="POST",
    )
    start = time.perf_counter()
    downloads_done = None
    with urllib.request.urlopen(request, timeout=timeout) as response:
        while True:
            line = response.readline()
            if not line:
                raise GenerationError("flux interrompu avant la fin de la génération")
            event = json.loads(line)
            if event.get("type") == "error":
                raise GenerationError(event.get("detail", "erreur inconnue"))
            if event.get("type") == "progress" and event.get("code") not in DOWNLOAD_CODES and downloads_done is None:
                downloads_done = time.perf_counter()
            if event.get("type") == "done":
                done = time.perf_counter()
                pdf = response.read(event["size"])
                end = time.perf_counter()
                break
    if len(pdf) != event["size"] or pdf[:5] != b"%PDF-":
        raise GenerationError("PDF incomplet ou invalide")
    if save_to is not None:
        save_to.parent.mkdir(parents=True, exist_ok=True)
        save_to.write_bytes(pdf)
    downloads_done = downloads_done or done
    return {
        "total_s": end - start,
        "wikipedia_s": downloads_done - start,
        "app_s": done - downloads_done,
        "transfer_s": end - done,
        "pages": count_pages(pdf),
        "size_bytes": len(pdf),
    }


def count_pages(pdf):
    from pypdf import PdfReader
    return len(PdfReader(io.BytesIO(pdf)).pages)


def median_run(runs):
    result = {metric: round(statistics.median(run[metric] for run in runs), 2) for metric in METRICS}
    result["pages"] = runs[-1]["pages"]
    result["size_bytes"] = runs[-1]["size_bytes"]
    result["runs"] = len(runs)
    return result


def divergence(value, reference):
    if not reference:
        return None
    return (value - reference) / reference


def verdict(measure, reference):
    if reference is None:
        return "nouveau", []
    notes = []
    pages_change = divergence(measure["pages"], reference["pages"])
    if pages_change is not None and abs(pages_change) > PAGES_DRIFT:
        notes.append(f"pages {reference['pages']} → {measure['pages']} : contenu Wikipédia modifié, temps moins comparables")
    app = divergence(measure["app_s"] / measure["pages"], reference["app_s"] / reference["pages"])
    if app is not None and app > REGRESSION:
        return "régression", notes
    if app is not None and app > WATCH:
        return "à surveiller", notes
    return "ok", notes


def percent(value):
    return "—" if value is None else f"{value:+.0%}"


def report(level, base_url, measures, reference, failures):
    lines = [
        f"# Atelier de performance ({level})",
        "",
        f"Cible : `{base_url}` — {datetime.now(timezone.utc):%Y-%m-%d %H:%M} UTC",
    ]
    if reference:
        lines.append(f"Référence : {reference['created']} ({reference['environment']['label']})")
    lines += [
        "",
        "| Scénario | Pages | Total (s) | Wikipédia (s) | Application (s) | Transfert (s) | Écart application / page | Écart total | Verdict |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    notes = []
    verdicts = {}
    for name, measure in measures.items():
        ref = (reference or {}).get("scenarios", {}).get(name)
        result, scenario_notes = verdict(measure, ref)
        verdicts[name] = result
        notes += [f"- {name} : {note}" for note in scenario_notes]
        app_change = divergence(measure["app_s"] / measure["pages"], ref["app_s"] / ref["pages"]) if ref else None
        total_change = divergence(measure["total_s"], ref["total_s"]) if ref else None
        lines.append(
            f"| {name} | {measure['pages']} | {measure['total_s']} | {measure['wikipedia_s']} | {measure['app_s']} "
            f"| {measure['transfer_s']} | {percent(app_change)} | {percent(total_change)} | {result} |"
        )
    for name, error in failures.items():
        verdicts[name] = "échec"
        lines.append(f"| {name} | — | — | — | — | — | — | — | échec |")
        notes.append(f"- {name} : {error}")
    lines += [
        "",
        f"Verdict sur le temps de l'application par page (hors Wikipédia) : ok jusqu'à +{WATCH:.0%}, "
        f"à surveiller jusqu'à +{REGRESSION:.0%}, régression au-delà. Médiane de plusieurs générations par scénario.",
    ]
    if notes:
        lines += ["", "Remarques :", *notes]
    return "\n".join(lines) + "\n", verdicts


def environment(label):
    return {"label": label, "python": platform.python_version(), "machine": platform.machine(), "cpus": os.cpu_count()}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://localhost:8000")
    parser.add_argument("--level", choices=("min", "max"), default="min")
    parser.add_argument("--repeat", type=int)
    parser.add_argument("--scenarios", type=Path, default=SCENARIOS)
    parser.add_argument("--reference", type=Path, default=REFERENCE)
    parser.add_argument("--save-reference", action="store_true")
    parser.add_argument("--environment", default=os.environ.get("PERF_ENVIRONMENT", platform.node()))
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()

    config = json.loads(args.scenarios.read_text(encoding="utf-8"))
    level = config["levels"][args.level]
    repeat = args.repeat or level["repeat"]
    language = config["language"]
    reference = json.loads(args.reference.read_text(encoding="utf-8")) if args.reference.exists() else None
    if reference and reference["environment"]["label"] != args.environment:
        print(f"Attention : référence mesurée sur « {reference['environment']['label']} », mesure sur « {args.environment} » : écarts indicatifs.", file=sys.stderr)

    measures, failures = {}, {}
    for name in level["scenarios"]:
        body = project(name, config["scenarios"][name], language)
        runs = []
        try:
            for attempt in range(repeat):
                try:
                    run = generate(args.base_url, body, language)
                except GenerationError as error:
                    if "Wikipédia" not in str(error):
                        raise
                    print(f"{name} #{attempt + 1} : {error} ; nouvelle tentative dans {RETRY_PAUSE_S} s", file=sys.stderr, flush=True)
                    time.sleep(RETRY_PAUSE_S)
                    run = generate(args.base_url, body, language)
                runs.append(run)
                print(f"{name} #{attempt + 1} : {run['pages']} pages, {run['total_s']:.1f} s (Wikipédia {run['wikipedia_s']:.1f} s, application {run['app_s']:.1f} s)", file=sys.stderr, flush=True)
            measures[name] = median_run(runs)
        except (GenerationError, urllib.error.URLError, TimeoutError, OSError, ValueError) as error:
            failures[name] = str(error)
            print(f"{name} : échec : {error}", file=sys.stderr, flush=True)

    text, verdicts = report(args.level, args.base_url, measures, reference, failures)
    print(text)
    if args.report:
        args.report.write_text(text, encoding="utf-8")
    if args.save_reference:
        if failures:
            print("Référence non enregistrée : des scénarios ont échoué.", file=sys.stderr)
            return 1
        saved = {"created": f"{datetime.now(timezone.utc):%Y-%m-%d}", "base_url": args.base_url,
                 "environment": environment(args.environment),
                 "scenarios": {**(reference or {}).get("scenarios", {}), **measures}}
        args.reference.write_text(json.dumps(saved, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"Référence enregistrée dans {args.reference}", file=sys.stderr)
    return 1 if failures or "régression" in verdicts.values() else 0


if __name__ == "__main__":
    sys.exit(main())
