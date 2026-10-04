---
name: locator-strategy
description: Use whenever choosing or verifying a Playwright locator during UI exploration or automation coding — defines the priority order (get_by_role > get_by_label > get_by_placeholder > get_by_text > data-testid > CSS > XPath) and when to write LOCATOR_REQUIRES_REVIEW instead of guessing.
---

# Skill: Locator Strategy

## Priority order (use the first one that resolves uniquely)
1. `get_by_role("button", name="Login")`
2. `get_by_label("User ID")`
3. `get_by_placeholder("Enter your ID")`
4. `get_by_text("Save Changes")`
5. `[data-testid="..."]`
6. CSS selector — only when nothing semantic is available
7. XPath — last resort only, for structural relationships CSS can't
   express

## When nothing reliable resolves
Write `LOCATOR_REQUIRES_REVIEW` instead of guessing a brittle selector.
Attach whatever evidence was found so a human can resolve it quickly.

## Never
- Guess an element ID or class name without confirming it in the actual
  rendered DOM.
- Reuse a locator captured on one environment without re-verifying on the
  target environment.
- Write an XPath that depends on absolute position — it breaks on any
  layout change.
