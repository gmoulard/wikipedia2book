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


def measure_one(base_url, count, titles, language, generator=generate, save_dir=None):
    body = project(f"{count} articles", {"articles": titles[:count]}, language)
    options = {"save_to": save_dir / f"limite-{count}-articles.pdf"} if save_dir else {}
    start = time.perf_counter()
    try:
        measure = generator(base_url, body, language, timeout=3600, **options)
    except (GenerationError, OSError, ValueError) as error:
        return {"articles": count, "error": f"{type(error).__name__}: {error}", "after_s": round(time.perf_counter() - start, 1)}
    return {"articles": count, **{key: round(value, 1) if isinstance(value, float) else value for key, value in measure.items()}}


def run(base_url, steps, titles, language, generator=generate, save_dir=None):
    results = []
    for count in steps:
        results.append(measure_one(base_url, count, titles, language, generator, save_dir))
        if "error" in results[-1]:
            break
    return results


def wait_for_server(base_url, opener=urllib.request.urlopen, sleep=time.sleep, timeout_s=600):
    # NE PAS enchaîner le palier suivant sans attendre : après un échec, la plateforme redémarre souvent le serveur, et le palier suivant échouerait aussitôt sans rien mesurer.
    waited = 0
    while waited < timeout_s:
        try:
            with opener(urllib.request.Request(base_url + "/api/version", headers={"User-Agent": USER_AGENT}), timeout=10):
                return
        except OSError:
            sleep(10)
            waited += 10
    raise SystemExit(f"{base_url} ne répond plus depuis {timeout_s} s")


def search(base_url, titles, language, start, precision, maximum, generator=generate, wait=wait_for_server, save_dir=None):
    results = []
    passed, failed, count = 0, None, start
    while True:
        results.append(measure_one(base_url, count, titles, language, generator, save_dir))
        if "error" in results[-1]:
            failed = count
            wait(base_url)
        else:
            passed = count
        if failed is None:
            if count >= maximum:
                break
            count = min(count * 2, maximum)
            continue
        middle = round((passed + failed) / 2 / precision) * precision
        if failed - passed <= precision or not passed < middle < failed:
            break
        count = middle
    return results, passed, failed


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


def summary(passed, failed, maximum):
    if failed is None:
        return f"Limite non atteinte : {passed} articles réussis (maximum demandé : {maximum})."
    if not passed:
        return f"Limite en dessous de {failed} articles : aucun palier réussi."
    return f"Limite entre {passed} articles (réussi) et {failed} articles (échec)."


def main():
    parser = argparse.ArgumentParser(description="Cherche la taille maximale d'un livre : paliers fixes jusqu'au premier échec, ou recherche par dichotomie.")
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--language", default="fr")
    parser.add_argument("--source-page", default="France")
    parser.add_argument("--steps", default=",".join(map(str, DEFAULT_STEPS)))
    parser.add_argument("--search", type=int, metavar="DEPART", help="dichotomie : double à partir de DEPART jusqu'au premier échec, puis coupe l'intervalle en deux")
    parser.add_argument("--precision", type=int, default=50)
    parser.add_argument("--max", type=int, default=2000, dest="maximum")
    parser.add_argument("--save-pdf", type=Path, metavar="DOSSIER", help="enregistre chaque PDF reçu dans DOSSIER (limite-<N>-articles.pdf), par exemple ./tmp, ignoré par git")
    args = parser.parse_args()
    if args.search:
        titles = source_titles(args.source_page, args.language, args.maximum)
        results, passed, failed = search(args.base_url, titles, args.language, args.search, args.precision, args.maximum, save_dir=args.save_pdf)
        print(report(results))
        print(summary(passed, failed, args.maximum))
    else:
        steps = [int(step) for step in args.steps.split(",")]
        titles = source_titles(args.source_page, args.language, max(steps))
        results = run(args.base_url, steps, titles, args.language, save_dir=args.save_pdf)
        print(report(results))
    print(json.dumps(results, ensure_ascii=False))


if __name__ == "__main__":
    main()
