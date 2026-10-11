#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
bash ../../05-identity-delegation/code/scripts/check.sh
bash -n scripts/check.sh scripts/fault_check.sh
docker compose config --quiet
docker compose build checks
docker compose run --rm checks
if [[ "${1:-}" != --minimum ]]; then
  bash scripts/fault_check.sh
  bash ../../06-istio-workload-security/code/scripts/check.sh
fi