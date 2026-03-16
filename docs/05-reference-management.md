# Managing Your Library

Deep dive into `papis`, the CLI reference and bibliography manager at the center of this scaffold.

---

## papis

Plain-text reference manager. Stores papers as YAML metadata + PDF files on your filesystem. Fully git-trackable, no GUI needed.

### Install

```bash
pip install papis
```

### Initial Config

Point papis at the `library/` directory inside this repo:

```bash
papis config --set dir ~/Documents/GitHub/cognitive-augmentation-ai-era/library
```

Or create `~/.config/papis/config` manually:

```ini
[settings]
default-library = research

[research]
dir = ~/Documents/GitHub/cognitive-augmentation-ai-era/library
```

### How papis stores data

Each paper gets its own folder containing plain-text metadata and the PDF:

```
library/
├── smith-2024-cognitive-enhancement/
│   ├── info.yaml    # metadata: title, authors, DOI, year, abstract, etc.
│   └── paper.pdf    # the actual paper
├── vaswani-2017-attention/
│   ├── info.yaml
│   └── paper.pdf
└── ...
```

The `info.yaml` file is human-readable and editable:

```yaml
title: "Cognitive Enhancement in the Age of AI"
author: "Smith, J. and Doe, A."
year: 2024
doi: "10.1234/example"
ref: "smith2024cognitive"
files:
  - paper.pdf
```

Everything is plain files, so `git diff` works naturally and the library travels with the repo.

### Examples

```bash
# Add a paper by DOI (downloads metadata automatically)
papis add --from doi 10.1038/s41586-020-2649-2

# Add a local PDF with manual metadata
papis add sources/paper.pdf \
  --set author "Smith, J." \
  --set title "Cognitive Enhancement" \
  --set year 2024

# Search your library
papis list
papis list --query "nootropics"

# Open a paper's PDF in your default viewer
papis open "cognitive enhancement"

# Edit metadata in $EDITOR
papis edit "smith 2024"

# Export the entire library to BibTeX
papis export --all --format bibtex > bibliography/references.bib

# Export a single entry
papis export --format bibtex "attention is all you need"
```

### Makefile shortcuts

```bash
# Add paper by DOI
make add-paper DOI="10.1038/s41586-020-2649-2"

# Add a local PDF
make add-pdf PDF="sources/paper.pdf"

# Export full library to bibliography/references.bib
make bib

# List all references
make list-refs
```

| Target | What it does | Output path |
|---|---|---|
| `make add-paper DOI="..."` | `papis add --from doi` | `library/<slug>/` |
| `make add-pdf PDF="..."` | `papis add <file>` | `library/<slug>/` |
| `make bib` | `papis export --all --format bibtex` | `bibliography/references.bib` |
| `make list-refs` | `papis list` | stdout |

### How it connects

- `make bib` regenerates `bibliography/references.bib`, which is the single source of truth for Pandoc citations.
- After running `make bib`, every `[@key]` reference in `manuscript/main.md` resolves automatically during `make pdf` / `make docx`.
- Papers stored in `library/` are git-tracked, so your reference collection is versioned alongside your manuscript.
- Combine with `make fetch-doi` or `make fetch-arxiv` to download the PDF first, then `make add-pdf` to import it with metadata.
