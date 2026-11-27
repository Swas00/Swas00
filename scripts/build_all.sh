#!/usr/bin/env bash
# Rebuild every generated asset locally with live data.
#   GITHUB_TOKEN=$(gh auth token) ./scripts/build_all.sh
# (Without a token, set PREVIEW_DATA=1 for placeholder contribution numbers.)
set -euo pipefail
cd "$(dirname "$0")"
USER_NAME="${1:-Swas00}"
python3 banners.py      "$USER_NAME" ../assets
python3 architecture.py "$USER_NAME" ../assets/architecture.svg
python3 cluster.py      "$USER_NAME" ../assets/cluster.svg
python3 observe.py      "$USER_NAME" ../assets/observe.svg
python3 datacenter.py   "$USER_NAME" ../assets/datacenter.svg
python3 neural.py       "$USER_NAME" ../assets/neural.svg
python3 deploy.py       "$USER_NAME" ../assets/deploy.svg
python3 edge.py         "$USER_NAME" ../assets/edge.svg
python3 stack.py        ../assets/stack.svg
python3 explorer.py     "$USER_NAME" ../README.md
python3 preview.py      ../assets ../preview.html
