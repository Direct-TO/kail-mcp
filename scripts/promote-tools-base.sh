#!/usr/bin/env sh
set -eu

SOURCE="${1:-rami-kali:latest}"
TARGET="${2:-rami-kali-tools:latest}"

docker image inspect "$SOURCE" >/dev/null
docker tag "$SOURCE" "$TARGET"

echo "Tagged $SOURCE as $TARGET"
