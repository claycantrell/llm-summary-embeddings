#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SOURCES_DIR="$REPO_ROOT/sources"

if [ ! -d "$SOURCES_DIR" ]; then
  echo "Error: sources/ directory not found at $SOURCES_DIR" >&2
  exit 1
fi

extracted=0
skipped=0

shopt -s nullglob
pdf_files=("$SOURCES_DIR"/*.pdf)
shopt -u nullglob

if [ ${#pdf_files[@]} -eq 0 ]; then
  echo "No PDF files found in $SOURCES_DIR"
  exit 0
fi

for pdf in "${pdf_files[@]}"; do
  txt="${pdf%.pdf}.txt"
  basename_pdf="$(basename "$pdf")"

  if [ -f "$txt" ]; then
    skipped=$((skipped + 1))
    continue
  fi

  echo "Extracting: $basename_pdf"
  pdftotext "$pdf" "$txt"
  extracted=$((extracted + 1))
done

echo "Extracted $extracted files, skipped $skipped (already exist)"
