---
name: e2e-automation-flows
description: Use when automation needs span multiple test-case rows, user roles/logins, or pages, with data created in one step and consumed several steps later (e.g. a voucher reference number) — documents the journey as one chained scenario in projects/<project>/e2e-flows/<flow-name>.md instead of a single row's Automation Suitable column.
---

# Skill: End-to-End Automation Flows (multi-step, multi-role, data-carrying)

## When to use this instead of a single row's Automation Suitable column
A single Test_Cases row can express "this one step is automatable." It
cannot express a business journey that spans multiple pages, multiple
user roles/logins, and data created in one step that must be reused
several steps later. Use a flow file whenever automation needs to chain
more than one such step together.

**Example** (real scenario): HOFIN user logs in and creates a voucher →
HOFA approver logs in, finds that same voucher, approves it → HOFIN user
logs back in and acknowledges the approval → HOFIN performs a follow-up
action on the now-acknowledged voucher. Four steps, two roles, one data
value (the voucher reference number) threaded through all of them, in a
fixed order.

## Where flow files live
`projects/<project>/e2e-flows/<flow-name>.md` — one file per journey.
See `templates/e2e_flow_template.md` for the exact structure to copy.

## What goes in a flow file
- **Business scenario** — one or two sentences describing the journey.
- **A step table**: Step number, Role/Login required, Action, Reference,
  Data carried forward.
  - **Reference** points at an existing Test_Cases row by **Name** when
    one was written for that step, or says "automation-only" with its own
    description when no standalone manual test case exists for that step
    — this is expected and fine; not every automation step needs a
    corresponding manual case.
  - **Data carried forward** names the exact value (e.g. "Voucher Ref No:
    FA-2024-00123") that later steps depend on — the Automation Engineer
    passes this as a variable between steps, never hardcodes it per step.
- **Automation Suitable** call for the flow as a whole, with a reason —
  same Yes/No + reason convention as the per-row columns.

## Rules for building automation from a flow file
- One browser context per role — never reuse a session across roles, even
  if the same physical tester could plausibly do both in real life.
- Steps execute strictly in the order the table specifies.
- Data produced in an earlier step must be captured into a variable and
  passed forward — never re-derived or assumed the same value will exist.
- If a step has no corresponding Test_Cases row (marked "automation-only"),
  the Automation Engineer still documents what that step does in the
  test's inline comments — the flow file's description is the source of
  truth for it, since no manual test case documents it elsewhere.
- A long flow may be broken into named helper functions per role/stage
  for readability, called in sequence by one overall test function — the
  journey stays a single logical test, not several disconnected ones.

## What this does NOT replace
Individual, single-step automation (one Test_Cases row marked Automation
Suitable = Yes) still works exactly as before — flow files are only for
journeys that genuinely chain multiple roles/pages/data together.
