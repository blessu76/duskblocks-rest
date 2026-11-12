#!/bin/bash
# Green gate for duskblocks-rest — run before every commit. Exit 0 = green.
set -euo pipefail
cd "$(dirname "$0")/.."
echo "== 0/3 kit";   python3 scripts/kit_lock.py check
echo "== 1/3 unit tests"; python3 -m unittest discover -s tests -q
echo "== 2/3 build is up to date"
tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT
rsync -a --exclude='.git' ./ "$tmp/"
python3 "$tmp/scripts/build.py" >/dev/null 2>&1
for f in $(git ls-files '*.html' sitemap.xml | grep -v '^404.html$'); do
  cmp -s "$f" "$tmp/$f" || { echo "$f is stale — run: python3 scripts/build.py"; exit 1; }
done
echo "== 3/3 static site checks"; python3 scripts/check_site.py
echo "GREEN"
