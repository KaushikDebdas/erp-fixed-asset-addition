---
name: ui-exploration
description: Use when inspecting the running application via the Playwright MCP server to record locators in the element catalog — defines the exploration procedure, scope discipline (map only the current flow), and evidence capture.
---

# Skill: UI Exploration (Playwright MCP)

## Procedure
0. Read the screen's `automation/element_catalog/<page-name>.md` first and
   reuse every `VERIFIED` locator; inspect only what is missing or changed.
1. Open `BASE_URL` from `.env`.
2. Log in using `ERP_USERNAME`/`ERP_PASSWORD` from `.env` — never
   hardcode, never print these. For an end-to-end flow needing multiple
   roles, log in as each role in its own browser context.
3. Navigate to only the page(s) the current step needs.
4. For each business step, find the corresponding UI element.
5. Verify the element resolves uniquely before recording it. Prefer a
   targeted look (`browser_find`, or `browser_evaluate` on one form) over a
   full-page `browser_snapshot`; take a full snapshot only for a screen that
   has no catalog file yet.
6. Capture evidence only when it is new: a screenshot if the screen has no file
   in `element_catalog/evidence/` or a locator was added or changed, otherwise
   a short DOM snippet. If the catalog entry is `VERIFIED` and unchanged, reuse
   it — no new screenshot, no full snapshot.
7. Write or update the catalog file
   `automation/element_catalog/<page-name>.md` (template:
   `templates/element_catalog_template.md`) for every page visited, with the
   screenshot in `element_catalog/evidence/` and a status of `VERIFIED` or
   `LOCATOR_REQUIRES_REVIEW` per element. Hand off to the Automation
   Engineer agent only after the user has checked the catalog.

## Scope discipline
Never crawl/inspect the entire application "just in case." Map one
flow's pages at a time, role by role, matched exactly to what's being
automated right now.

## Shared components
Inspect and map a component that appears across many pages (nav bar,
common modal) once, record it once in its own catalog file, and
reference that file from every page's catalog instead of re-inspecting it.

## Evidence
Every mapped locator should have evidence attached so a human reviewing a
`LOCATOR_REQUIRES_REVIEW` item can verify quickly without re-running the
exploration.
