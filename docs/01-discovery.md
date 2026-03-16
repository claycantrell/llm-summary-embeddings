# Finding Papers

Tools for searching the academic literature from your terminal.

---

## semantic_bibtool

Convert paper titles into BibTeX entries via the Semantic Scholar API (200M+ papers).

### Install

```bash
pip install semantic_bibtool
```

### API Key (free)

Request at <https://www.semanticscholar.org/product/api#Partner-Form>, then add to `.env`:

```bash
export SEMANTIC_SCHOLAR_API_KEY="your-key-here"
```

### Examples

```bash
# Search by title, print BibTeX to stdout
semantic_bibtool "attention is all you need"

# Batch search from a file of titles (one per line)
semantic_bibtool sources/titles.txt -o bibliography/references.bib

# Include paper URLs in the BibTeX output
semantic_bibtool "cognitive enhancement and AI" --add-url -o bibliography/references.bib

# Append a single entry to your existing .bib
semantic_bibtool "deep learning for science" >> bibliography/references.bib
```

### Makefile shortcut

```bash
make search QUERY="cognitive augmentation"
```

Runs `semantic_bibtool` with the given query. Output goes to stdout; redirect or append to `bibliography/references.bib` as needed.

### How it connects

- Output feeds directly into `bibliography/references.bib`, which Pandoc reads during `make pdf` / `make docx`.
- Combine with `papis add --from doi` (see [05-reference-management.md](05-reference-management.md)) to store the full paper alongside metadata.

---

## semanticscholar (Python library)

Programmatic access to the Semantic Scholar API for deeper, filtered searches.

### Install

```bash
pip install semanticscholar
```

Uses the same `SEMANTIC_SCHOLAR_API_KEY` environment variable as `semantic_bibtool`.

### Examples

```python
from semanticscholar import SemanticScholar

sch = SemanticScholar()

# Basic search
results = sch.search_paper("nootropics cognitive performance", limit=10)
for p in results:
    print(f"[{p.year}] ({p.citationCount} cites) {p.title}")

# Filter by year
results = sch.search_paper("large language models", year="2023-2025", limit=20)

# Get full details for a known paper
paper = sch.get_paper("DOI:10.1145/3411764.3445243")
print(paper.title, paper.abstract)

# Find highly-cited papers on a topic
results = sch.search_paper("transformer architecture", limit=50)
top = sorted(results, key=lambda p: p.citationCount or 0, reverse=True)[:10]
for p in top:
    print(f"  {p.citationCount:>5} cites  {p.title}")
```

### Makefile shortcut

```bash
make search-py QUERY="cognitive augmentation"
```

Runs an inline Python script that prints the top 10 results with year and citation count.

### How it connects

- Use to explore a topic broadly before committing papers to your `papis` library.
- Once you identify relevant papers, grab their DOIs and run `make add-paper DOI="..."` or `make fetch-doi DOI="..."`.

---

## lixplore-cli

Scripted literature review pipelines -- batch queries and filtered searches in one command.

### Install

See the project repository for current install instructions (pip or direct clone).

### Examples

```bash
# Run a batch query file through the pipeline
lixplore-cli search --input queries.txt --output results.json

# Filter by field and date range
lixplore-cli search --query "AI cognitive augmentation" --from 2020 --to 2025

# Export results to CSV for further processing
lixplore-cli search --query "brain-computer interfaces" --format csv > results.csv
```

### How it connects

- Results can be fed into `semantic_bibtool` for BibTeX conversion.
- Useful as a first pass when you have many related subtopics to explore at once.
