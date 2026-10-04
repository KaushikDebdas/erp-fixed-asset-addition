# Element catalog

The permanent record of the screens and elements we have seen in the
application. One file per page, named after the page class
(`login_page.md` goes with `pages/login_page.py`).

## Why it exists
- A new team member can see what is on a screen without opening the app.
- When a test breaks after a UI change, compare the catalog with the live page
  and see what moved.
- The catalog says what exists. The page class (`pages/*.py`) is the one place
  tests get locators from.

## Rules
1. `ui-explorer` creates or updates a catalog file every time it visits a page.
   Start from `templates/element_catalog_template.md`.
2. Never delete a catalog file. Mark an element REMOVED if it disappears.
3. When a locator changes, update the catalog and the page class together.
4. Statuses: `VERIFIED` (found and checked), `LOCATOR_REQUIRES_REVIEW`
   (no reliable locator yet — never guess one), `REMOVED`.
5. Screenshots go in `evidence/`, named after the page.
6. Never put credentials or real personal data in these files.
