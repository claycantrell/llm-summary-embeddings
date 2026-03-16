#!/usr/bin/env python3
"""Search for papers by topic via OpenAlex."""

import sys

if len(sys.argv) < 2:
    print("Error: QUERY is required. Usage: python3 scripts/search-openalex.py \"your topic\"")
    sys.exit(1)

query = sys.argv[1]

try:
    import pyalex
    from pyalex import Works
except ImportError:
    print("Error: pyalex not installed. Run: pip3 install pyalex")
    sys.exit(1)

pyalex.config.email = "user@example.com"
results = Works().search(query).get(per_page=10)

print(f"\n--- OpenAlex results for: {query} ---\n")
for w in results:
    year = w.get("publication_year", "N/A")
    cited = w.get("cited_by_count", 0)
    title = w.get("title", "Untitled")
    doi = w.get("doi", "")
    print(f"  [{year}] ({cited} cites) {title}")
    if doi:
        print(f"         DOI: {doi}")

print()
