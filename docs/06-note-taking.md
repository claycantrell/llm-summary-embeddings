# Structured Notes

Tools for capturing, organizing, and connecting your reading notes.

---

## nb

CLI notebook with notes, bookmarks, tagging, wiki-links, and built-in git sync. Good for quick capture.

### Install

**macOS:**
```bash
brew install nb
```

**Linux:**
```bash
brew install nb   # via linuxbrew
# or see https://xwmx.github.io/nb/ for other methods
```

### Examples

```bash
# Create a new note
nb add "Initial thoughts on cognitive augmentation taxonomy"

# Create a note with a specific filename
nb add --filename "lit-review-notes.md" "Literature review rough notes"

# Add tags
nb add "Transformer architecture overview" --tags ai,architecture,review

# List all notes
nb list

# Search notes by content
nb search "cognitive load"

# Search by tag
nb list --tags review

# Open a note in $EDITOR
nb edit 1
```

### How it connects

- Good for quick, timestamped capture during a reading session.
- Notes are stored as markdown files in `~/.nb/` with automatic git versioning.
- Complements the project-local `notes/` directory (see the template below) for more structured reading notes tied to specific papers.

---

## zk

Zettelkasten-style note-taking with markdown, wiki-links, and sqlite-powered search. Good for building a knowledge graph of interconnected ideas.

### Install

**macOS:**
```bash
brew install zk
```

**Linux:**
```bash
brew install zk   # via linuxbrew
# or see https://github.com/zk-org/zk for other methods
```

### Examples

```bash
# Initialize a zk notebook in the notes/ directory
cd notes/ && zk init

# Create a new note
zk new --title "Cognitive load theory and AI assistance"

# Create a linked note (references an existing note)
zk new --title "Working memory constraints" --link-to "cognitive-load-theory"

# List all notes
zk list

# Full-text search
zk list --match "spaced repetition"

# Find notes linking to a specific note
zk list --linked-by "cognitive-load-theory"

# Find orphan notes (not linked to/from anything)
zk list --orphan
```

### How it connects

- Use `zk` inside the `notes/` directory to build a web of interconnected research ideas.
- Wiki-links (`[[note-title]]`) let you trace conceptual relationships across papers.
- The sqlite index enables fast full-text search even with hundreds of notes.

---

## Reading note template

This scaffold includes a template at `templates/note.md` for structured paper reading notes:

```markdown
# {{PAPER_TITLE}}

**Date:** {{DATE}}
**DOI:** {{DOI}}
**Tags:**

## Summary

## Key Findings
-

## Methodology
-

## Relevance to My Research

## Key Quotes
>

## Questions / Follow-ups
-

## References to Chase
-
```

### Makefile shortcut

```bash
make new-note TITLE="Attention Is All You Need"
```

Creates a timestamped note file in `notes/` (e.g., `notes/2026-03-08-attention-is-all-you-need.md`) populated with the template sections. Fill in each section as you read the paper.

### How it connects

- The `notes/` directory is where all project-specific reading notes live.
- Notes reference papers by DOI and `[@citation-key]`, tying them back to `bibliography/references.bib`.
- The "References to Chase" section feeds your next round of `make search` queries.
- Use `make search-notes QUERY="..."` to search across all notes in the directory.
