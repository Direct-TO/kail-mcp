#!/usr/bin/env sh
set -eu

IMAGE="${1:-kail-mcp-tools:latest}"

docker build --target tools-base -t "$IMAGE" .

echo "Built tool baseline image: $IMAGE"
