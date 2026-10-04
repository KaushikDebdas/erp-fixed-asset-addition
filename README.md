# AI SQA Framework

CR/SRS → test cases written exactly per the team's own `skills/
test-case-writing.md` standard (single Excel, edited directly) → uploaded
to Zephyr as-is → independently, UI-verified Playwright + Python (POM)
automation, including multi-role end-to-end flows → execution → dated
Allure/HTML report. Built for use with Claude Code as the orchestrator.

## Two independent tracks — no shared ID system
- **Test case generation** ends when you review/edit the Excel and
  upload it to Zephyr yourself.
- **Automation** is separate: single rows marked `Automation Suitable =
  Yes`, an ad-hoc flow instruction, or a documented multi-role journey in
  `e2e-flows/`. See `CLAUDE.md` → "Why no shared TC ID."

## Framework root — Claude Code setup files
```
ai-sqa-framework/
├── .claude/       ← agents/ (registered subagents) + settings.json
└── .mcp.json      ← Playwright MCP server config
```
Both are created during the one-time setup below.

## Project folder
```
projects/addons/
├── project_config.yaml
├── cr/            ← CR/SRS documents
├── domain-docs/   ← domain reference material, any format
├── test-cases/    ← Test_Case_<JIRA-ID>.xlsx — edited in place
└── e2e-flows/     ← multi-role, multi-step journey documentation
```

## One-time setup (before first use)
Claude Code needs two things that are easy to miss:
1. **The `.claude/` folder** at the project root — `agents/` (the 7 agents
   registered as subagents), and `settings.json` (permissions). Without it,
   Claude Code will not discover the agents on its own.
2. **The Playwright MCP server** configured in `.mcp.json` at the project
   root (requires Node.js 18+) — used by the UI Explorer agent. This is
   separate from the Python `playwright` package.

Exact contents and verification steps (`/agents`, `/mcp`) are in
`CLAUDE.md` → "Claude Code Setup". You can simply ask Claude Code to set
these up on first run.

## Start here
1. Read `CLAUDE.md` first.
2. `skills/test-case-writing.md` — the real, detailed standard this whole
   framework is built around: exact 11-column schema, a `Test Case Type`
   column (`Positive`/`Negative`/`Edge Case`/`Business`/`Out of Scope` —
   Folder stays a plain feature path), ~100-cases-per-story volume
   target, fixed defaults, exact `.xlsx` formatting, plus a Bug Report
   format and a Banglish-in/
   English-out communication rule.
3. `skills/e2e-automation-flows.md` — for journeys that span multiple
   pages, roles, and carry data between steps (e.g. HOFIN create → HOFA
   approve → HOFIN acknowledge). See `templates/e2e_flow_template.md` and
   the filled example in `projects/addons/e2e-flows/`.
4. `templates/TestCases_template.xlsx` — the team's exact 11 columns
   (including `Test Case Type`) plus 3 appended for this framework
   (`Automation Suitable`, `Automation Reason`, `Suite`) — delete those 3
   before uploading to Zephyr.
   `templates/BugReport_template.xlsx` — the bug report format.
5. `automation/` — Playwright + pytest + POM skeleton. Tests organized by
   feature, not suite — smoke/regression is a pytest marker.
6. `automation/HOW_TO_RUN.md` — commands, and where every run's dated
   results (`automation/reports/<date>/<time>/`) end up.

## Recommended first milestone
```
1 CR (e.g. a slice of one Jira story)
  → Business Analyst agent → business_knowledge/
  → your review
  → Test Case Generator agent → test-cases/Test_Case_<JIRA-ID>.xlsx
    (per skills/test-case-writing.md, with Automation Suitable/Reason/Suite)
  → your review/correction, in place
  → you upload to Zephyr (independent)
  → separately: point at Yes-marked rows, or describe a flow, or write an
    e2e-flows/ journey → UI Explorer → temporary mapping →
    Automation Engineer → well-commented Playwright test(s)
  → Test Reporter agent → pytest run → dated report in automation/reports/
```