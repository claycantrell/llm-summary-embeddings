#!/usr/bin/env bash
set -euo pipefail

if [ $# -lt 1 ]; then
  echo "Usage: $0 path/to/refs.bib" >&2
  exit 1
fi

BIB_FILE="$1"

if [ ! -f "$BIB_FILE" ]; then
  echo "Error: file not found: $BIB_FILE" >&2
  exit 1
fi

if ! command -v papis &>/dev/null; then
  echo "Error: papis is not installed" >&2
  exit 1
fi

# Count entries
total="$(grep -c '^@' "$BIB_FILE" || true)"
echo "Found $total entries in $(basename "$BIB_FILE")"

imported=0
failed=0

# Split bib file into individual entries and import each one
# Uses awk to split on lines starting with @
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

awk '
  /^@/ {
    entry_num++
    file = sprintf("%s/entry_%04d.bib", tmp_dir, entry_num)
  }
  entry_num > 0 { print > file }
' tmp_dir="$tmp_dir" "$BIB_FILE"

for entry_file in "$tmp_dir"/entry_*.bib; do
  [ -f "$entry_file" ] || continue

  # Extract the citation key for display
  cite_key="$(grep -m1 '^@' "$entry_file" | sed 's/^@[a-zA-Z]*{//;s/,.*$//')"
  echo "Importing: $cite_key"

  if papis add --from bibtex "$entry_file" 2>/dev/null; then
    imported=$((imported + 1))
  else
    echo "  Warning: failed to import $cite_key" >&2
    failed=$((failed + 1))
  fi
done

echo "Done. Imported $imported/$total entries ($failed failed)"
