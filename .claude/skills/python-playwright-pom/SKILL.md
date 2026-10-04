---
name: python-playwright-pom
description: Use when writing or organizing Playwright automation code — defines the automation/ folder layout, the simple beginner-friendly Page Object Model, helper functions, smoke/regression pytest markers, multi-role end-to-end flow structure, and the mandatory commenting standard.
---

# Skill: Python + Playwright POM Conventions

## Golden rule
Write code a new team member can read on day one. Plain functions, plain
classes, short methods. No decorators, no metaclasses, no generated
locators, no clever one-liners. If a line needs thought to understand, add a
comment explaining WHY it is there.

## Folder convention
```
automation/
├── pages/                # one class per page + base_page.py
├── tests/                # feature-organized, numbered: test_01_login.py
├── element_catalog/      # PERMANENT record of every page/element seen
├── automation_mapping/   # temporary review JSON, per automation-mapping skill
├── test_data/
├── utils/                # logger, run_context, helpers
├── config/               # settings.py reads .env
├── logs/                 # test_run.log (written by utils/logger.py)
├── reports/              # dated Allure results/screenshots/traces/HTML report
├── conftest.py
└── HOW_TO_RUN.md
```

## Browser rule
Always headed and maximized: `launch(headless=False, args=["--start-maximized"])`
plus `new_context(no_viewport=True)` (see `conftest.py`). No fixed viewport, so
it fills any screen.

## Page Object rules
1. One class per page in `pages/<page>_page.py`. It inherits `BasePage`
   (`pages/base_page.py`), which holds the common actions (open, click,
   type_text, get_text, is_visible, wait_until_visible).
2. Locators are defined ONCE, in `__init__`, each with a one-line comment
   saying what the element is.
3. Methods are business actions (`login`, `submit_voucher`), not raw clicks.
   Every method has a docstring saying what it does and why.
4. Tests only call page methods. No locators and no raw Playwright calls in
   test files.
5. Check `pages/` for an existing class/method before writing a new one.
   Shared UI (nav bar, common modal) goes in `common_components.py`.
6. Locators come from `ui-explorer`'s verified mapping and
   `element_catalog/<page>.md`. Never guess one. If a step is
   `LOCATOR_REQUIRES_REVIEW`, stop and flag it.
7. When a locator changes, update the page class AND the catalog file.

## Reference examples (copy their style)
- `pages/base_page.py`, `pages/login_page.py`
- `tests/test_01_login.py`

## Helpers — reuse before writing new ones
- `utils/helpers.py` (data): `unique_name("Voucher")`, `random_number(6)`,
  `random_text(8)` — values that must differ every run.
- `utils/helpers.py` (dates): `today()`, `days_from_today(7)` — never hardcode
  a date. Add a calendar-picking helper only after exploring the real widget.
- `utils/logger.py`: `action_logger` (did the action work?) and
  `assertion_logger` (did the business outcome happen?).
- New helper? Add it to the matching section of `utils/helpers.py`, 5–15 lines, a
  docstring with an example of use, and no dependency on any page class.

## Screenshots, failure reasons and traces in tests
Every test must leave enough evidence in the report for someone who was not
there. Full rules: the `logging-reporting` skill.
- **Screenshots:** add the `take_screenshot` fixture to the test and call it at
  each important step with a short description of what the screen shows:
  `take_screenshot("filter popup filled")`. Files are numbered in the order
  taken, one folder per test:
  `reports/<date>/<time>/screenshots/<test name>/03_filter_popup_filled.png`,
  and are attached to the HTML report. The framework adds the last screenshot
  (`NN_end_of_test_passed` / `_FAILED`) itself. Never take screenshots with raw
  `page.screenshot(...)` in a test.
- **Failure reasons:** when a test checks a message or value, the check must
  say what it expected and what it actually found, so the failure explains
  itself. Put these checks in the page object (for a message popup: compare the
  exact text, fail if a different message or none appears, and include the
  message that was on screen in the failure text). Never write a bare
  `assert x` that fails with no explanation.
- **Traces:** each test records a trace, saved only if the test fails and
  attached to the HTML report. If a test file shares one browser tab across its
  tests, record one trace chunk per test (`context.tracing.start_chunk(...)` at
  the start, `stop_chunk(path=...)` for a failed test or `stop_chunk()` for a
  passed one, in the file's `page` fixture), so each failure has its own trace.
- **Report files:** do not edit the report setup (`utils/run_context.py`,
  the report hooks in `conftest.py`) when writing a test. The single-file HTML
  report is built automatically at the end of every run.

## Smoke/Regression via markers, not folders
```python
@pytest.mark.smoke
@pytest.mark.regression
def test_login_with_valid_credentials(login_page):
    ...
```
Assign markers from the Excel's **Suite** column. Test files are numbered in
run order (`test_01_login.py`, `test_02_income_statement.py`) and
named by feature, never by suite.

## Multi-role end-to-end flows
- One browser context per role — never share a session across roles.
- Capture data produced early (e.g. a voucher reference number) into a
  variable and pass it explicitly into later steps.
- Break a long flow into named helpers per role/stage
  (`create_voucher_as_hofin`, `approve_voucher_as_hofa`), called in order by one
  test function.

## Page loading rule
Every action that opens or changes a page (open a URL, click Sign In, click a
menu item that loads a new page) must be followed by `wait_for_page_load()`
(in `pages/base_page.py`), so the next step starts only when the page is fully
loaded. `open()` already does this. Then wait for the specific element the next
step needs (`wait_until_visible`, or a loading message to disappear) instead of
sleeping for a fixed time. Do not use `networkidle`: this application keeps
background requests running and it never settles.

## Mandatory commenting standard
The finished code must read as complete documentation for anyone, a year from now.
- File docstring at the top of every `.py` file: what this file is and when to
  use it.
- Every class and function/method gets a docstring that says WHAT it does,
  what it returns, and an example if useful.
- Inline comments describe what the next line or step does, in plain words
  (`# Step 2: click the x button`).
- Do NOT write comments about how the code was developed or debugged: no
  attempt counts, no "this used to fail", no workaround stories, no tool
  or version history. If the code needs a retry or a special wait, give the
  constant a clear name and say only what it is (`# Maximum time to wait for
  the report`), never why it was added.
- Test bodies use numbered step comments: `# Step 1: ...`, `# Step 2: ...`.
- Each test's docstring names the scenario/flow it covers.
- Never log passwords or other secrets.
