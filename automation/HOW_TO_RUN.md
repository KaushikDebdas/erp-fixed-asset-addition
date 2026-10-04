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
   `agents/` and `settings.json`). If not, ask Claude Code to create it —
   see `CLAUDE.md` → "Claude Code Setup". Check with `/agents` inside
   Claude Code.
7. Make sure the Playwright MCP server is configured: `.mcp.json` at the
   project root must contain the `playwright` server, or run
   `claude mcp add playwright npx @playwright/mcp@latest`. Approve it when
   Claude Code asks, then check with `/mcp` (or `claude mcp list`) —
   `playwright` must show as connected.

## Running tests

| Command | What it does |
|---|---|
| `pytest -m smoke` | Runs only smoke-tagged tests |
| `pytest -m regression` | Runs only regression-tagged tests |
| `pytest -m "smoke or regression"` | Runs both suites |
| `pytest -k test_valid_login` | Runs one specific test by name |
| `pytest tests/test_01_login.py` | Runs all tests in one file |
| `pytest -v` | Verbose — shows each test name as it runs |
| `pytest --headed` | Runs with the browser visible (debugging) |

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
        ├── screenshots/      (a folder per test; numbered 01_..., 02_... in the order taken)
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
1. **Screenshots**: `automation/reports/<date>/<time>/screenshots/<test name>/`,
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
| Agents not listed in `/agents` | The `.claude/agents/` folder is missing or the files lack YAML frontmatter (`name`, `description`) |
| `ModuleNotFoundError` | Re-run `pip install -r requirements.txt`; check your virtual environment |
