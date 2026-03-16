#!/usr/bin/env python3
"""Search for papers by topic via Semantic Scholar."""

import sys

if len(sys.argv) < 2:
    print("Error: QUERY is required. Usage: python3 scripts/search-papers.py \"your topic\"")
    sys.exit(1)

query = sys.argv[1]

try:
    from semanticscholar import SemanticScholar
except ImportError:
    print("Error: semanticscholar not installed. Run: pip3 install semanticscholar")
    sys.exit(1)

sch = SemanticScholar()
results = sch.search_paper(query, limit=10)

print(f"\n--- Results for: {query} ---\n")
for p in results:
    cites = p.citationCount if p.citationCount else 0
    year = p.year if p.year else "N/A"
    doi = ""
    if p.externalIds and "DOI" in p.externalIds:
        doi = f"  DOI: {p.externalIds['DOI']}"
    print(f"  [{year}] ({cites} cites) {p.title}{doi}")

print()
