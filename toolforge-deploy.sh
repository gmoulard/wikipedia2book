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
