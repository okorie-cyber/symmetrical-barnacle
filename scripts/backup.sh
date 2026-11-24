#!/usr/bin/env bash
# Create a single-file backup of the whole repo (all branches and history).
# Restore with: git clone findable-YYYYMMDD.bundle findable
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
out="${1:-findable-$(date +%Y%m%d).bundle}"
git bundle create "$out" --all
git bundle verify "$out"
echo "Backup written to $out"
