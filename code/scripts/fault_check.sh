#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
source_file="$PWD/scripts/policy_outage.py"
pushd ../../05-identity-delegation/code >/dev/null
docker compose config --format json | python3 -c 'import json, sys; assert "--db=dev-file" in json.load(sys.stdin)["services"]["keycloak"]["command"]'
docker compose restart keycloak
docker compose up -d --wait keycloak
docker compose --profile tools run --rm --no-deps smoke
trap 'docker compose up -d --wait opa' EXIT
docker compose stop opa
docker compose --profile tools run --rm --no-deps -v "$source_file:/policy_outage.py:ro" smoke python /policy_outage.py denied
docker compose up -d --wait opa
docker compose --profile tools run --rm --no-deps -v "$source_file:/policy_outage.py:ro" smoke python /policy_outage.py recovery
trap - EXIT
popd >/dev/null