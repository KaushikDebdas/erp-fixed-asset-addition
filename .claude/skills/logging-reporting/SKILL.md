---
name: logging-reporting
description: Use when executing automated tests or building the test report — defines the two separate log streams (technical action log vs business assertion log), the per-run dated results folder, the shareable single-file HTML report, numbered screenshots, failure traces, and what data to capture per step.
---

# Skill: Logging & Reporting

## Two separate log types (never merge these)
**A. Technical action log** — did the Playwright action itself succeed?
```
[INFO] Add voucher with valid reference number
[INFO] Filling Reference Number field
[PASS] Reference Number field filled successfully
```
**B. Business assertion log** — did the expected business outcome
actually happen?
```
[INFO] Verifying save confirmation
[PASS] Save confirmation displayed
```
A successful click/fill action does NOT mean the business test passed.

## Every run gets its own dated folder
`automation/reports/<YYYY-MM-DD>/<HH-MM-SS>/` holds everything from that run,
set up automatically by `conftest.py` + `utils/run_context.py`. Never write
these to a flat, shared folder. See `automation/HOW_TO_RUN.md`.
```
<HH-MM-SS>/
├── Test_Report_<date>_<time>.html   <- the shareable report
├── allure-results/                  (raw data the report is built from)
├── screenshots/passed/<test name>/NN_<description>.png   (tests that passed)
├── screenshots/failed/<test name>/NN_<description>.png   (tests that failed)
├── traces/<test name>.zip           (failed tests only)
└── downloads/                       (files exported by tests)
```

## The shareable HTML report (mandatory, automatic)
- Every run must end with ONE self-contained HTML file in the run folder,
  `Test_Report_<date>_<time>.html`, built from that run's `allure-results/`
  with `allure generate --single-file`. It is created by
  `generate_html_report()` in `utils/run_context.py`, called from
  `pytest_sessionfinish` in `conftest.py`.
- It must open by double-click, offline, on any computer, with no server and no
  installation, because it is sent to the team lead and other departments.
  Never hand over Allure's default multi-file report folder: it needs a web
  server and shows nothing when opened from disk. Never send `allure-results/`.
- Contents: every test with its result, the error message of a failed test,
  the numbered screenshots, an Environment box (application URL, environment,
  browser; never credentials), and for a failed test its trace.
- The machine that RUNS the tests needs the Allure command-line tool and Java
  (`allure --version`, `java -version`). If either is missing the tests still
  run, the run prints "HTML report NOT created", and you must say the report
  was not created. Never claim a report exists without checking the file.

## Screenshots
- Every screenshot is numbered in the order it was taken and named for what
  the screen shows: `screenshots/passed/<test name>/01_filter_popup_opened.png`.
- Screenshots are sorted by result so a reader sees the failures at once: the
  folder of a test that passed is in `screenshots/passed/`, the folder of a test
  that failed is in `screenshots/failed/`. This is done automatically after each
  test by `sort_screenshots_by_result()` in `utils/run_context.py`, called from
  `pytest_runtest_makereport` in `conftest.py`. A test never builds these paths.
- A test takes one at each important step with the `take_screenshot` fixture:
  `take_screenshot("filter popup opened")`. Use a short description of what
  the screen shows at that moment.
- The last screen of every test is taken automatically
  (`NN_end_of_test_passed` or `NN_end_of_test_FAILED`).
- Every screenshot is also attached to the Allure report under the same
  number and name.

## Traces
- A trace is a recording of the browser during a test: every action, a
  screenshot and the page HTML at each step, network calls and console
  messages.
- One trace is recorded per test and saved ONLY if the test failed, as
  `traces/<test name>.zip`. A run where every test passes has no traces.
  When several tests share one browser tab, record one trace chunk per test
  (`tracing.start_chunk` / `stop_chunk`) so each failure has its own trace.
- The trace is also attached to the failed test in the HTML report.
- Open one with `playwright show-trace <file>.zip`, or drag it onto
  https://trace.playwright.dev (the file is not uploaded).

## Failure reasons
A failure must say why. An assertion about a message or value states what was
expected and what was actually found (for a message popup, the exact text that
was on screen, or that none appeared). When a test fails, the message that was
on screen is written to `logs/test_run.log`, and the failure screenshot and
trace show the rest.

## Per-step data to capture
Timestamp, scenario/flow name, step number, action, target, result, error
message (if any), screenshot path, trace reference (on failure).

## Tooling
- Python `logging` module for the two log streams above (written to the
  terminal and to `automation/logs/test_run.log`).
- `pytest` for execution + markers (`smoke`, `regression`).
- `allure-pytest` for the structured results, and the Allure command-line tool
  (with Java) to build the single-file HTML report.
- Playwright's built-in tracing for failure traces.

## Reporting rules
- Never claim a test passed unless it was actually run this session.
- Every failure gets its final screenshot, its trace, and the reason it failed.
- The report should let someone map a failure back to its scenario/flow
  name without cross-referencing another file.
- After a run, check that the HTML report file exists and give its path.
