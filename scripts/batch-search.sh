#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
QUERIES_FILE="${1:-$REPO_ROOT/scratch/queries.txt}"
BIB_FILE="$REPO_ROOT/bibliography/references.bib"

if [ ! -f "$QUERIES_FILE" ]; then
  echo "Error: queries file not found at $QUERIES_FILE" >&2
  echo "Usage: $0 [queries-file]" >&2
  exit 1
fi

mkdir -p "$(dirname "$BIB_FILE")"

# Ensure bib file exists
touch "$BIB_FILE"

count=0
total="$(wc -l < "$QUERIES_FILE" | tr -d ' ')"

while IFS= read -r query || [ -n "$query" ]; do
  # Skip empty lines and comments
  if [ -z "$query" ] || [[ "$query" == \#* ]]; then
    continue
  fi

  count=$((count + 1))
  echo "[$count/$total] Searching: $query"
  semantic_bibtool "$query" >> "$BIB_FILE" 2>/dev/null || echo "  Warning: search failed for '$query'" >&2
done < "$QUERIES_FILE"

# Deduplicate: remove entries with duplicate citation keys
# Keeps the first occurrence of each @type{key, line and its content
if [ -s "$BIB_FILE" ]; then
  tmp_file="$(mktemp)"
  awk '
    /^@[a-zA-Z]+\{[^,]+,/ {
      key = $0
      sub(/^@[a-zA-Z]+\{/, "", key)
      sub(/,.*$/, "", key)
      if (seen[key]) {
        skip = 1
        next
      }
      seen[key] = 1
      skip = 0
    }
    !skip { print }
  ' "$BIB_FILE" > "$tmp_file"
  mv "$tmp_file" "$BIB_FILE"
fi

echo "Done. Processed $count queries. Results in $BIB_FILE"
