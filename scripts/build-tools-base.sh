#!/usr/bin/env sh
set -eu

IMAGE="${1:-rami-kali-tools:latest}"

docker build --target tools-base -t "$IMAGE" .

echo "Built tool baseline image: $IMAGE"
