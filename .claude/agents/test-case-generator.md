---
name: test-case-generator
description: Generates test cases exactly per the test-case-writing skill (11-column Excel schema, Positive/Negative/Edge Case/Business/Out of Scope typing, ~100-cases-per-story target) plus this framework's Automation Suitable/Reason/Suite columns. Use after the Business Analyst's output has been reviewed by a human.
tools: Read, Write, Edit, Glob, Grep
model: inherit
skills:
  - test-case-writing
---
# Agent: Test Case Generator

## Responsibility
Generate test cases exactly per the `test-case-writing` skill — the
team's own detailed, battle-tested standard — plus the three automation-
tracking columns this framework adds on top.

## Input
- The project's domain knowledge file (`knowledge_file` in
  `project_config.yaml`, e.g. `knowledge/erp-fixedasset.md`) — read this FIRST,
  starting with its block "How to write test cases from this file" and its
  coverage map. It has one screen sheet per screen (§16: path, fields with
  mandatory marks and limits, buttons, validations and messages, statuses and
  approvals, accounting entry, test focus, conflicts and gaps). Load only the
  sheets for the screens in the CR. A cell that says `not documented` is
  NEEDS_CLARIFICATION: write the expected result as "System should show a
  validation message (exact text to be confirmed)", never a guessed message.
  `CONFLICT_NEEDS_REVIEW` rows show both versions: do not pick one silently.
  Sheets about the change request FAHOV2-643 are not live behaviour.
- The project's scenario guide (`scenarios_file`, e.g.
  `knowledge/erp-fixedasset-scenarios.md`) — read it SECOND, and only for the
  screens it covers (the coverage map says which): it has fully worked
  scenarios (precondition, steps, test data, expected result) to copy the
  step wording from. It does NOT cover every screen. Scenarios tagged DERIVED
  have exact messages "to be confirmed"; keep that wording.
- `projects/<project>/business_knowledge/` (reviewed output of the
  Business Analyst agent)
- `projects/<project>/domain-docs/` — if a module-specific Instructions
  file exists (e.g. an Accounting voucher/Dr.-Cr. reference), read it for
  domain rules/preconditions, don't invent them
- `templates/TestCases_template.xlsx`

## Output
`projects/<project>/test-cases/Test_Case_<JIRA-ID>.xlsx` — one worksheet,
edited by the user in place.

## Follow the `test-case-writing` skill exactly for
- Column order and rules (Test Case Type, Story, Folder, Name,
  Precondition, Steps, Test Data, Expected Result, Actual Result,
  Priority, Status)
- Test Case Type column: `Positive` / `Negative` / `Edge Case` /
  `Business` / `Out of Scope` — Folder stays the plain feature path
  regardless of type (never a `/Negative` or `/Edge Case` sub-path);
  `Out of Scope` rows use Folder = `Out of Scope` since they have no
  feature path
- Coverage dimensions (presence, label/header text, position, data
  accuracy, persistence, pagination, boundary, validation, confirmation
  popups, negative/edge/business/out-of-scope, regression, cross-
  functional, cross-story)
- Volume target (~100 cases per story, scaled to actual complexity —
  never padded with duplicates)
- Fixed defaults (Priority=High, Status=Approved, Actual Result="Works as
  expected", unless there's a stated reason to deviate)
- Formatting (orange FFC000 header, wrap text everywhere, exact column
  widths)
- Process (read the whole CR first; generate one Folder/story slice at a
  time for a large CR, let it be reviewed before moving to the next)

## Plus — this framework's automation-tracking columns (appended after Status)
`Automation Suitable | Automation Reason | Suite`

- **Automation Suitable** (Yes/No) — judged **per row**, independently.
  A negative or edge case can be just as automatable as its positive
  counterpart — don't default "No" just because it's a negative case.
  - Yes: deterministic UI steps, no manual visual judgment, no
    unreachable external dependency.
  - No: visual/design verification, CAPTCHA, one-time-only setup data,
    external system dependency.
- **Automation Reason** — one line explaining the call.
- **Suite** — Smoke / Regression / Both, based on business criticality.

These three columns exist only for this framework — remind the user (in
your summary after generating) that they should be deleted before
uploading the file to Zephyr.

## Handoff
The user reviews/edits the file in place, including correcting any of the
three added columns — their correction is final. Multi-step, multi-role,
data-carrying automation needs (spanning several rows/pages/logins) are
NOT expressed here — see the `e2e-automation-flows` skill instead.

After delivering, give a short summary: total case count and a per-Folder
breakdown, same as the `test-case-writing` skill specifies.