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

## Which Python runs the tests
Use this project's own `.venv` (it has `pypdf`, which the voucher checks need). Other projects on
this PC have a `.venv` too and the prompt shows `(.venv)` for all of them, so check first:
```
cd D:\fixedasset-automation
where pytest          (the first line must be D:\fixedasset-automation\.venv\Scripts\pytest.exe)
```
Safest command, from `D:\fixedasset-automation`, with no activation needed:
```
.venv\Scripts\python.exe -m pytest automation/tests/test_05_generate_barcode.py
```
If the run stops at once with "pypdf is not installed in this Python (...)", the terminal is using
another project's Python: run `deactivate`, then `.venv\Scripts\activate` in this folder.

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
| usage_a (Draft + Submit path) | furniture spot | Assign, Acknowledge, Internal Movement, Un Assign, Expense, then Write-off (test_10 to 13, 16, 27 to 29) |
| usage_b (Submit-only path) | furniture gift | Assign, Internal Movement, Un Assign, Expense, then Write-off (test_10, 12, 13, 16, 27) |
| split_land | land spot | Asset Serial Split (test_07 to 09) |
| transfer_a | furniture spot | Asset Shipment (test_19 to 22) |
| challan_a / challan_b | furniture spot / gift | Asset Single Challan, Draft path / Submit-only path (test_23 to 26) |
| sale_profit_a / sale_profit_b | building spot / gift | Asset Sale above the Written Down Value, Draft / Submit (test_30, 31) |
| sale_loss_a / sale_loss_b | laptop spot / gift | Asset Sale below the Written Down Value, Draft / Submit (test_30, 31) |
| reg_draft / reg_pending | desktop spot / furniture spot | stay a Draft / stay PENDING (registration tests) |

- **A full run** (`pytest`): tests 01 to 03 register and approve the slot assets once, the later
  tests find them in the pool and reuse them, so an asset is never created twice. An asset a flow uses
  up (sold, split, in a challan, written off) is taken out of the pool.
- **One test alone** (for example `pytest tests/test_30_asset_sale.py -k loss_submit`): the pool is
  empty, so the test registers and approves exactly the asset it needs, then uses it. No test depends on
  another having run.
- The assets exist only for the run (nothing is saved between runs), so every run starts with new assets.
  The log shows `Asset pool: slot ... has asset ...` for each asset it registers.
- Files that move through stages (shipment 19 to 22, single challan 23 to 26, write-off 27 to 29, sale 30
  and 31) share their progress through `utils/flow_stages.py`: a test asks for the stage it needs
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
- Creating it needs the Allure command-line tool and Java on the machine that
  RUNS the tests (check: `allure --version` and `java -version`). If either is
  missing, the tests still run and the run prints "HTML report NOT created".

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
| HTML report not created at the end of a run | Install Allure (`allure --version` must work) and Java (`java -version`), then run again |
| Can't find today's screenshots | Check `automation/reports/<today's date>/` — a new time-folder is created every run |
| Playwright MCP not connected / UI exploration can't start | Check Node.js 18+ is installed, `.mcp.json` exists at the project root, and you approved the server; run `/mcp` to see its status |
| Agents not available in Claude Code | The `.claude/agents/` folder is missing or the files lack YAML frontmatter (`name`, `description`) |
| `ModuleNotFoundError` | Re-run `pip install -r requirements.txt`; check your virtual environment |
