---
name: ui-exploration
description: Use when inspecting the running application via the Playwright MCP server to build an automation mapping — defines the exploration procedure, scope discipline (map only the current flow), and evidence capture.
---

# Skill: UI Exploration (Playwright MCP)

## Procedure
1. Open `BASE_URL` from `.env`.
2. Log in using `TEST_USERNAME`/`TEST_PASSWORD` from `.env` — never
   hardcode, never print these. For an end-to-end flow needing multiple
   roles, log in as each role in its own browser context.
3. Navigate to only the page(s) the current step needs.
4. For each business step, find the corresponding UI element.
5. Verify the element resolves uniquely before recording it.
6. Capture a screenshot or DOM snippet as evidence.
7. Save the result into a temporary mapping artifact (JSON) — see the
   `automation-mapping` skill — before handing off to the Automation
   Engineer agent.
8. Write or update the permanent catalog file
   `automation/element_catalog/<page-name>.md` (template:
   `templates/element_catalog_template.md`) for every page visited, with the
   screenshot in `element_catalog/evidence/`. Do this even when the mapping
   JSON is later archived.

## Scope discipline
Never crawl/inspect the entire application "just in case." Map one
flow's pages at a time, role by role, matched exactly to what's being
automated right now.

## Shared components
Inspect and map a component that appears across many pages (nav bar,
common modal) once, save it as a reusable fragment, and reference it from
every page-specific mapping instead of re-inspecting it.

## Evidence
Every mapped locator should have evidence attached so a human reviewing a
`LOCATOR_REQUIRES_REVIEW` item can verify quickly without re-running the
exploration.
