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
    | awk -v pod="$pod" '/"[A-Z]+ [^"]* HTTP\/[0-9.]+" [0-9][0-9][0-9]/ { print pod ";" substr($1, 1, 13) }' \
    | sort | uniq -c | awk '{ print $2 ";" $1 }'
done
echo "END-HOURLY"
