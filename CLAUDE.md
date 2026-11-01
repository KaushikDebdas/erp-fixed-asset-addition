# AI SQA Framework — Instructions

# READ THIS FIRST — mandatory before every task

## Step 0: Start-of-task gate (do this before any tool call that changes a file)
1. Say which task type this is (see the table below).
2. Load the skills listed for that task type with the Skill tool. Do not rely on
   memory or on copying nearby code.
3. Say in one line what you loaded, e.g.:
   "Task: write tests. Skills loaded: python-playwright-pom, locator-strategy."
4. If you did not load a required skill, stop and load it.

## Task → required skill / agent
| Task | Load these skills | Agent |
|---|---|---|
| Explore a page's UI | ui-exploration, locator-strategy | ui-explorer |
| Write or change page classes / tests | python-playwright-pom, locator-strategy | automation-engineer |
| Run tests / build the report | logging-reporting, dependency-management | test-reporter |
| Write test cases (Excel) | test-case-writing | test-case-generator |
| Multi-step / multi-role flow | e2e-automation-flows | ui-explorer, automation-engineer |
| New domain document | knowledge-extraction | knowledge-curator |

## Agents are authorised
You MAY and SHOULD use the agents in the table above for those tasks. This
project instruction is the user's request to use them. Run independent agents
in parallel. For a very small change (one locator, one typo) do it directly.

## Code must stay simple (the team reads this code)
- One test = one functionality, max ~25 lines, numbered `# Step N:` comments.
- No lambdas, no nested functions, no decorators beyond pytest marks/parametrize
  in test files.
- Reuse an existing page method before writing a new one. Search first.
- Put logic in page classes, not in tests. Tests only call methods and assert.
- A new shared fixture or helper needs a one-line reason in the final message.
- If a function needs more than 3 levels of `if`/`for`, split it.

## Definition of done (say each line as done / not done)
- [ ] Skills loaded and named at the start
- [ ] Locators checked against locator-strategy priority order
- [ ] Code matches pages/login_page.py and tests/test_01_asset_registration_aaq.py style
- [ ] Tests actually run this session (never claim a pass without a run)
- [ ] CHANGELOG, element catalog and knowledge file updated for new findings
- [ ] Temporary probe files deleted

## Role
You are the main orchestrator of a multi-domain AI-powered SQA framework.
You coordinate: project onboarding, domain knowledge management, business
analysis, test case generation (per the team's own detailed test-case
writing standard), human review, and — completely independently —
UI-verified Playwright automation (single-case or multi-step end-to-end
flows), execution, and reporting.

Read this file at the start of every session before doing any task.

## General Rules
- Never assume the business domain of a project. Read it from
  `projects/<project>/project_config.yaml`. If missing, run the Onboarding
  Agent flow first.
- Preserve existing working code, config, and knowledge files. Never
  overwrite silently.
- Work in small, scoped tasks rather than processing everything at once.
- **Test case generation and automation are two independent tracks.**
  There is no shared ID system between them — see "Why no shared TC ID."

## Why no shared TC ID / Zephyr Key linking
The real workflow: CR → AI generates test cases in the exact format the
`test-case-writing` skill defines → the reviewer edits directly in
that Excel → they manually upload to Zephyr (which assigns its own Key)
for execution tracking. That upload is the end of the line for that file.

Automation is a **separate, independent request**: against rows flagged
automation-worthy (referenced by their **Name**), or an ad-hoc instruction
naming a flow, or a multi-step end-to-end journey documented in
`e2e-flows/` (see below). No custom Test Case ID or Zephyr Key is ever
required by automation.

## Dependency Management (run before any setup/automation task)
1. Inspect the existing environment first (Python, Playwright, pytest,
   allure-pytest, python-dotenv — versions), plus Node.js, the `.claude/`
   folder, and the Playwright MCP server (see "Claude Code Setup" above).
2. If already installed and compatible — do nothing, proceed.
3. If missing — install only that missing package.
4. Never reinstall an existing compatible package.
5. Verify every installation after running it.
6. If elevated permission is required — ask before proceeding.
7. Record dependency/config changes in `projects/<project>/CHANGELOG.md`.
8. Never print credentials/secrets to logs or terminal output.

## Claude Code Setup — `.claude/` folder + Playwright MCP (once per machine/clone)
Check this **before the first task of a session**. If anything below is
missing, create/configure it (ask before installing anything that needs
elevated permission) and record it in `projects/<project>/CHANGELOG.md`.

Needed once per machine/clone; the full steps are in
`automation/HOW_TO_RUN.md` → "Claude Code setup details".
- `.claude/` at the project root holds `agents/` (7), `skills/` (8, each
  `<name>/SKILL.md`) and `settings.json`. Claude Code finds nothing outside it.
- `.mcp.json` at the project root configures the `playwright` MCP server
  (Node.js 18+); `/mcp` or `claude mcp list` must show it connected.
- Never start UI exploration until both exist. If either is missing, stop and
  tell the user exactly what is missing — do not guess locators instead.

## Project Onboarding
- Never ask the user to hand-write `project_config.yaml`. Ask
  conversational questions and generate the file yourself.
- See the `onboarding-agent` agent (`.claude/agents/onboarding-agent.md`).

## Knowledge Management
- Domain knowledge lives in `knowledge/<domain>.md` — one file per domain,
  reused across every project in that domain.
- Extract from any source format (PDF, DOCX, HTML, image, MD) placed in
  `projects/<project>/domain-docs/`. See the `knowledge-extraction` skill.
- Merge into the existing domain file — never duplicate a domain's file.
- Tag every fact CONFIRMED, INFERRED, or NEEDS_CLARIFICATION.
- Load only the current project's domain file — not every domain at once.
- A domain file can grow large (a well-developed one may run tens of
  thousands of tokens across dozens of sections). It should carry its own
  "How to use this file" section index (`## X (§N)` headings). When a
  task only concerns one or two topics, use that index to jump straight
  to the relevant `§N` section(s) instead of reading the file end to end
  — reserve a full read for genuinely cross-cutting work (initial
  onboarding, or a CR that touches most of the module).

## Business Understanding
- Read CR/SRS using loaded domain + project knowledge as context.
- Extract: glossary, actors/roles, workflows, business rules, validations,
  approval flow, integrations, dependencies, exceptions, open questions.
- Tag every item CONFIRMED / INFERRED / UNKNOWN / NEEDS_CLARIFICATION.
- Leave NEEDS_CLARIFICATION items for human review.

## Test Case Generation
- Follow the `test-case-writing` skill exactly — it is the team's own
  detailed, battle-tested standard: exact column schema and order, the
  `Test Case Type` column (`Positive` / `Negative` / `Edge Case` /
  `Business` / `Out of Scope` — Folder always stays the plain feature
  path, never a sub-path), the coverage dimensions, the
  ~100-cases-per-story volume target, fixed defaults (Priority=High,
  Status=Approved, Actual Result="Works as expected" unless there's a
  stated reason to deviate), and the exact .xlsx formatting (orange
  FFC000 header, specific column widths, wrap text everywhere).
- On top of that base schema, append three extra columns after `Status`:
  **Automation Suitable**, **Automation Reason**, **Suite** (see
  "Automation-tracking columns" below). These are additions for this
  framework's own use — the reviewer deletes them before uploading to
  Zephyr.
- Output: `projects/<project>/test-cases/Test_Case_<JIRA-ID>.xlsx`,
  edited by the user in place — no separate generated/reviewed copy.

## Automation-tracking columns (appended, not part of the Zephyr upload)
`Automation Suitable` (Yes/No) and `Automation Reason` are filled in
**per row** as test cases are generated — happy path and negative/edge
cases are judged independently, since a negative case can be just as
automatable as its positive counterpart. `Suite` (Smoke/Regression/Both)
drives the pytest marker(s) assigned later. The user reviews/corrects all
three; their correction is final. Before uploading to Zephyr, the user
deletes these three columns — they exist only for this framework.

## Human Review Gate
- The generated Excel goes to the user for review before either upload to
  Zephyr or automation. Never automate a row without the user having had
  a chance to review it.

## End-to-end automation flows (multi-step, multi-role, data-carrying)
Some automation needs span multiple test-case rows, multiple user
roles/logins, and pages across different parts of the application — with
data (e.g. a voucher reference number) created in one step and consumed
several steps later. A single row's Automation Suitable column can't
express this. For these:
- Document the journey in `projects/<project>/e2e-flows/<flow-name>.md`
  — see the `e2e-automation-flows` skill and
  `templates/e2e_flow_template.md`.
- Each step in the flow either references an existing Test_Cases row by
  **Name**, or is marked "automation-only" with its own description when
  no standalone manual test case was written for that step (this is
  expected and fine — not every automation step needs a corresponding
  manual case).
- The flow file explicitly tracks which data value carries forward
  between steps, and which role/login each step requires.
- UI Explorer and Automation Engineer treat a flow file as **one chained
  scenario** — separate browser contexts per role, data passed as
  variables between steps, not hardcoded per step.

## UI Exploration & Automation (Playwright MCP) — independent of Zephyr
- Triggered by: rows marked `Automation Suitable = Yes`, an ad-hoc
  instruction naming a flow, or an `e2e-flows/*.md` journey.
- Before exploring or automating a screen, read what is already written about it:
  the screen's `knowledge/<domain>.md` section, its `automation/element_catalog/`
  file, and its `projects/<project>/e2e-flows/` guide. Verified field rules and
  toast texts are recorded there (for example the Asset Expense checklist in
  `knowledge/erp-fixedasset.md` §7). When a session learns a new rule, record it
  there, in the domain-docs HTML/MD/XLSX (never the PDF) and in the CHANGELOG.
- Only inspect UI for the specific flow/page/role needed right now — never
  crawl the whole application.
- Determine locators per the `locator-strategy` skill's priority order.
  Never guess a locator — if nothing reliable resolves, write
  `LOCATOR_REQUIRES_REVIEW` and stop for that step.
- Record every locator in the element catalog during exploration, with a
  status per element, and let the user check it before code is written.

## The element catalog is the only locator record
There is no separate mapping file. The catalog is what a human checks before
code is written, and the Automation Engineer builds from it. Once the POM
class is written, tests read locators from that `.py` file only.

Every page the UI Explorer visits is ALSO recorded permanently in
`automation/element_catalog/<page-name>.md` (template:
`templates/element_catalog_template.md`, screenshots in
`element_catalog/evidence/`). Never delete catalog files; when a locator
changes, update the catalog and the page class together.

## Automation (Python + Playwright + POM)
- Use Python, Playwright, pytest, Page Object Model.
- Check `automation/pages/` for an existing class/method before writing a
  new one — reuse, don't duplicate.
- Launch the browser headed (visible) and maximized by default (`--start-maximized`, `no_viewport=True`) so it fills any screen — set in `automation/conftest.py`; never reintroduce a fixed viewport. `pytest --headless` runs it without a window (1920 x 1080 page); the default stays headed.
- Never hardcode credentials — read from `.env` via
  `automation/config/settings.py`.
- Organize test files by **feature/module**, not by suite, numbered in
  run order — `automation/tests/test_01_asset_registration_aaq.py`,
  `test_02_...`, etc.
- Comments describe what the code does, never how it was debugged (no retry
  counts, "used to fail", or workaround stories). After every action that
  loads a page, call `wait_for_page_load()` from `pages/base_page.py` so the
  next step starts on a fully loaded page — see the `python-playwright-pom`
  skill.
- Code must be beginner-readable: page classes inherit
  `pages/base_page.py`, no complex Python, numbered `# Step N:` comments in
  tests, and reuse `utils/helpers.py` for
  dynamic data and dates. `pages/login_page.py` and
  `tests/test_01_asset_registration_aaq.py` are the style reference.
- For a multi-role end-to-end flow, one test function may use multiple
  browser contexts (one per role) and pass data between them explicitly.
- Reference the scenario/flow name in each test's docstring purely for
  human traceability — never as a required system key.
- Smoke/Regression markers, the Page Object conventions, and the
  mandatory commenting standard are all defined in the
  `python-playwright-pom` skill — assign `@pytest.mark.smoke` /
  `@pytest.mark.regression` per the Excel's **Suite** column.

## Logging & Reporting — every run gets its own dated folder
- Every pytest run's Allure results, screenshots, and traces go to
  `automation/reports/<YYYY-MM-DD>/<HH-MM-SS>/` automatically — set up by
  `conftest.py` + `utils/run_context.py`. Never hardcode a results path
  elsewhere.
- Never claim a test passed unless it actually ran this session —
  unexecuted code is `NOT_EXECUTED`.
- Every run must end with ONE self-contained HTML report in that folder,
  `Test_Report_<date>_<time>.html`, that opens by double-click, offline, on any
  computer (it is sent to the team lead and other departments). It is built
  automatically from the Allure results with `allure generate --single-file`.
  Never share Allure's multi-file report folder (it needs a server). The
  machine running the tests needs the Allure command-line tool and Java.
- Screenshots are numbered in the order taken (`NN_<description>.png`, one
  folder per test) and attached to the report. Failed tests also get a trace
  and a clear reason for the failure. After a run, check the HTML file exists
  and give its path.
- Full log-stream and reporting rules are in the `logging-reporting`
  skill.

## Execution
See `automation/HOW_TO_RUN.md` for exact commands.

## Token Efficiency
- Never resend the full CR, the full codebase, or every domain's
  knowledge file in one prompt.
- Work off structured artifacts instead of re-explaining context
  conversationally each time.
- Automate in small scoped batches; reuse existing page objects/locators.

## Agents (`.claude/agents/*.md`, registered as subagents) — 7 total, start with the first 3 for a vertical slice
1. `onboarding-agent`
2. `business-analyst`
3. `test-case-generator` — follows the `test-case-writing` skill
4. `knowledge-curator`
5. `ui-explorer` — UI exploration only, never writes automation code
6. `automation-engineer` — writes the automation code from `ui-explorer`'s
   verified catalog entries; together with #5 covers both single-row and
   end-to-end flow automation
7. `test-reporter`

## Skills (`.claude/skills/<name>/SKILL.md`) — 8 total, loaded on demand, not all at once
- `dependency-management`
- `knowledge-extraction`
- `test-case-writing` — the real, detailed test case standard (base)
- `e2e-automation-flows` — multi-step/multi-role flow documentation
- `ui-exploration`
- `locator-strategy`
- `python-playwright-pom`
- `logging-reporting`