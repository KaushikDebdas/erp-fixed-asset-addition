---
name: test-case-writing
description: Use whenever generating test cases or bug reports from a CR/SRS document, for any module. Defines the exact 11-column Excel schema and order, the Test Case Type taxonomy (Positive/Negative/Edge Case/Business/Out of Scope), coverage dimensions, the ~100-cases-per-story volume target, fixed defaults, and exact .xlsx formatting.
---

# Skill: Test Case Writing & Bug Report (Universal — use for ANY CR)

This is the one skill to use whenever generating test cases or bug
reports from a CR document, regardless of module. It is module-agnostic
by design. If the CR touches a module that has its own domain reference
file (`knowledge/<domain>.md`), read that too — this file defines HOW to
write cases; the domain file defines WHAT is true about the module.

---

## 1. Test Case Output

**File:** single `.xlsx`, one worksheet `Sheet1`, named
`Test_Case_<JIRA-ID>.xlsx`.

**Base columns, in this order (do not add, remove, or rename these
eleven):**
`Test Case Type` | `Story` | `Folder` | `Name` | `Precondition` | `Steps` |
`Test Data` | `Expected Result` | `Actual Result` | `Priority` | `Status`

**This framework appends three more columns after Status** —
`Automation Suitable` | `Automation Reason` | `Suite` — for automation
tracking only. They are not part of the ten-column Zephyr-bound standard;
delete them before uploading to Zephyr. See `CLAUDE.md` →
"Automation-tracking columns."

### Column Rules

- **Test Case Type** — one of: `Positive`, `Negative`, `Edge Case`,
  `Business`, `Out of Scope`. This is the single source of truth for what
  kind of case a row is — Folder is never used to encode this (see
  Folder rule below, which stays a plain feature path regardless of
  type).
  - **Positive** — the happy-path behavior of the feature.
  - **Negative** — invalid input, rejected actions, permission denials,
    blocked states.
  - **Edge Case** — boundary values, max-length, zero/blank, concurrent
    actions, unusual-but-valid states.
  - **Business** — accounting/voucher entries, calculations, workflow
    state/status transitions, financial/business-rule outcomes.
  - **Out of Scope** — verifies a stated out-of-scope item is NOT
    available.
- **Story** — story ID from the document (e.g. F01S01, F01S02). Omit only
  if the CR truly has no story numbering.
- **Folder** — taken directly from the feature's case path (e.g.
  "Accounting/Voucher/IOU", "Accounting/Voucher/Approval"), regardless of
  Test Case Type — a Negative or Edge Case row for a feature uses the
  same Folder value as that feature's Positive rows, never a `/Negative`
  or `/Edge Case` sub-path. Repeat the same Folder value on every row
  belonging to that feature. Keep all rows of one Folder grouped together
  (sorted by Test Case Type within the group for readability), following
  the document's section order. Exception: `Out of Scope` cases still use
  a single top-level `Out of Scope` value in Folder, since they aren't
  testing a built feature and have no feature path to belong to.
- **Name** — max 255 chars, precise, phrased `Verify` or `ensure <single
  specific behavior>`. Each row tests exactly ONE thing.
- **Precondition** — numbered multi-line list from that section's stated
  preconditions. Use the document's exact wording where given.
- **Steps** — numbered, multi-line, atomic UI actions naming the literal
  control:
  ```
  1. Login into ERP.
  2. Go to [Module] module.
  3. Click on [Section] and go to [Screen] page.
  4. Click on [exact button/field name] and enter [specific value].
  ```
  Literal control names, not generic phrasing — required so a case can be
  automated directly from Steps without guessing, and so a new reader
  understands exactly what to click.
- **Test Data** — login placeholder `<ERP Username> / <ERP Password>`
  plus the specific field value(s) driving this exact case, so Steps +
  Test Data alone differentiate every row.
- **Expected Result** — future tense, starts with `System should …`,
  concrete and checkable — never a vague "should work correctly."
- **Actual Result** — always `Works as expected`.
- **Priority** — always `High` unless you explicitly state a reason to
  deviate.
- **Status** — always `Approved`.

### Coverage Requirements (the most important part)

Do not write one case per requirement. Decompose every requirement and
acceptance criterion into many granular cases. For each relevant UI
element, field, column, button, filter, and rule, generate cases across:

- Presence/display, label & header text, position & ordering, alignment &
  layout
- Data accuracy (DB→UI mapping per record; blank/null when not
  applicable), persistence (survives refresh, logout/login), pagination
- Boundary/stability (max-length values, long names, system stays stable)
- Field validation (numeric-only, rejects negative, limit enforcement,
  read-only non-editable, defaults correctly, optional fields clearable,
  valid date format)
- Mock-up/Prototype review — every visible/functional element in attached
  mockups
- Button/action logic (enabled/disabled conditions exactly as stated),
  conditional behavior, validation/error handling
- Confirmation popups (exact title/message, both buttons, confirm and
  cancel paths)
- **Negative** — invalid/rejected/blocked path for every filter/search/
  rule/action, marked `Test Case Type = Negative`
- **Edge Cases** — boundary/max-length/zero-blank/concurrent/unusual-but-
  valid states, marked `Test Case Type = Edge Case`
- **Business-Oriented** — underlying business/domain outcome (accounting/
  voucher entries with correct Dr./Cr. accounts and amounts,
  calculations, workflow state transitions) — cross-reference the
  module's domain knowledge file rather than assuming values. Marked
  `Test Case Type = Business`
- **Out of Scope** — a case verifying each stated out-of-scope item is
  NOT available, marked `Test Case Type = Out of Scope` (Folder =
  `Out of Scope`)
- Regression (existing functionality unaffected), cross-functional
  (interactions with other features), cross-story (interactions between
  stories within the same CR)

Also ensure coverage for: functional validations, negative scenarios,
boundary value testing, API failure scenarios, state handling, duplicate
action prevention, multiple-user same-time actions, data consistency,
permission checks, session handling, invalid input handling, notification
validations, retry/recovery scenarios, performance-related risks, abuse/
spam behavior, and edge cases commonly missed in manual testing.

Think like a senior QA engineer working on a production system — consider
slow internet, duplicate clicks, stale UI, interrupted requests, invalid
states, and unexpected user actions.

### Volume Target

Aim for thoroughness comparable to a full manual QA pass — **at least 100
cases per story** where the story warrants it. For a multi-story CR,
target roughly `100 × number of stories` as a ceiling to aim toward,
scaled down for genuinely small stories. Never pad with duplicates — match
depth to actual requirement complexity.

### .xlsx Formatting

- Header row (row 1): bold, solid orange fill `FFC000`.
- Fix the top row/header row.
- Wrap text enabled on **all columns**, header and body — including the
  three appended automation-tracking columns.
- Multi-line Steps/Precondition as real line breaks within the cell, not
  separate rows.
- Column widths: Test Case Type 14, Story 12, Folder 44, Name 75,
  Precondition 45, Steps 45, Test Data 14, Expected Result 40,
  Actual Result 20, Priority 15, Status 18, Automation Suitable 16,
  Automation Reason 30, Suite 12.

### Process

1. If a module-specific domain knowledge file exists, read it first —
   don't invent domain rules/preconditions.
2. Read the entire CR: Scope, In Scope, Out of Scope, every numbered
   feature/story, Preconditions, Impacted Areas, Requirements (UI +
   Functional), Acceptance Criteria, Exceptions.
3. Cross-reference a separate Scope-of-Work checklist if provided, but the
   CR/SRS takes precedence when they conflict.
4. For a large CR, generate one Folder/story slice at a time (covering
   all Test Case Types for that slice — Positive, Negative, Edge Case,
   Business) and let it be reviewed before moving to the next slice.
5. Fill Automation Suitable/Reason/Suite per row as you go (see
   `CLAUDE.md`).
6. Build the `.xlsx` per the formatting rules above and present it.
7. After delivering, give a short summary: total case count and a
   per-Folder breakdown.

---

## 2. Bug Report Format

**Fields:** `Title` | `Steps to Reproduce` | `Actual Result` |
`Expected Result` | `Severity` | `Priority`

- **Title** — concise, specific (name the screen and exact control/
  behavior, not just "X not working").
- **Steps to Reproduce** — numbered, literal-action style, same as test
  case Steps, starting from a known state.
- **Actual Result** — exact observed message/behavior.
- **Expected Result** — what should happen instead, per the CR or domain
  rules.
- **Severity / Priority** — per team's standard scale (Critical/High/
  Medium/Low).

---

## 3. Communication Rule

Input may arrive in Banglish, Bengali, English, or mixed — interpret
intent without requiring an English rewrite. When the requested *output*
is a QA/BA artifact (test case, bug report, doc), always produce it in
professional English.
