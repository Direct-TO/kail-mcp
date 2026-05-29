#!/usr/bin/env sh
set -eu

SOURCE="${1:-kail-mcp:latest}"
TARGET="${2:-kail-mcp-tools:latest}"

docker image inspect "$SOURCE" >/dev/null
docker tag "$SOURCE" "$TARGET"

echo "Tagged $SOURCE as $TARGET"
