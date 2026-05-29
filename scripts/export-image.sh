#!/usr/bin/env sh
set -eu

OUT="${1:-kail-mcp-images.tar.gz}"
if [ "$#" -gt 0 ]; then
    shift
fi

if [ "$#" -eq 0 ]; then
    set -- kail-mcp:latest kail-mcp-tools:latest
fi

for image in "$@"; do
    docker image inspect "$image" >/dev/null
done

docker save "$@" | gzip -c > "$OUT"

echo "Exported $* to $OUT"
echo "Import on another machine with: sh scripts/import-image.sh $OUT"
