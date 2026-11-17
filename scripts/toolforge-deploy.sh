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

repo="https://github.com/gmoulard/wikipedia2book"
json_field() { python3 -c "import json,sys; d=json.load(sys.stdin); print(d$1)"; }

started=$(toolforge build start --detach --json --use-latest-versions --ref production-toolforge "$repo")
build=$(echo "$started" | json_field '["new_build"]["name"]')
commit=$(echo "$started" | json_field '["new_build"]["resolved_ref"]')
echo "build $build, commit $commit"

status=unknown
for _ in $(seq 1 60); do
  sleep 15
  status=$(toolforge build show "$build" --json | json_field '["build"]["status"]')
  echo "build: $status"
  case "$status" in
    running|pending|unknown) ;;
    *) break ;;
  esac
done
if [ "$status" != ok ]; then
  toolforge build logs "$build" | tail -60
  exit 1
fi

toolforge envvars create FONTCONFIG_FILE /workspace/toolforge-fonts.conf >/dev/null
toolforge envvars create GIT_COMMIT "$commit" >/dev/null
# NE PAS passer ces valeurs en argument de toolforge envvars create : les autres utilisateurs du bastion les verraient ; elles sont lues sur l'entrée standard. Une variable absente des secrets GitHub garde sa valeur sur Toolforge.
for name in WIKIPEDIA2BOOK_MONITOR_TOKEN WIKIPEDIA2BOOK_OAUTH_CLIENT_ID WIKIPEDIA2BOOK_OAUTH_CLIENT_SECRET; do
  if [ -n "${!name:-}" ]; then
    printf '%s' "${!name}" | toolforge envvars create "$name" >/dev/null
    echo "variable posée : $name"
  fi
done
wait_idle() {
  local token="${WIKIPEDIA2BOOK_MONITOR_TOKEN:-}"
  if [ -z "$token" ]; then
    token=$(toolforge envvars show WIKIPEDIA2BOOK_MONITOR_TOKEN --json 2>/dev/null | json_field '["envvar"]["value"]' || true)
  fi
  if [ -z "$token" ]; then
    echo "pas de jeton de supervision : redémarrage sans attendre la fin des générations"
    return
  fi
  for _ in $(seq 1 180); do
    count=$(printf 'Authorization: Bearer %s
' "$token" | curl -fsS -H @- https://wikipedia2book.toolforge.org/api/health/details | json_field '.get("generations_in_progress")' || echo inconnu)
    if [ "$count" = 0 ]; then
      echo "aucune génération en cours"
      return
    fi
    echo "générations en cours : $count, attente"
    sleep 10
  done
  echo "toujours des générations en cours après 30 min : redémarrage quand même"
}
wait_idle
toolforge webservice buildservice restart

for _ in $(seq 1 20); do
  sleep 10
  if curl -fsS https://wikipedia2book.toolforge.org/api/version | grep -q "\"commit\":\"$commit\""; then
    echo "déployé : $commit"
    exit 0
  fi
done
toolforge webservice logs | tail -50
echo "le webservice ne sert pas $commit"
exit 1
