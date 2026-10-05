# My Dashboard — element catalog

| Field | Value |
|---|---|
| Page class | `pages/base_page.py` → `BasePage.close_popup_if_present()` (shared method, not a dedicated `DashboardPage` class yet) |
| Module / menu path | Landing page right after login |
| Entry URL | `/myDashboard/myDashboard` |
| Role needed | ERP External User |
| Last explored | 2026-10-03 |
| Screenshot | `evidence/dashboard_page_popup.png`, `evidence/dashboard_popup_close_button_offscreen_1366x768.png` (× above the visible area) |

## Elements

| # | Element | What it is for | Locator (Playwright) | Seen in the page as | Status |
|---|---|---|---|---|---|
| 1 | Announcement/image popup | Promotional image carousel (e.g. "Discover Authentic Bangladesh with Otithi") shown on some logins | `page.locator("#modals.active")` | White modal box with image + left/right carousel arrows | VERIFIED |
| 2 | Popup close button | Dismisses the announcement popup (not used by the automation, see Notes) | `page.locator("#modals button[data-close-button]")` | "×" icon, top-right of the popup | VERIFIED |
| 3 | Dark overlay behind the popup | Covers the whole page while the popup is open; a click on it outside the popup box closes the popup | `page.locator("#overlay.active")`, clicked at `position={"x": 5, "y": 5}` (top-left corner, always outside the popup box) | Dark layer behind the white popup box | VERIFIED |

## Notes
- Not an ARIA/Bootstrap dialog — it is a custom component (`<div id="modals" class="modals active">`), so role-based locators (`get_by_role`) do not find it. Had to use the `id`/attribute CSS selector instead.
- It does not appear on every login (not observed on the very first login of this session, but reliably appeared after a fresh logout → login cycle). Treat it as conditional: wait briefly for it, and if it never shows, continue — do not fail the test.
- `BasePage.close_popup_if_present(timeout=3000)` encapsulates this: waits up to 3s for `#modals.active`, clicks the overlay `#overlay.active` at its top-left corner, then waits for the popup to be hidden; if the popup never shows it logs and returns without error.
- **System bug, verified 2026-10-05:** the popup box is fixed at the centre of the window and can be taller than the window. At 1366x768 it is 838 px high and starts at y = -35, so the × button (y = -20) is above the visible area and a normal click on it times out. At 800x600 and 480x700 the box is smaller and the × is on screen. Clicking outside the popup box closes it at every size tried (1366x768, 1920x1080, 800x600, 480x700), so the automation uses the overlay click instead of the × button.
- No dedicated `dashboard_page.py` exists yet (deleted along with the rest of the Addons-specific automation). This catalog entry exists purely to document the popup; add the dashboard's other elements here once a `DashboardPage` class is written.
