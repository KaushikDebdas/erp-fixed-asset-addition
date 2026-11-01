# Login (ERP sign-in screen) — element catalog

| Field | Value |
|---|---|
| Page class | `pages/login_page.py` → `LoginPage` |
| Module / menu path | None. The ERP address redirects here when nobody is signed in. |
| Entry URL | `BASE_URL` from `.env`; it redirects to `https://erpstaging.brac.net/idp/realms/brac/protocol/openid-connect/auth?...` (page title "Sign in to BRAC ERP") |
| Role needed | None |
| Last explored | 2026-10-11 |
| Screenshot | `evidence/login_failed_sign_in.png` (after a wrong login) |

## Elements

| # | Element | What it is for | Locator (Playwright) | Seen in the page as | Status |
|---|---|---|---|---|---|
| 1 | Username box | Type the user name | `page.get_by_role("textbox", name="Username")` | textbox "Username" | VERIFIED |
| 2 | Password box | Type the password | `page.get_by_role("textbox", name="Password")` | textbox "Password" | VERIFIED |
| 3 | Sign In button | Submit the credentials | `page.get_by_role("button", name="Sign In")` | button "Sign In" | VERIFIED |
| 4 | Invalid login message | Shown after a wrong username or password | `page.get_by_text("Invalid username or password.")` | plain text next to the Username box; both boxes also become `[invalid]` | VERIFIED |

## Office Selection screen (shown after sign-in to users with more than one office)

Explored 2026-10-14 with a multi-office user signed in by the user. Page title "Office Selection", address `/officeDashboard/selectLogInOffice?flag=false`.
Screenshots: `evidence/login_office_selection.png`, `evidence/login_office_selection_dropdown_open.png`.

| # | Element | What it is for | Locator (Playwright) | Seen in the page as | Status |
|---|---|---|---|---|---|
| 5 | Screen heading | Tells the Office Selection screen is showing | `page.get_by_role("heading", name="Please select office to login")` | heading level 3 | VERIFIED |
| 6 | Office Code box | Click to open the office list | `page.locator("#officeIdDiv_input")` | unnamed textbox (first on the page) | VERIFIED (CSS id; no accessible name exists) |
| 7 | Office Code arrow | Opens the office list | `page.locator("#officeIdDiv_arrow")` | arrow beside the box | VERIFIED |
| 8 | Office option | One office in the opened list | `page.locator("#officeIdDiv_ctr .row").filter(has_text="<office text>")` | row text like `[BO - 0189] Golapgonj (Dhaka Dhakin-Sylhet)` | VERIFIED (list read; no option clicked yet) |
| 9 | Office Name box | Read-only; fills after an option is picked | `page.locator("#officeName")` | read-only textbox | VERIFIED (not yet seen filled) |
| 10 | Office Type box | Read-only; fills after an option is picked | `page.locator("#officeType")` | read-only textbox | VERIFIED (not yet seen filled) |
| 11 | Go button | Confirms the chosen office | `page.get_by_role("button", name="Go", exact=True)` | button "Go" (without `exact=True` it also matches "Logout") | VERIFIED |
| 12 | Logout button | Leaves without choosing | `page.get_by_role("button", name="Logout")` | button "Logout" | VERIFIED |

## Log out (any ERP page after sign-in; used by `LoginPage.log_out()`)
| # | Element | Purpose | Locator | Text on screen | Status |
|---|---|---|---|---|---|
| 13 | Account menu icon | Round user icon at the top right; opens the account menu (`#login_container`, hidden until clicked) | `page.locator("#btn_login")` | (icon only) | VERIFIED |
| 14 | Logout link | Ends the session; the browser goes to the sign-in screen (`/idp/...`) | `page.locator('#login_container a[href="/logout"]')` | Logout | VERIFIED |
- Read on env42 (HOFA) 2026-11-01 as the HOFA acknowledger, on the dashboard and on the Fixed Asset module. After Logout the Username box shows at once. The menu also has "Release Notes". The page also holds a hidden session-timeout dialog with its own `#session-timeout-dialog-logout` button; it is not used.

### Office Selection notes
- The picker is a custom list, not a native select. Options are `div.row` items inside `#officeIdDiv_ctr`, and the list is hidden until the box or arrow is clicked.
- Each option reads `[<type> - <code>] <name>`, for example `[BO - 0189] Golapgonj (Dhaka Dhakin-Sylhet)`. The page's JavaScript lists all of the user's offices up front, so the options can be read before opening the list (`officeFlaxBox.setData([...])`).
- The first office is pre-highlighted (`ffb-sel`) but not chosen; the box starts empty and is required.
- It appears after the sign-in server step, so the address has already left `/idp/`. `verify_logged_in()` therefore passes before the office is chosen.
- Choosing "[BO - 6981] ... - Development" fills the Office Name box ("Golapgonj (Dhaka Dhakin-Sylhet) - Development") and Office Type box ("Branch Office"), closes the list and sets the hidden `#officeId`. Clicking Go then opens `/myDashboard/myDashboard` (title "My Dashboard"). Confirmed 2026-10-14.
- NOT YET SEEN: what a single-office user sees (expected: no such screen, straight to the dashboard) and what a head-office user's list looks like. Both need another sign-in.

## Notes
- Checked on 2026-10-11 with a made-up user name and password (no real account used). One failed attempt only.
- The sign-in server is a separate part of the site: its addresses contain `/idp/`. After a good login the address leaves `/idp/`. `LoginPage.verify_logged_in()` uses that to decide a login worked.
- Messages for other failures (for example a locked or disabled account) were not seen. If one appears, add it here and in `verify_logged_in()`.
