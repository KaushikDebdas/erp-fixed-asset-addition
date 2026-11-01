# How to Run the Automation Suite

## First-time setup
1. Install Python 3.10+ — check with `python --version`
2. Install dependencies: `pip install -r requirements.txt`
3. Install Playwright's browser: `playwright install chromium`
4. Copy `.env.example` to `.env` and fill in `BASE_URL` and credentials
   (add extra role credentials here too, for multi-role E2E flows).
   Never commit the real `.env` — it's already in `.gitignore`.
5. Install Node.js 18+ (`node --version`) — required by the Playwright MCP
   server that Claude Code uses for UI exploration.
6. Make sure the `.claude/` folder exists at the project root (with
   `agents/`, `skills/` and `settings.json`). If not, ask Claude Code to
   create it — see `CLAUDE.md` → "Claude Code Setup".
7. Make sure the Playwright MCP server is configured: `.mcp.json` at the
   project root must contain the `playwright` server, or run
   `claude mcp add playwright npx @playwright/mcp@latest`. Approve it when
   Claude Code asks, then check with `/mcp` (or `claude mcp list`) —
   `playwright` must show as connected.
8. Install Allure and Java. They are only needed to build the HTML report at the end of a run
   (the tests run without them). `npm install -g allure-commandline`, then a Java 8 or newer
   (any JDK, for example from adoptium.net) with `JAVA_HOME` set. Check with `allure --version`,
   `java -version` and `echo %JAVA_HOME%`. Details: "The HTML report" below.

## The users in `.env` (who signs in, and in which office)
| Settings | Who | Used for |
|---|---|---|
| `ERP_USERNAME`, `ERP_PASSWORD`, `DEFAULT_BRANCH` | the main user (the sender) | every test; creates and approves |
| `ASSIGN_ERP_USERNAME`, `ASSIGN_ERP_PASSWORD`, `ASSIGN_DEFAULT_BRANCH` | the employee an asset is assigned to | Asset Assign Acknowledgement (test 11); needs the `Asset Assign Acknowledgement` menu |
| `ACK_SHIPMENT_ERP_USERNAME`, `ACK_SHIPMENT_ERP_PASSWORD`, `ACK_SHIPMENT_ERP_DEFAULT_BRANCH` | a user of the receiving branch; its default branch IS the receiving branch | acknowledging an Asset Shipment or a Single Challan sent to another branch (tests 20 and 24); needs the In-Challan menus |

- `DEFAULT_BRANCH` is the office picked at **Office Selection** after signing in (only users with more than one office see that screen). Write it in any style: `0233`, `[BO-0233]-Chagalnaiya`, `- Development`. Leave it empty for a user with one office.
- **The ERP allows one login per user.** The three users must be different people, and do not use one of them in the Playwright MCP browser while a test run is going.
- Approving and acknowledging need the accounting day open. The top right corner of every Fixed Asset page shows `Accounting Date : dd-mm-yyyy [DAY OPEN]` or `[DAY CLOSED]`. On a closed day those steps are refused with `Business day not open for Fixed Asset.`; the tests that create things stop early with a message when their own office's day is closed.
- Run one scenario: `pytest tests/test_20_asset_shipment_in_challan.py -k different_branch_same_project` (add `-k single_out_challan_different_branch_same_project` for the Single Challan twin in `test_24_asset_single_in_challan.py`).

## Which Python runs the tests
Use this project's own `.venv` (it has the packages from `requirements.txt`). Other projects on
this PC have a `.venv` too and the prompt shows `(.venv)` for all of them, so check first:
```
cd D:\fixedasset-automation
where pytest          (the first line must be D:\fixedasset-automation\.venv\Scripts\pytest.exe)
```
Safest command, from `D:\fixedasset-automation`, with no activation needed:
```
.venv\Scripts\python.exe -m pytest automation/tests/test_05_generate_barcode.py
```
If pytest or a package such as playwright is not found, the terminal is using another project's
Python: run `deactivate`, then `.venv\Scripts\activate` in this folder.

Small screen: add `--screen-size 1280x720` to run in a window of that size.

## Running tests

| Command | What it does |
|---|---|
| `pytest -m smoke` | Runs only smoke-tagged tests |
| `pytest -m regression` | Runs only regression-tagged tests |
| `pytest -m "smoke or regression"` | Runs both suites |
| `pytest -k test_internal_movement` | Runs the tests whose name contains the text |
| `pytest tests/test_01_asset_registration_aaq.py` | Runs all tests in one file |
| `pytest -v` | Verbose — shows each test name as it runs |

By default the browser is visible and maximized (set in `conftest.py`). Add
`--headless` to run without a window, for example `pytest -m smoke --headless`;
the page then gets a 1920 x 1080 size.

## Running one test from VS Code (play button)
The project's `.vscode/settings.json` turns on pytest and selects the `.venv`
Python, so the Testing panel (beaker icon) lists every test and each test and
file has a play button. After pulling the project: press Ctrl+Shift+P, run
"Developer: Reload Window", then open the Testing panel. A test started from
the play button runs with the browser visible and the same logs.

## Where the assets come from (the asset map)
Every test that needs an asset takes it from the asset pool by slot name
(`assets.get("sale_profit_a")`, `utils/asset_pool.py`). The table of slots is in
`test_data/asset_slots.py`; this is who uses which asset:

| Slot | Item | Used by, in order |
|---|---|---|
| usage_a (Draft + Submit path) | furniture spot | Assign, Acknowledge, Internal Movement, Un Assign, Expense, then Write-off (test_10 to 13, 16, 26 to 28) |
| usage_b (Submit-only path) | furniture gift | Assign, Internal Movement, Un Assign, Expense, then Write-off (test_10, 12, 13, 16, 27) |
| split_land | land spot | Asset Serial Split (test_07 to 09) |
| transfer_a | furniture spot | Asset Shipment (test_18 to 22) |
| challan_a / challan_b | furniture spot / gift | Asset Single Challan, Draft path / Submit-only path (test_22 to 26) |
| sale_profit_a / sale_profit_b | building spot / gift | Asset Sale above the Written Down Value, Draft / Submit (test_29, 30) |
| sale_loss_a / sale_loss_b | laptop spot / gift | Asset Sale below the Written Down Value, Draft / Submit (test_29, 30) |
| reg_draft / reg_pending | desktop spot / furniture spot | stay a Draft / stay PENDING (registration tests) |

- **A full run** (`pytest`): tests 01 to 03 register and approve the slot assets once, the later
  tests find them in the pool and reuse them, so an asset is never created twice. An asset a flow uses
  up (sold, split, in a challan, written off) is taken out of the pool.
- **One test alone** (for example `pytest tests/test_29_asset_sale.py -k loss_submit`): the pool is
  empty, so the test registers and approves exactly the asset it needs, then uses it. No test depends on
  another having run.
- The assets exist only for the run (nothing is saved between runs), so every run starts with new assets.
  The log shows `Asset pool: slot ... has asset ...` for each asset it registers.
- Files that move through stages (shipment 18 to 21, single challan 22 to 25, write-off 26 to 28, sale 29
  and 30) share their progress through `utils/flow_stages.py`: a test asks for the stage it needs
  (`flow.reach("submitted")`) and any earlier stage that is not done yet is done first.
- Only one login can be open for an account at a time (ERP shows "Concurrent Login Problem" for a second
  one), so nothing else may be logged in as the test user while tests run, and the browser of the Claude
  Code Playwright server must be closed.

## Watching a run in the terminal
`pytest.ini` turns on `-s`, so every run prints, live and with or without a
browser window:
- a START line for each test with its position, e.g.
  `========== START [3/64]: test_list_grid_columns ==========`
- every action and check the test does, one line each (`[INFO] Click: Search button`)
- an END line with the result and the time,
  e.g. `========== END: test_list_grid_columns - PASSED in 2.5 seconds ==========`
The same lines are saved in `automation/logs/test_run.log`.

A single test can carry both `@pytest.mark.smoke` and
`@pytest.mark.regression` — it shows up in both `-m` runs without any
duplicated code.

## Where results go — every run gets its own dated folder
```
automation/reports/
└── 2026-09-17/
    └── 09-15-30/
        ├── Test_Report_2026-09-17_09-15-30.html   <- THE REPORT: send this file
        ├── allure-results/   (raw data the report is built from)
        ├── screenshots/      (passed/ and failed/, each with a folder per test; numbered 01_..., 02_... in the order taken)
        ├── traces/           (failed tests only, one .zip per failed test)
        └── downloads/        (reports exported by the tests)
```
Handled automatically by `conftest.py` / `utils/run_context.py` — you
never create these folders yourself.

## The HTML report (to share with the team)
At the end of every run, one file is created in the run folder:
`Test_Report_<date>_<time>.html`.
- **Double-click it** to open it in any browser. It works offline, needs no
  server and no installation, so it can be emailed or copied as it is.
- It shows every test with its result, the error message of a failed test, the
  numbered screenshots (including the last screen of each test), and for a
  failed test the trace file as a download.

### How it is made (automatic, nothing to run by hand)
When the last test of a run has finished, `conftest.py` (`pytest_sessionfinish`) calls
`generate_html_report()` in `utils/run_context.py`. It runs the Allure command-line tool on the
raw data of this run:
```
allure generate --single-file --clean automation/reports/<date>/<time>/allure-results -o automation/reports/<date>/<time>/report_temp
```
and moves `report_temp/index.html` to `automation/reports/<date>/<time>/Test_Report_<date>_<time>.html`.
The last line of the run prints the place: `HTML report: <path>`.

### What the PC needs
- **The Allure command-line tool**: `npm install -g allure-commandline` (needs Node.js).
  Check: `allure --version`.
- **Java 8 or newer** (any JDK, for example from adoptium.net) with the `JAVA_HOME` variable set to
  its folder. Check: `java -version`, and `echo %JAVA_HOME%` (Command Prompt) or `$env:JAVA_HOME` (PowerShell).

Without them the tests still run and pass or fail as usual; only the HTML report is missing.

### If the report was not created
1. Look at the end of the run for the line `HTML report NOT created: ...`.
2. **Do not run the tests again.** The raw data of that run is still in
   `automation/reports/<date>/<time>/allure-results/` (it holds the results, screenshots and traces).
3. Install Allure and Java (see "What the PC needs"). Then, from the project folder, in Command Prompt:
```
allure generate --single-file --clean automation\reports\<date>\<time>\allure-results -o automation\reports\<date>\<time>\report_temp
move automation\reports\<date>\<time>\report_temp\index.html automation\reports\<date>\<time>\Test_Report_<date>_<time>.html
rmdir /s /q automation\reports\<date>\<time>\report_temp
```
   Replace `<date>` and `<time>` with the folder names of that run, for example `2026-10-15` and `01-21-54`.
4. Another way: copy the `allure-results` folder to a PC that has Allure and Java, run the first
   command there and double-click `report_temp\index.html`.

## Traces (failed tests only)
A trace is a recording of the browser during a test: every action, a
screenshot at each step, the page's HTML at each step, network calls and
console messages. Open it to see exactly what happened before a failure.
- Each test records a trace while it runs. It is saved only if the test
  FAILED, as `traces/<test name>.zip`. A run where every test passes has no
  traces.
- Open one: `playwright show-trace automation/reports/<date>/<time>/traces/<test>.zip`
  or drag the .zip onto https://trace.playwright.dev (opened in your browser,
  the file is not uploaded).
- The same .zip is also attached to the failed test in the HTML report.

## Other views of a run
1. **Screenshots**: `automation/reports/<date>/<time>/screenshots/passed/<test name>/` (or `failed/`),
   e.g. `01_filter_popup_opened.png` ... and a last `NN_end_of_test_passed.png`
   (or `_FAILED`).
2. **Downloaded reports**: `automation/reports/<date>/<time>/downloads/`.
3. **Log**: `automation/logs/test_run.log`.

## Other folders worth knowing
- `automation/logs/test_run.log` — every action and assertion log line from
  every run, with timestamps.
- `automation/element_catalog/` — one readable file per page we have
  explored (what each element is, its locator, a screenshot).
- `automation/utils/` — helpers: `helpers.py` (unique names, random numbers,
  today / N days from today).

## Troubleshooting — something went wrong? Find your problem and its fix here
Find what you see in the left column and try the fix next to it.

| What you see | What to do |
|---|---|
| `BASE_URL not set` error | Check `.env` exists and `BASE_URL` is filled in |
| Browser not found | Run `playwright install chromium` |
| Login fails inside a test | Check credentials in `.env` are still current |
| A test is skipped unexpectedly | Check its `@pytest.mark` decorators match the `-m` filter you ran |
| HTML report not created at the end of a run | Install Allure (`allure --version` must work) and Java (`java -version`), then build the report from the finished run: see "The HTML report > If the report was not created" (no need to run the tests again) |
| Can't find today's screenshots | Check `automation/reports/<today's date>/` — a new time-folder is created every run |
| Playwright MCP not connected / UI exploration can't start | Check Node.js 18+ is installed, `.mcp.json` exists at the project root, and you approved the server; run `/mcp` to see its status |
| Agents not available in Claude Code | The `.claude/agents/` folder is missing or the files lack YAML frontmatter (`name`, `description`) |
| `ModuleNotFoundError` | Re-run `pip install -r requirements.txt`; check your virtual environment |

## Claude Code setup details
(Moved here from CLAUDE.md to keep that file small. Headings below are one level lower.)

#### 1. The `.claude/` folder must exist at the project root
Claude Code only auto-discovers subagents, skills, and permissions from
inside `.claude/`. A plain top-level `agents/` or `skills/` folder is not
enough on its own. Structure:
```
.claude/
├── agents/          ← one file per agent (7 total), registered as subagents
├── skills/          ← one <skill-name>/SKILL.md per skill, auto-discovered
└── settings.json    ← project permissions (shared with the team)
```
- **`.claude/agents/<name>.md`** — Markdown with YAML frontmatter
  (`name`, `description`, `tools` to restrict access, `model: inherit`,
  and optionally `skills:` listing the skill names — matching each
  skill's own `name:` field exactly — this agent relies on). The body
  below the frontmatter is the agent's system prompt.
- **`.claude/skills/<skill-name>/SKILL.md`** — the filename must be
  exactly `SKILL.md`; the folder name and the `name:` field in its
  frontmatter must match. Frontmatter needs at minimum `name` and a
  `description` written as a trigger ("use when...") — that description
  is what Claude uses to decide relevance, not just a title restatement.
- **`.claude/settings.json`** — allow the routine commands (pytest, pip,
  playwright, npx) and deny reading `.env`.
- Keep personal overrides in `.claude/settings.local.json` (git-ignored).
- Verify: the Agent tool's available-types list must include all 7 agent
  names, and the Skill tool's available-skills list must include all 8
  skill names. (The old `/agents` wizard has been removed — it now just
  prints a pointer to edit the files directly or ask Claude to do it.)

#### 2. Playwright MCP server must be configured (needed by `ui-explorer`)
This is separate from the Python `playwright` package in
`requirements.txt`. It is a Node.js package that lets Claude Code drive a
browser during UI exploration.
1. Prerequisite: Node.js 18+ (`node --version`). If missing, ask the user
   to install it.
2. Create `.mcp.json` at the **project root** (committed to git, so every
   team member gets the same setup):
   ```json
   {
     "mcpServers": {
       "playwright": {
         "command": "npx",
         "args": ["@playwright/mcp@latest"]
       }
     }
   }
   ```
   Equivalent CLI command: `claude mcp add playwright npx @playwright/mcp@latest`
3. Claude Code asks for approval the first time it sees a project-scoped
   MCP server — the user approves it once.
4. Verify: `/mcp` inside Claude Code (or `claude mcp list` in a terminal)
   must show `playwright` as connected. If the MCP browser is missing, let
   the MCP server install it, or run `npx playwright install chromium`.
- Never start UI exploration until this check passes. If it fails, stop
  and tell the user exactly what is missing — do not guess locators
  instead.
