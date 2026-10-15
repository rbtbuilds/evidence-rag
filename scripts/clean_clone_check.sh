#!/usr/bin/env bash
set -eu
task_root="$(cd "$(dirname "$0")/.." && pwd)"
export PATH="$task_root/.runtime/toolchain/node_modules/.bin:$PATH"
export PLAYWRIGHT_BROWSERS_PATH="$task_root/.runtime/ms-playwright"
mkdir -p "$task_root/.runtime"
task_tmp="$(mktemp -d "$task_root/.runtime/clean-clone.XXXXXX")"
cleanup() {
  case "$task_tmp" in
    "$task_root"/.runtime/clean-clone.*) rm -rf -- "$task_tmp" ;;
    *) return 1 ;;
  esac
}
trap cleanup EXIT
git clone --no-hardlinks "$task_root" "$task_tmp/repository"
cd "$task_tmp/repository"
export UV_CACHE_DIR="$PWD/.runtime/uv-cache"
export npm_config_cache="$PWD/.runtime/npm-cache"
unset EVIDENCE_HOME EVIDENCE_PROFILE
uv sync --frozen
npm --prefix web ci
uv run evidence-rag init > /dev/null
uv run evidence-rag seed-fixtures
./scripts/check.sh
npm --prefix web run test:e2e
uv run evidence-rag evaluate --profile fixture --split test --generation extractive --output .runtime/clean-evaluation
printf '\nClean clone verification passed at %s on ports 8115/5115.\n' "$(git rev-parse HEAD)"
