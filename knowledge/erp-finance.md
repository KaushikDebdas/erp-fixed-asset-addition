# ERP Finance — Income Statement & Balance Sheet (domain knowledge)

| Field | Value |
|---|---|
| Domain / sub-domain | Finance / Income Statement and Balance Sheet |
| Application | BRAC ERP, Finance ("addons") app — staging environment |
| Project using this file | `projects/addons/` |
| Last updated | 2026-10-02 |
| Sources | Live exploration of the staging app with Playwright MCP (2026-10-01/02); automated test runs of `tests/test_01_login.py` and `tests/test_02_income_statement.py`; screenshots in `automation/element_catalog/evidence/`; page notes in `automation/element_catalog/*.md` |

**Tags:** `[CONFIRMED]` seen directly in the app or in a test run · `[INFERRED]` reasonable reading of what was seen, not stated by the app · `[NEEDS_CLARIFICATION]` unknown; ask a business owner before relying on it.

> No credentials, personal data or report figures are stored here. Report numbers on staging change; never use them as expected values.

---

## How to use this file (section index)

Read only the section(s) you need.

| § | Topic | Use it when |
|---|---|---|
| §1 | Application and access | Starting any task: URLs, login, sign-in flow |
| §2 | Session behaviour | A test is sent to a different sign-in page |
| §3 | Finance app navigation | Writing steps that go to a report |
| §4 | Income Statement screen and workflow | Any Income Statement test case |
| §5 | Report Filter fields | Choosing inputs / required-field and negative cases |
| §6 | Report view options | Designing coverage across views |
| §7 | Messages the screen shows | Writing expected results |
| §8 | Preview vs Export behaviour | Waits, timings, large reports |
| §9 | Exported Excel file | Checking a downloaded report |
| §10 | Report data structure | Understanding what a report contains |
| §11 | Automated coverage so far | Avoiding duplicate automation |
| §12 | Test data and environment notes | Running or extending the suite |
| §13 | Open questions | Before writing business-rule test cases |
| §14 | Not explored yet | Scoping the next exploration |
| §15 | Optional filters: values and dependencies | Choosing filter values or combinations |

---

## §1 Application and access

- [CONFIRMED] The ERP login page is `https://erpstaging.brac.net/`. It redirects to a Keycloak sign-in page (`/idp/realms/brac/protocol/openid-connect/auth?...`, page title "Sign in to BRAC ERP"). The address after the redirect contains values that change every visit (`state`, `tab_id`); never compare the full URL.
- [CONFIRMED] The sign-in form has a Username box, a Password box (with a show/hide toggle next to it), a "Forgot Password?" link and a "Sign In" button. A failed login error message has not been captured yet (§14).
- [CONFIRMED] After a successful login the browser lands on **My Dashboard**: `/myDashboard/myDashboard?flag=false`, page title "My Dashboard". It shows module tiles and a module tab bar (Settings, HRM, EDMS, ePMS, Procurement, eTender, Microfinance, Accounting, Budget).
- [CONFIRMED] **Advertisement popup:** right after login an image popup (banner slider with Prev / Next arrows and an × in the corner, container id `modals`) may appear on My Dashboard. It does **not** appear every time. While it is open it blocks every click on the page behind it. It is taller than a 1280×720 window, so on small screens its × can sit above the visible area.
- [CONFIRMED] The Finance app lives under the same host: `/addons/fin/dashboard`.
- [CONFIRMED] The user used for exploration belongs to Head Office (shown in the Finance header as "Head Office [BDHO]").
- [NEEDS_CLARIFICATION] Which role or permission is required to open Financial Reports. Only one user has been used.

## §2 Session behaviour

- [CONFIRMED] Opening `/addons/fin/dashboard` (or any `/addons/...` page) when not logged in, or after the session has ended, redirects to a **different** sign-in page (`loginstg.brac.net`, title "SSO Login") that asks for a BRAC PIN and password, or "Sign in" with a BRAC Gmail account. The ERP username/password do not work there.
- [CONFIRMED] Working route: log in at the ERP page (`BASE_URL`) first, close the popup if shown, then open the `/addons/...` address. Done this way, the Finance app opens without a second sign-in.
- [CONFIRMED] A browser session that sat unused for several minutes was found logged out when it was used again.
- [NEEDS_CLARIFICATION] The exact session timeout, and whether a direct visit to `/addons/...` ever ends an active ERP session.

## §3 Finance app navigation

- [CONFIRMED] Finance dashboard (`/addons/fin/dashboard`, title "Dashboard") top menu: **Dashboard**, **Settings**, **Consolidation**, **Reports**. The dashboard welcome area shows an "ERP <month year> close status" progress bar and "Consolidation status".
- [CONFIRMED] **Reports** menu (nested drop-downs, each opens after the one above is clicked):
  - **Voucher** → Store Vouchers, HO Breakup Vouchers, Auto voucher, HO Voucher
  - **Ledger** → Ledger Balance, Ledger Transaction Details, Ledger Wise Summary Balance
  - **Financial Report** → **Income Statement** (the only item explored); further items exist but have not been listed (§14)
- [CONFIRMED] The word "Income statement" (lower-case s) also appears as an item in other menus of the app. Locators for "Income Statement" must match the capital S exactly.
- [CONFIRMED] Menu path used by the automation: **Reports > Financial Report > Income Statement**. Clicking it opens `/addons/fin/financial-reports/income-statement`, page title "Financial Report | Income Statement" (the title shown just after the click is "Financial Report").

## §4 Income Statement — screen and workflow

- [CONFIRMED] Opened without criteria, the page shows the text **Please choose criteria from "Filter" options** and an empty report area.
- [CONFIRMED] Workflow: **Filter** button (top bar) → "Report Filter" popup → fill fields → **Preview** → report appears as a grid on the **same page** (no address change) → **Export** (top bar) downloads an Excel file.
- [CONFIRMED] The popup also has its own **Export** button. It downloads the Excel file without showing the report first. This is the route used when a report is too large to preview (§8).
- [CONFIRMED] The popup closes after Preview. Opening Filter again keeps the values entered earlier on the same page load; reloading the page gives an empty filter.
- [CONFIRMED] The report is shown as an interactive pivot grid (a WebDataRocks component). Row labels can be collapsed/expanded.

## §5 Report Filter fields

Required fields are marked with `*` on screen.

| Field | Required | Type and values | Default |
|---|---|---|---|
| From date | **Yes** | Month picker, shown as `MM-YYYY` (e.g. `07-2025`) | empty |
| To date | **Yes** | Month picker, shown as `MM-YYYY` (e.g. `06-2026`) | empty |
| Report view | **Yes** | Drop-down, 13 options in 4 groups (§6) | empty ("Please choose report view") |
| Show Zero | **Yes** | Drop-down: Yes / No | No |
| Conversion | No | Drop-down: No Conversion, Crore Unit, Million Unit | No Conversion |
| Project Status | No | Drop-down: Active / Inactive / Close | All |
| Category | No | Multi-select (e.g. Development, Enterprise, Microfinance, each with a count in brackets) | none = all |
| Program | No | Multi-select, searchable ("All program") | none = all |
| Project | No | Multi-select, searchable ("All Project") | none = all |
| Report For | No | Drop-down: Field Office / Head Office | All |
| Divisional office | No | Multi-select ("All division") | none = all |
| Regional office | No | Multi-select ("All Region") | none = all |
| Area office | No | Multi-select ("All Area") | none = all |
| Branch Office | No | Multi-select ("All Branch") | none = all |
| CoA Layer | No | Multi-select: 2-Sub Group, 3-Parent, 4-Sub Parent, 5-Head, 6-Sub Head, 7-Ledger | none = all |

- [CONFIRMED] Buttons at the bottom of the popup: Reset, Preview, Export, Close.
- [CONFIRMED] The month picker shows a year at the top with back / forward arrows and 12 months (Jan–Dec). Months after the current month (at the time: Oct, Nov, Dec 2026) are disabled, and the forward arrow is disabled in the current year. Selecting a month fills the box as `MM-YYYY`.
- [CONFIRMED] The Report view drop-down is searchable-style (select2) and its options are grouped (§6).
- [INFERRED] From date later than To date, a missing required field, and a range crossing many years are likely validation / edge cases. No behaviour has been captured for them yet (§14).

## §6 Report view options (the main search criteria)

The Report view drop-down groups its 13 options. Option names are exact.

| Group (as shown) | Options |
|---|---|
| Time Breakdown | Yearly, Monthly, Consolidate |
| Project/Program View | Category, Program, Project |
| Office Hierarchy View | Division, Region, Area, Branch |
| Report For | HO, FO, Both |

- [CONFIRMED] Every option except **Branch** produces an on-screen report (Preview) and a downloadable Excel file with the date range 07-2025 to 06-2026 (§11).
- [CONFIRMED] **Branch** is too large to preview; see §7 and §8.
- [CONFIRMED] With **Yearly** and the range 07-2025 to 06-2026, the grid shows two column headings, **2025** and **2026** — i.e. the yearly breakdown groups by calendar year, so one financial year (Jul–Jun) is split over two columns.
- [NEEDS_CLARIFICATION] How "Consolidate" differs from "Yearly" in the figures, what the "Report For" options HO / FO / Both mean when the separate "Report For" field (All / Field Office / Head Office) is also present, and how Report view = "Report For" interacts with it.

## §7 Messages the screen shows

The screen shows messages as small pop-up boxes (SweetAlert). Texts are exact, including the space before the comma.

| Message | When | Position / look | Button |
|---|---|---|---|
| `Due to the large data size , please view the report by downloading in Excel format.` | After Preview with Report view = **Branch** (date range 07-2025 to 06-2026) | Centre of the screen, error icon (red ×) | OK |
| `Your file download will start shortly!` | After **Export in the Filter popup**, when the server has finished preparing the file | Top-right corner, success icon (green tick) | – |
| `Please wait...` | While the server builds the report or the Excel file | A box over the page (not a pop-up message) | – |

- [CONFIRMED] Clicking OK on the large-data message closes the message only; the Filter popup stays open with the values still filled.
- [CONFIRMED] The top-bar **Export** (used after a normal Preview) showed **no** message in the checks made — only "Please wait..." and then the download. 
- [NEEDS_CLARIFICATION] Whether the top-bar Export is expected to show a success message too. If it should, the missing message is a defect to raise.
- [NEEDS_CLARIFICATION] The messages for invalid input (missing required field, From date after To date) have not been captured.

## §8 Preview vs Export behaviour

- [CONFIRMED] **Normal Preview:** click Preview → "Please wait..." → report grid appears. Seconds for most views.
- [CONFIRMED] **Large report (Branch):** Preview shows the large-data message instead of a report. The Excel file must be downloaded from the **Export button inside the Filter popup**. The server then works for roughly **2 to 2.5 minutes** before the success message appears and the file downloads (the same test failed when the download wait was only 2 minutes).
- [CONFIRMED] **Top-bar Export** after a normal Preview: "Please wait..." then the file downloads, no message.
- [INFERRED] The large-data rule depends on how many rows the report would have, not only on the Report view name, so other combinations (very wide date ranges, "Both" with "Branch" detail) might also trigger it.
- [NEEDS_CLARIFICATION] The size limit that triggers the large-data message.

## §9 Exported Excel file

- [CONFIRMED] File type `.xlsx`, about 200 KB for Report view = Yearly, 07-2025 to 06-2026.
- [CONFIRMED] Sheets in that file: **income-statement**, **Project List**, **Office Demarcation**. The income-statement sheet had about 3,900 rows and 8 columns.
- [CONFIRMED] All 13 exportable views downloaded a non-empty `.xlsx` on 2026-10-01/02.
- [NEEDS_CLARIFICATION] The expected column layout of each sheet per Report view, which was not inspected in detail, and whether the exported figures must equal the on-screen figures.

## §10 Report data structure

- [CONFIRMED] Rows are chart-of-account entries shown as `[code]-Name`, in a tree. Example path: `[4]-Income` → `[41]-Operating Income` → `[4101]-Service Charge Income Micro Credit` → `[410101]-Service Charge-Current Loan` → `[41010101]-…` → `[4101010101]-…` → leaf `[4101010101-01]-Service Charge`. Codes get longer by two digits per level; the last level has a `-NN` suffix.
- [CONFIRMED] Other top-level income groups seen under `[41]`: Income from Social Enterprise (`[4102]`), Investment Income (`[4103]`), Other Operating Income (`[4104]`).
- [CONFIRMED] Income amounts are shown as **negative** numbers with thousands separators and no decimals.
- [INFERRED] The negative sign means income is stored as a credit balance.
- [CONFIRMED] Leaf values are underlined (they can be clicked to see detail); parent rows show totals.
- [CONFIRMED] CoA Layer filter options are 2-Sub Group, 3-Parent, 4-Sub Parent, 5-Head, matching the depth of the tree.
- [NEEDS_CLARIFICATION] The numeric meaning of "CoA Layer" values versus the code lengths, and whether parent totals must equal the sum of their children (a candidate business-rule check).

## §11 Automated coverage so far

All in `automation/tests/`. The date range of the Income Statement tests is set once at the top of the file; the values below are the current ones (07-2025 to 06-2026). Each test downloads its own Excel file named `<test name>_<date range>.xlsx`.

| Test | Criteria | What is checked |
|---|---|---|
| `test_login_page_loads` | Sign-in page | Form is displayed |
| `test_login_with_valid_credentials` | Valid user | Reaches My Dashboard; popup closed if shown |
| `test_open_income_statement_page_from_reports_financial_report_menu` | Menu path | Income Statement page opens |
| `test_income_statement_time_breakdown_yearly` | Time Breakdown = Yearly | Report shown, no unexpected message, Excel downloaded |
| `test_income_statement_time_breakdown_monthly` | Time Breakdown = Monthly | same |
| `test_income_statement_time_breakdown_consolidate` | Time Breakdown = Consolidate | same |
| `test_income_statement_project_program_view_category` | Project/Program View = Category | same |
| `test_income_statement_project_program_view_program` | Project/Program View = Program | same |
| `test_income_statement_project_program_view_project` | Project/Program View = Project | same |
| `test_income_statement_office_hierarchy_division` | Office Hierarchy View = Division | same |
| `test_income_statement_office_hierarchy_region` | Office Hierarchy View = Region | same |
| `test_income_statement_office_hierarchy_area` | Office Hierarchy View = Area | same |
| `test_income_statement_office_hierarchy_branch_large_report_export_only` | Office Hierarchy View = Branch | Exact large-data message, then Export in the popup shows exact success message and downloads the file |
| `test_income_statement_report_for_head_office` | Report For = HO | Report shown, Excel downloaded |
| `test_income_statement_report_for_field_office` | Report For = FO | same |
| `test_income_statement_report_for_both_offices` | Report For = Both | same |

- [CONFIRMED] All 16 tests passed in the latest full run (about 10.5 minutes). The tests prove the report appears and a non-empty file downloads; they do **not** compare any figure.
- [CONFIRMED] Added 2026-10-02, **not yet executed**: `tests/test_03_income_statement_filter_combinations.py`, 52 pairwise combinations of Report view, Project Status, Category, Program, Project, Report For, Divisional office and CoA Layer, with Show Zero = No and Conversion = no conversion fixed (§15).
- [CONFIRMED] Not covered by automation: Show Zero and Conversion values other than the defaults, the Regional / Area / Branch office fields, multiple values in one filter, invalid input, other date ranges, other reports (§14).

## §12 Test data and environment notes

- [CONFIRMED] Staging data changes over time. Never assert exact report numbers; assert that a report appears, what messages show, and that the file downloads.
- [CONFIRMED] The month picker blocks future months, so test date ranges must end in or before the current month.
- [CONFIRMED] Run the browser maximized and visible; a small window hides the popup's × button (§1).
- [CONFIRMED] A full run of the 16 tests takes about 10–11 minutes, most of it the Branch export and the large views.
- [CONFIRMED] Credentials live only in the git-ignored `.env`; never write them in documentation.

## §13 Open questions (ask a business owner)

1. [NEEDS_CLARIFICATION] Fiscal year: is the financial year July–June? (The tests use 07-2025 to 06-2026, and the Yearly view splits it into 2025 and 2026.)
2. [NEEDS_CLARIFICATION] What exactly triggers the "large data size" message (row count? Report view?) and should Branch ever allow Preview?
3. [NEEDS_CLARIFICATION] Should the top-bar Export show a success message like the popup Export does?
4. [NEEDS_CLARIFICATION] What do Show Zero = Yes, Conversion (Crore / Million), Project Status and CoA Layer change in the report and in the Excel file?
5. [NEEDS_CLARIFICATION] Meaning and interaction of the "Report For" group options (HO / FO / Both) and the separate "Report For" field.
6. [NEEDS_CLARIFICATION] Expected behaviour and messages for invalid input (missing required field, From date after To date).
7. [NEEDS_CLARIFICATION] Which roles may see Financial Reports and which offices' data each role sees.
8. [NEEDS_CLARIFICATION] Do on-screen totals have to equal the Excel totals, and do parent totals equal the sum of their children?
9. [NEEDS_CLARIFICATION] Session timeout and expected behaviour when the session ends during a report.

## §15 Optional filters: values and dependencies

Explored in the live Filter popup on 2026-10-02. Locators are in `automation/element_catalog/income_statement_page.md`.

| Filter | Kind | Values |
|---|---|---|
| Conversion | Single select | (empty = no conversion), Crore Unit, Million Unit |
| Project Status | Single select | (empty), Active, Inactive, Close |
| Category | Multi-select, fixed list | Development, Enterprise, Microfinance, Self Financing, Unknown (each with a count in brackets) |
| Program | Multi-select, loaded from the server | Depends on Category; paged ("Loading more results…") |
| Project | Multi-select, loaded from the server | Depends on Program |
| Report For | Single select | (empty), Field Office, Head Office |
| Divisional / Regional / Area / Branch office | Multi-selects, loaded from the server | See dependencies below |
| CoA Layer | Multi-select, fixed list | 2-Sub Group, 3-Parent, 4-Sub Parent, 5-Head, 6-Sub Head, 7-Ledger |

- [CONFIRMED] Cascade 1: Category → Program → Project. The Program list is empty until a Category is chosen and the box is opened; the Project list follows the chosen Program.
- [CONFIRMED] Cascade 2: Division → Region → Area → Branch. Region shows "No results found" until a Division is chosen, and Area until a Region is chosen. Seen: Dhaka → Gazipur, Manikgonj, Munshigonj, Narsingdi; Gazipur → Kapasia(N). Branch lists branches even with no parent chosen.
- [CONFIRMED] Report For = Field Office shows the four office fields; Head Office hides them and clears anything chosen in them.
- [CONFIRMED] Program choices depend on Project Status as well as Category: Category = Enterprise with Project Status = Inactive has no programs ("No results found"). Every other Status and Category pair has programs (checked on 2026-10-02).
- [CONFIRMED] Divisional office choices narrow to the chosen Program and Project: with a Program and Project chosen the list is empty for Category = Enterprise and for Project Status = Close; for Development with any, Active or Inactive status it holds a few divisions (the set differs by status, e.g. Sylhet and Rajshahi for Active). With no Program chosen all divisions (or those of the chosen Category) are listed.
- [CONFIRMED] A filter combination with no matching data shows a red popup "No data found" after Preview (nothing is exported).
- [CONFIRMED] With CoA Layer = 3-Parent, Preview shows a report but the top-bar Export shows "No Data Found" and downloads nothing. The same filters without CoA Layer export normally. [NEEDS_CLARIFICATION] Is this intended?
- [CONFIRMED] Full filter-combination run (2026-10-02): the top-bar Export showed "No Data Found" and downloaded nothing after a Preview that did show a report, in 15 of 52 combinations. It always happened with CoA Layer = 3-Parent, and also with Head Office + CoA 7-Ledger, Report view Region + Head Office, Report view Division + Head Office, and Report view Division + Enterprise Program + Project. [NEEDS_CLARIFICATION] Why does Export disagree with Preview?
- [CONFIRMED] Report view = HO together with Report For = Field Office (and a Divisional office) shows "For HO view demarcation selection is invalid". [INFERRED] The Report view options HO / FO / Both only work with a matching Report For.
- [CONFIRMED] A multi-select list stays open after an option is clicked and can cover the next field; clicking an empty spot in the popup closes it.
- [CONFIRMED] "Report For" (filter) and the Report view options HO / FO / Both are different fields.
- [INFERRED] The 52 pairwise combinations in `test_03_income_statement_filter_combinations.py` treat Program, Project and Divisional office as valid only when their parent filter has a value. Whether the app also accepts them without a parent is not tested.
- [NEEDS_CLARIFICATION] What Show Zero = Yes, Conversion = Crore / Million Unit and CoA Layer actually change in the report (see §13).
- [NEEDS_CLARIFICATION] Which filter combinations make a report large enough to trigger the large-data warning (only Report view = Branch with no other filter is confirmed). The combination tests accept either the report or exactly that warning.

## §14 Not explored yet

- Balance Sheet (this project's second sub-domain): where it is in the menu and its filter fields.
- The other items under **Financial Report**, the **Consolidation** and **Settings** menus, and the Ledger and Voucher reports.
- Login failure: the error message shown for a wrong password (the element is not mapped yet).
- Optional filter fields and their effect, other date ranges, and negative / edge cases for the Report Filter.
- The detail behind a clicked leaf value in the report grid.
