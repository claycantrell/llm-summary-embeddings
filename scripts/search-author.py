#!/usr/bin/env python3
"""Search for papers by a specific author via Semantic Scholar."""

import sys

if len(sys.argv) < 2:
    print("Error: AUTHOR is required. Usage: python3 scripts/search-author.py \"Jane Smith\"")
    sys.exit(1)

author_name = sys.argv[1]

try:
    from semanticscholar import SemanticScholar
except ImportError:
    print("Error: semanticscholar not installed. Run: pip3 install semanticscholar")
    sys.exit(1)

sch = SemanticScholar()
authors = sch.search_author(author_name, limit=3)

if not authors:
    print(f"No authors found matching: {author_name}")
    sys.exit(0)

author = authors[0]
print(f"\n--- Papers by {author.name} ---")
print(f"    Affiliations: {author.affiliations}")
print(f"    h-index: {author.hIndex}, Total citations: {author.citationCount}\n")

papers = sch.get_author_papers(author.authorId, limit=20)
for p in papers:
    cites = p.citationCount if p.citationCount else 0
    year = p.year if p.year else "N/A"
    doi = ""
    if p.externalIds and "DOI" in p.externalIds:
        doi = f"  DOI: {p.externalIds['DOI']}"
    print(f"  [{year}] ({cites} cites) {p.title}{doi}")

print()
