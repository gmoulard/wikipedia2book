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
import json
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from perf_check import GenerationError, generate, project

USER_AGENT = "Wikipedia2Book-limit/1.0 (https://github.com/gmoulard/wikipedia2book)"
DEFAULT_STEPS = (25, 50, 100, 200, 400, 800)


def source_titles(page, language, count):
    titles = []
    # NE PAS revenir à prop=links : il renvoie aussi les liens rouges (pages inexistantes), dont Wikipédia ne peut pas produire le PDF, et le test échoue sans avoir atteint la limite du serveur.
    params = {"action": "query", "format": "json", "formatversion": 2, "generator": "links", "titles": page,
              "gplnamespace": 0, "gpllimit": "max", "prop": "info"}
    while len(titles) < count:
        url = f"https://{language}.wikipedia.org/w/api.php?" + urllib.parse.urlencode(params)
        request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(request, timeout=60) as response:
            data = json.load(response)
        titles += sorted(linked["title"] for linked in data.get("query", {}).get("pages", []) if not linked.get("missing"))
        if "continue" not in data:
            break
        params.update(data["continue"])
        time.sleep(1)
    if len(titles) < count:
        raise SystemExit(f"« {page} » ne contient que {len(titles)} liens, {count} demandés")
    return titles[:count]


def run(base_url, steps, titles, language, generator=generate):
    results = []
    for count in steps:
        body = project(f"{count} articles", {"articles": titles[:count]}, language)
        start = time.perf_counter()
        try:
            measure = generator(base_url, body, language, timeout=3600)
        except (GenerationError, OSError, ValueError) as error:
            results.append({"articles": count, "error": f"{type(error).__name__}: {error}", "after_s": round(time.perf_counter() - start, 1)})
            break
        results.append({"articles": count, **{key: round(value, 1) if isinstance(value, float) else value for key, value in measure.items()}})
    return results


def report(results):
    lines = ["| Articles | Pages | Taille | Wikipédia | Application | Transfert | Total | Résultat |",
             "|---|---|---|---|---|---|---|---|"]
    for result in results:
        if "error" in result:
            lines.append(f"| {result['articles']} | — | — | — | — | — | {result['after_s']} s | échec : {result['error']} |")
        else:
            lines.append(f"| {result['articles']} | {result['pages']} | {result['size_bytes'] / 1e6:.1f} Mo | {result['wikipedia_s']} s | "
                         f"{result['app_s']} s | {result['transfer_s']} s | {result['total_s']} s | ok |")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Génère des livres de plus en plus gros jusqu'au premier échec.")
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--language", default="fr")
    parser.add_argument("--source-page", default="France")
    parser.add_argument("--steps", default=",".join(map(str, DEFAULT_STEPS)))
    args = parser.parse_args()
    steps = [int(step) for step in args.steps.split(",")]
    titles = source_titles(args.source_page, args.language, max(steps))
    results = run(args.base_url, steps, titles, args.language)
    print(report(results))
    print(json.dumps(results, ensure_ascii=False))


if __name__ == "__main__":
    main()
