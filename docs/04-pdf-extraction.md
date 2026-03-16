# Extracting Text from PDFs

Tools for converting PDFs into plain text for reading, searching, and processing.

---

## pdftotext (poppler)

Fast, simple text extraction. Handles most single-column academic papers well.

### Install

**macOS:**
```bash
brew install poppler
```

**Linux:**
```bash
sudo apt install poppler-utils
```

### Examples

```bash
# Extract to stdout
pdftotext sources/paper.pdf -

# Extract to a .txt file (same name, different extension)
pdftotext sources/paper.pdf sources/paper.txt

# Extract a specific page range (pages 3-7)
pdftotext -f 3 -l 7 sources/paper.pdf -

# Preserve layout (useful for tables)
pdftotext -layout sources/paper.pdf sources/paper.txt

# Extract and search for a term
pdftotext sources/paper.pdf - | grep -i "cognitive load"
```

### Makefile shortcuts

```bash
# Extract text from a single PDF (prints to stdout)
make extract-text PDF="sources/paper.pdf"

# Extract text from all PDFs in sources/
make extract-all
```

`make extract-text` runs `pdftotext` on the given PDF and streams output to stdout. `make extract-all` runs the `scripts/extract-all-text.sh` script, which processes every PDF in `sources/` and writes corresponding `.txt` files alongside them.

### How it connects

- Extracted text is useful for full-text search across your source papers.
- The `make identify-doi` target uses `pdftotext` internally to find DOIs embedded in PDFs.
- Plain text output can be piped into other tools or pasted into reading notes.

---

## pdfminer.six

Layout-aware extraction for complex PDFs -- multi-column layouts, embedded tables, and unusual formatting.

### Install

```bash
pip install pdfminer.six
```

No API key required.

### Examples

```bash
# Basic extraction (layout-aware by default)
pdf2txt.py sources/paper.pdf > sources/paper.txt

# Output as HTML (preserves some formatting)
pdf2txt.py -t html sources/paper.pdf > sources/paper.html

# Extract only pages 1-5
pdf2txt.py -p 1,2,3,4,5 sources/paper.pdf > sources/paper.txt

# Adjust character margin for better column detection
pdf2txt.py -M 2.0 sources/paper.pdf > sources/paper.txt
```

### When to use pdfminer instead of pdftotext

| Scenario | Use |
|---|---|
| Standard single-column paper | `pdftotext` (faster) |
| Two-column conference paper | `pdfminer.six` (better column handling) |
| Paper with complex tables | `pdfminer.six` (layout-aware) |
| Batch processing many PDFs | `pdftotext` (faster) |
| Need HTML output | `pdfminer.six` |

### How it connects

- Same workflow as `pdftotext`: output goes into `sources/` as `.txt` files for searching and note-taking.
- Particularly useful for ACM/IEEE-style two-column papers where `pdftotext` mangles the column order.
- The `requirements.txt` includes `pdfminer.six` so it is installed automatically by `setup.sh`.
