# My Dashboard — element catalog

| Field | Value |
|---|---|
| Page class | `pages/base_page.py` → `BasePage.close_popup_if_present()` (shared method, not a dedicated `DashboardPage` class yet) |
| Module / menu path | Landing page right after login |
| Entry URL | `/myDashboard/myDashboard` |
| Role needed | ERP External User |
| Last explored | 2026-10-03 |
| Screenshot | `evidence/dashboard_page_popup.png` |

## Elements

| # | Element | What it is for | Locator (Playwright) | Seen in the page as | Status |
|---|---|---|---|---|---|
| 1 | Announcement/image popup | Promotional image carousel (e.g. "Discover Authentic Bangladesh with Otithi") shown on some logins | `page.locator("#modals.active")` | White modal box with image + left/right carousel arrows | VERIFIED |
| 2 | Popup close button | Dismisses the announcement popup | `page.locator("#modals button[data-close-button]")` | "×" icon, top-right of the popup | VERIFIED |

## Notes
- Not an ARIA/Bootstrap dialog — it is a custom component (`<div id="modals" class="modals active">`), so role-based locators (`get_by_role`) do not find it. Had to use the `id`/attribute CSS selector instead.
- It does not appear on every login (not observed on the very first login of this session, but reliably appeared after a fresh logout → login cycle). Treat it as conditional: wait briefly for it, and if it never shows, continue — do not fail the test.
- `BasePage.close_popup_if_present(timeout=3000)` encapsulates this: waits up to 3s for `#modals button[data-close-button]` to become visible, clicks it if found, otherwise logs and returns without error.
- No dedicated `dashboard_page.py` exists yet (deleted along with the rest of the Addons-specific automation). This catalog entry exists purely to document the popup; add the dashboard's other elements here once a `DashboardPage` class is written.
