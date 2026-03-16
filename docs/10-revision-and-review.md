# Revision and Review

Tools and templates for managing manuscript revisions, generating track-changes diffs, and responding to peer review.

## latexdiff — Track Changes Between Versions

**Install:** Included with most TeX distributions (`brew install --cask mactex` or `tlmgr install latexdiff`)

latexdiff generates a PDF highlighting additions, deletions, and modifications between two versions of a manuscript — similar to "Track Changes" in Word. Useful for co-author review and peer review submissions where reviewers expect to see what changed.

### Usage

```bash
make diff OLD="manuscript/draft-v1.md" NEW="manuscript/main.md"
```

This converts both Markdown files to LaTeX, runs latexdiff, and compiles the result to PDF. The output lands in `output/`.

### What the Output Shows

- **Blue underline** — added text
- **Red strikethrough** — deleted text
- Unchanged text appears normally

### Tips

- Save numbered snapshots before major revisions: copy `manuscript/main.md` to `manuscript/draft-v1.md` before starting a revision round.
- For peer review resubmission, generate the diff between the originally submitted version and the revised version. Many journals request this as a supplementary file.
- Git can also serve as your version history — compare any two commits without saving separate files:

```bash
git show HEAD~3:manuscript/main.md > /tmp/old-draft.md
make diff OLD="/tmp/old-draft.md" NEW="manuscript/main.md"
```

---

## pandoc-crossref — Automatic Cross-References

**Install:** `brew install pandoc-crossref`

pandoc-crossref auto-numbers figures, tables, equations, and sections in your manuscript. It is already integrated into the build pipeline — no extra configuration needed.

### Labeling Syntax

| Element | Syntax | Example |
|---|---|---|
| Figure | `{#fig:label}` | `![Caption](path.png){#fig:results}` |
| Table | `{#tbl:label}` | `: Caption {#tbl:summary}` |
| Equation | `{#eq:label}` | `$$ E = mc^2 $$ {#eq:einstein}` |
| Section | `{#sec:label}` | `## Methods {#sec:methods}` |

### Referencing

Use `@` followed by the label prefix and name:

```markdown
The results are shown in @fig:results.
Summary statistics appear in @tbl:summary.
From @eq:einstein, we derive the following.
As described in @sec:methods, we used a mixed-methods approach.
```

These render as "Figure 1", "Table 2", "Equation 3", "Section 4" (with correct numbering) in the final PDF.

### Multiple References

```markdown
See @fig:results and @fig:comparison.
```

Renders as: "See Figures 1 and 2."

### Numbering Behavior

- Figures, tables, and equations are numbered sequentially in order of appearance.
- If you reorder elements, numbers update automatically on the next build.
- Section references use the section number (e.g., "Section 2.1").

---

## Peer Review Response Template

**Location:** `templates/peer-review-response.md`

When you receive reviewer comments, use this template to write a structured point-by-point response.

### Workflow

1. Copy the template:

```bash
cp templates/peer-review-response.md manuscript/review-response-r1.md
```

2. Fill in the manuscript title, journal, and date.

3. For each reviewer comment:
   - Paste the exact comment in the blockquote (`> ...`).
   - Write your response explaining what you did and why.
   - Note specific changes with page and line numbers.

4. Add or remove reviewer/comment sections as needed — the template includes Reviewer 1 and Reviewer 2 as a starting point.

5. List all major changes in the "Summary of Changes" section at the end.

### Example Entry

```markdown
### Comment 1.1
> The authors do not adequately justify their choice of GPT-4
> over other large language models.

**Response:** We have expanded the justification in Section 3.1.
GPT-4 was selected because it was the only model with function-calling
support at the time of the study. We have also added a paragraph
discussing limitations of this choice and how results may differ
with other models.

**Changes made:** Added justification paragraph in Section 3.1
(page 7, lines 12-24). Added limitation discussion in Section 5
(page 15, lines 8-14).
```

### Generating a Diff for Reviewers

Pair the response letter with a latexdiff PDF so reviewers can verify your changes:

```bash
make diff OLD="manuscript/draft-submitted.md" NEW="manuscript/main.md"
```

Submit both the response letter and the diff PDF with your revision.
