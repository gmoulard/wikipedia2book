#!/bin/bash
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

set -uo pipefail
cd "$(dirname "$0")/.." || exit 1

mode=${1:?usage: update-stats.sh daily|deploy}
status=0
git config user.name "github-actions[bot]"
git config user.email "41898282+github-actions[bot]@users.noreply.github.com"

if [ "$mode" = daily ]; then
  python3 scripts/toolviews_stats.py docs/toolviews.csv || status=1
fi

capture=$(mktemp)
if ssh -i ~/.ssh/toolforge -o IdentitiesOnly=yes -o BatchMode=yes -o ServerAliveInterval=30 \
    gm474d6f756c617264@login.toolforge.org "become wikipedia2book bash -s" \
    < scripts/toolforge-hourly.sh > "$capture"; then
  python3 scripts/toolforge_hourly.py docs/toolforge_hourly.csv "$capture" --generations docs/toolforge_generations.csv || status=1
else
  echo "::error::Relevé horaire impossible : journaux du webservice Toolforge inaccessibles"
  status=1
fi

python3 scripts/toolviews_chart.py docs/toolviews.csv docs/stats.md --hourly docs/toolforge_hourly.csv --generations docs/toolforge_generations.csv || status=1

files="docs/toolviews.csv docs/stats.md"
[ -f docs/toolforge_hourly.csv ] && files="$files docs/toolforge_hourly.csv"
[ -f docs/toolforge_generations.csv ] && files="$files docs/toolforge_generations.csv"
git add -- $files
if git diff --cached --quiet; then
  echo "Aucun changement"
  exit $status
fi
git commit -q -m "stats: $mode $(date -u '+%F %H:%M') UTC"
for attempt in 1 2 3; do
  if git fetch -q origin main && git rebase -q origin/main && git push -q origin HEAD:main; then
    exit $status
  fi
  sleep $((attempt * 5))
done
echo "::error::Impossible de pousser les statistiques sur main"
exit 1
