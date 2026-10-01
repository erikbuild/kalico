#!/usr/bin/env bash
# ABOUTME: Runs a shell command inside Kalico's CI build image with the current directory mounted at /work.
# ABOUTME: Builds the image from scripts/Dockerfile-build (linux/amd64, as in CI) when it is missing.
set -euo pipefail

IMAGE=kalico-build
ROOT=$(cd "$(dirname "$0")/.." && pwd)

if [ "$#" -eq 0 ]; then
    echo "usage: $0 '<shell command>'" >&2
    exit 2
fi

if ! docker image inspect "$IMAGE" >/dev/null 2>&1; then
    docker build --platform linux/amd64 -f "$ROOT/scripts/Dockerfile-build" \
        -t "$IMAGE" "$ROOT"
fi

# The venv lives in a docker volume so it never collides with a host .venv
# DICTDIR keeps the image's /ci_build/dict; commands that build or read local
# dictionaries set DICTDIR=/work/dict themselves
exec docker run --rm --platform linux/amd64 \
    -v "$PWD":/work -w /work \
    -v kalico-build-venv:/venv -e UV_PROJECT_ENVIRONMENT=/venv \
    -v kalico-build-uv-cache:/root/.cache/uv -e UV_LINK_MODE=copy \
    --entrypoint /bin/bash "$IMAGE" -c "$*"
