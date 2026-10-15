#!/usr/bin/env bash
set -eu
cd "$(dirname "$0")/.."
export PATH="$PWD/.runtime/toolchain/node_modules/.bin:$PATH"
export UV_CACHE_DIR="$PWD/.runtime/uv-cache"
uv run ruff check .
uv run pyright
uv run pytest -m 'not real_model'
npm --prefix web run typecheck
npm --prefix web run test -- --run
npm --prefix web run build
