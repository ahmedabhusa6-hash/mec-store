#!/bin/bash
# MEC-21: GitHub sync via isolated orphan-commit worktree
# - Whitelist = 94 remote files (current working-tree versions) + 9 new files
# - Single orphan commit -> force-push -> old secret-bearing history unreachable
# - Secret scan BEFORE push; abort if any hit
set -e

SRC=/home/z/my-project
WT=/tmp/mec21-gh
rm -rf "$WT"
mkdir -p "$WT"
cd "$WT"
git init -q
git config user.name "MEC Orchestrator"
git config user.email "mec@local"

# 1. copy whitelisted files (working-tree versions)
while IFS= read -r f; do
  if [ -f "$SRC/$f" ]; then
    mkdir -p "$(dirname "$f")"
    cp "$SRC/$f" "$f"
  else
    echo "WARN: remote file missing locally: $f"
  fi
done < /tmp/remote_files.txt

# 2. new files from MEC-21
NEW_FILES=(
  "prisma/migrations/20260928130000_product_aliases/migration.sql"
  "src/app/api/store/waitlist/route.ts"
  "src/app/sitemap.ts"
  "public/og-image.png"
  "public/icon.png"
  "public/apple-icon.png"
  "public/favicon.ico"
  "public/favicon-32.png"
)
for f in "${NEW_FILES[@]}"; do
  if [ -f "$SRC/$f" ]; then
    mkdir -p "$(dirname "$f")"
    cp "$SRC/$f" "$f"
    echo "NEW: $f"
  else
    echo "ERROR: expected new file missing: $f"; exit 1
  fi
done

# 3. secret scan (fail-closed)
echo "--- secret scan ---"
HITS=$(grep -rlE "ghp_[A-Za-z0-9]{20,}|sbp_v0_[A-Za-z0-9]{10,}|psk_[A-Za-z0-9]{10,}|fed3a37[A-Za-z0-9-]{10,}|mec_[A-Za-z0-9_-]{20,}|postgresql://[^\"' ]*:[^\"' ]*@.*password" . --include="*" 2>/dev/null | grep -v "^./.git/" || true)
if [ -n "$HITS" ]; then
  echo "SECRET SCAN FAILED — hits:"; echo "$HITS"; exit 1
fi
echo "secret scan clean"

# also scan for REAL key material (length-qualified patterns only — bare "psk_"
# appears in Arabic docs as a placeholder illustration, verified 2026-09-28)
if grep -rqE "psk_[A-Za-z0-9]{10,}" . --include="*.ts" --include="*.tsx" --include="*.json" --include="*.md" 2>/dev/null; then
  echo "REAL psk_ key material found:"; grep -rlE "psk_[A-Za-z0-9]{10,}" . --include="*.ts" --include="*.tsx" --include="*.json" 2>/dev/null; exit 1
fi

# 4. commit + push
git add -A
COUNT=$(git ls-files | wc -l)
echo "files in commit: $COUNT"
git commit -qm "MEC-21: security hardening + growth batch + Supabase migration 001

- Security: wallet phone-bearer hardening (no row creation, no ref leak, 20/min cap),
  live-mode sandbox fallthrough guard (G-B0), catalog stock depth -> availability tri-state,
  public /intel link removed from storefront
- Performance: Railway DATABASE_URL pgbouncer tax removed (6543->5432, limit 5),
  catalog ETag/304
- Growth/SEO: metadataBase + canonical + og:image/locale/url + twitter card,
  sitemap.xml, robots hardening, favicon.ico/apple-icon/icon.png, 1200x630 OG image,
  Arabic search aliases (37 products) + empty state, waitlist CTA on OOS cards,
  env-configurable support link, admin token rotated (was in old git history)
- Database: versioned migration 001 (Product.aliases) applied + verified on Supabase
- History: orphan commit — secret-bearing pre-MEC-20 history purged from main

Regression: 39 PASS / 0 FAIL / 1 SKIP (local prod build)
Verified: tsc 0 errors, eslint 0 errors, next build 20 routes"

# 5. push (force, orphan history)
source "$SRC/.env" 2>/dev/null || true
git push --force "https://x-access-token:${GITHUB_TOKEN}@github.com/ahmedabhusa6-hash/mec-store.git" HEAD:main 2>&1 | tail -3
echo "--- push done ---"
git log --oneline -1
echo "commit files: $COUNT"
