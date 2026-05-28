#!/usr/bin/env sh
set -eu

ARCHIVE="${1:-rami-kali-image.tar.gz}"

gzip -dc "$ARCHIVE" | docker load

echo "Imported $ARCHIVE"
echo "Start without rebuilding: docker compose up -d"
echo "Fast rebuild app changes: docker compose -f docker-compose.yml -f docker-compose.fast.yml up -d --build --force-recreate"
