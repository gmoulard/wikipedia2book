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

set -euo pipefail

pods=$(kubectl get pods --field-selector=status.phase=Running \
  -o jsonpath='{range .items[*]}{.metadata.name}{"\n"}{end}' | grep '^wikipedia2book-' || true)
if [ -z "$pods" ]; then
  echo "aucun pod du webservice wikipedia2book en cours d'exécution" >&2
  exit 1
fi

echo "BEGIN-HOURLY"
for pod in $pods; do
  kubectl logs --timestamps "$pod" \
    | awk -v pod="$pod" '/"[A-Z]+ [^"]* HTTP\/[0-9.]+" [0-9][0-9][0-9]/ && !/"[A-Z]+ \/api\/stats\/hourly[ ?]/ { print pod ";" substr($1, 1, 13) }' \
    | sort | uniq -c | awk '{ print $2 ";" $1 }'
done
echo "END-HOURLY"

echo "BEGIN-GENERATIONS"
{
  for pod in $pods; do
    kubectl logs --timestamps "$pod" \
      | awk -v pod="$pod" '$2 == "{\"generation\":" && match($0, /"status": "(done|error|aborted)"/) { s = substr($0, RSTART + 11, RLENGTH - 12); print pod ";" substr($1, 1, 13) ";" s }' \
      | sort | uniq -c | awk '{ print $2 ";" $1 }'
  done
  if [ -d "${GENERATIONS_DIR:-$HOME/generations}" ]; then
    find "${GENERATIONS_DIR:-$HOME/generations}" -maxdepth 1 -name '????-??-??.jsonl' -exec cat {} + \
      | awk '{
          if (!match($0, /^\{"at": "[0-9T:-]+/)) next
          at = substr($0, 9, 13)
          if (!match($0, /"pod": "wikipedia2book-[A-Za-z0-9-]+"/)) next
          pod = substr($0, RSTART + 8, RLENGTH - 9)
          if (!match($0, /"generation": [0-9]+, "status": "(done|error|aborted)"/)) next
          s = substr($0, RSTART, RLENGTH); sub(/.*"status": "/, "", s); sub(/"$/, "", s)
          print pod ";" at ";" s
        }' \
      | sort | uniq -c | awk '{ print $2 ";" $1 }'
  fi
} | awk -F';' '{ key = $1 ";" $2 ";" $3; if ($4 > best[key]) best[key] = $4 } END { for (key in best) print key ";" best[key] }' | sort
echo "END-GENERATIONS"
