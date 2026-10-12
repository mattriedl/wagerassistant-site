#!/usr/bin/env bash
# SYNC.sh — sync deployable files from the source workspace into this repo and push.
# The GitHub token is read at runtime from the secrets file; it is NEVER stored here.
set -euo pipefail

SRC="/home/ubuntu/betting_calculators"
DST="/home/ubuntu/wagerassistant-site"
SECRETS="/home/ubuntu/.config/abacusai_auth_secrets.json"
REPO="mattriedl/wagerassistant-site"
BRANCH="main"

cd "$DST"

# --- rsync deployable files (same excludes as initial deploy) ---
rsync -a --delete \
  --exclude='.git/' \
  --exclude='SYNC.sh' \
  --exclude='.gitignore' \
  --exclude='README.md' \
  "$SRC"/*.html "$DST"/
rsync -a "$SRC"/styles.css "$SRC"/nav.js "$SRC"/sitemap.xml "$SRC"/sitemap.html \
  "$SRC"/robots.txt "$SRC"/site.webmanifest "$DST"/ 2>/dev/null || true
# favicons / images / IndexNow key
for f in favicon.ico favicon.svg apple-touch-icon.png og-image.png; do
  [ -f "$SRC/$f" ] && cp "$SRC/$f" "$DST"/ || true
done
cp "$SRC"/*.txt "$DST"/ 2>/dev/null || true
# blog (mirror, delete removed posts)
mkdir -p "$DST/blog"
rsync -a --delete "$SRC/blog/" "$DST/blog/"
# tools: scripts + the one allowed README; drop other docs
mkdir -p "$DST/tools"
rsync -a --delete \
  --exclude='*.pdf' --exclude='*.docx' \
  --include='README_BLOG_AUTOMATION.md' \
  --include='*.py' --include='_nav.html' \
  --exclude='*.md' \
  "$SRC/tools/" "$DST/tools/"

# --- commit & push ---
TOKEN="$(python3 -c "import json;print(json.load(open('$SECRETS'))['githubuser']['secrets']['access_token']['value'])")"
git add -A
if git diff --cached --quiet; then
  echo "No changes to sync."
  exit 0
fi
git commit -m "Automated sync: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
# push with token transiently in the URL, then reset remote to tokenless URL
git push "https://x-access-token:${TOKEN}@github.com/${REPO}.git" "$BRANCH"
git remote set-url origin "https://github.com/${REPO}.git"
echo "Sync complete."
