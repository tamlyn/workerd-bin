#!/bin/bash
set -euo pipefail

cd "$(dirname "$0")/.."
rm -rf dist

for asset in \
    workerd-darwin-64.gz \
    workerd-darwin-arm64.gz \
    workerd-linux-64.gz \
    workerd-linux-arm64.gz
do
    WORKERD_ASSET=$asset uv build --wheel
done
