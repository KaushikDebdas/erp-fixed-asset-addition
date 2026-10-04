---
name: dependency-management
description: Run before any setup, automation, or execution task — checks installed versions (Python, Playwright, pytest, allure-pytest, python-dotenv, Node.js, the Allure command-line tool and Java) and the .claude/ + Playwright MCP setup before installing or reinstalling anything.
---

# Skill: Dependency Management

Run this check before any setup, automation, or execution task.

## Steps
1. Check what's already installed and its version (Python, Playwright,
   pytest, allure-pytest, python-dotenv) and Node.js (`node --version`,
   18+ required for the Playwright MCP server).
   Also check the Allure command-line tool (`allure --version`) and Java
   (`java -version`): they are needed to build the shareable HTML report at
   the end of a run, and are installed on the machine, not through
   `requirements.txt`. If missing, tell the user; tests still run but no HTML
   report is created.
2. If installed version satisfies `requirements.txt` — do nothing,
   proceed.
3. If missing — install only that missing package.
4. After installing, verify with an import check or `--version`.
5. If Playwright browsers are needed, check first whether they're already
   present before re-downloading.
6. If elevated permission is required, stop and ask before proceeding.
7. Confirm the Claude Code setup exists (see `CLAUDE.md` → "Claude Code
   Setup"): the `.claude/` folder (`agents/`, `skills/`, `settings.json`)
   and the Playwright MCP server in `.mcp.json`. If either is missing,
   create it. Verify the Agent tool's available-types list includes all 7
   project agents and the Skill tool's listing includes all 9 project
   skills (or `/mcp` / `claude mcp list` for the MCP server) —
   `playwright` must show as connected before any UI exploration.
8. Log installs/changes to `projects/<project>/CHANGELOG.md`.

## Never
- Reinstall an existing compatible package "just to be safe."
- Install a dependency that isn't actually needed for the current task.
- Overwrite an existing config file without showing the diff and
  confirming first.
- Print credentials, tokens, or `.env` contents to logs or terminal
  output.
