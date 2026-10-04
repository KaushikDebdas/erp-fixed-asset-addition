# Flow: <Short Flow Name>

**Business scenario:** <one or two sentences describing the journey end
to end — what business outcome it achieves and why it spans multiple
roles/pages.>

| Step | Role/Login | Action | Reference | Data carried forward |
|---|---|---|---|---|
| 1 | <e.g. HOFIN User> | <what they do> | <Test_Cases Name, or "automation-only: <description>"> | <data value produced, if any> |
| 2 | <e.g. HOFA Approver> | <what they do> | <reference> | <data value consumed/produced> |
| 3 | ... | ... | ... | ... |

**Automation Suitable:** <Yes/No> — <one-line reason>

---
## Notes for the Automation Engineer
- One browser context per distinct role listed above — never reuse a
  session across roles.
- The data column above is the exact variable name/value to thread
  between steps — don't hardcode it separately in each step or assume
  it'll still be there without passing it explicitly.
- Steps execute in the order listed — don't reorder for convenience.
- Any step marked "automation-only" has no standalone manual test case;
  its description in this table is the only spec for it — document that
  in the test's inline comments too.
