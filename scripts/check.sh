#!/usr/bin/env bash
set -eu
cd "$(dirname "$0")/.."
export PATH="$PWD/.runtime/toolchain/node_modules/.bin:$PATH"
export UV_CACHE_DIR="$PWD/.runtime/uv-cache"
export npm_config_cache="$PWD/.runtime/npm-cache"
node -e 'if(Number(process.versions.node.split(".")[0])!==24)throw new Error("Use Node 24 LTS on PATH; do not replace the global runtime.")'
uv run --no-sync ruff check .
uv run --no-sync pyright
uv run --no-sync pytest -m 'not real_model' --disable-socket --allow-unix-socket --allow-hosts=127.0.0.1,::1
npm --prefix web run typecheck
npm --prefix web run test -- --run
npm --prefix web run build
uv run --no-sync python scripts/check_contracts.py
uv run --no-sync evidence-rag validate-corpus > /dev/null
