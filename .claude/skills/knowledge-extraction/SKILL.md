---
name: knowledge-extraction
description: Use when the Knowledge Curator ingests any domain reference material (PDF, DOCX, HTML, image, Markdown) dropped into projects/<project>/domain-docs/ — defines per-format extraction rules and the CONFIRMED/INFERRED merge procedure into knowledge/<domain>.md.
---

# Skill: Knowledge Extraction (multi-format)

Used by the Knowledge Curator agent to turn any reference document into
structured entries for `knowledge/<domain>.md`.

## Format-specific extraction
| Format | How to extract |
|---|---|
| PDF (text-based) | Direct text extraction, preserve section headings |
| PDF (scanned) | OCR first, then extract; flag low-confidence OCR text |
| DOCX | Extract text + heading structure; keep tables structured |
| HTML | Extract body content only; discard nav/ads/boilerplate |
| Image (screenshot, diagram, flowchart) | Describe what it shows in words; tag `INFERRED` by default |
| Markdown | Read directly |

## Entry format
```markdown
## <Topic / Screen / Workflow name>
- [CONFIRMED] <fact, with source file + section/page reference>
- [INFERRED] <fact reasonably implied but not stated outright>
```

## Merge procedure
1. Read the existing domain knowledge file (if any).
2. Extract new entries; skip duplicates, upgrade tags when a stronger
   source confirms something previously inferred.
3. Contradicts a `CONFIRMED` entry → add as `CONFLICT_NEEDS_REVIEW` with
   both versions/sources, never overwrite.
4. Never delete a `CONFIRMED` entry without explicit human approval.

## Rules
- Always cite the source file (and page/section, when possible).
- Image-derived business-rule facts should be flagged for human
  confirmation before being trusted for test case generation.
