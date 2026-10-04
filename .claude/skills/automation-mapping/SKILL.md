---
name: automation-mapping
description: Use when producing or consuming the temporary automation-mapping JSON between UI exploration and automation coding — defines the JSON format for single scenarios and multi-role e2e flows, and the VERIFIED/LOCATOR_REQUIRES_REVIEW/READY_FOR_AUTOMATION status values.
---

# Skill: Automation Mapping (temporary artifact, not a source of truth)

## What this artifact is for
During UI Exploration, locators are captured into a JSON file purely so a
human can review and verify them before any code is written. It is a
checkpoint, not a database the running test suite depends on.

## Why it must not become the permanent locator store
POM exists to centralize locators in one place — the page class. If
the running test suite also read locators from JSON, every UI change would
require updating two places, and they would drift out of sync. So:
- The JSON is written once, during exploration, for review.
- The Automation Engineer reads it once, to write the POM class(es).
- After that, the `.py` page class is the only place tests read locators from.
- The JSON for a completed flow may be archived
  (`automation/automation_mapping/_archive/`) or deleted.

## The permanent record is the element catalog
Whenever `ui-explorer` visits a page it ALSO writes (or updates)
`automation/element_catalog/<page-name>.md` using
`templates/element_catalog_template.md`, with screenshots in
`element_catalog/evidence/`. The catalog is documentation for humans and is
never deleted. Tests never read it. When a locator changes, update the
catalog and the page class together.

## Format — single scenario
`automation/automation_mapping/<scenario-name>.json`:
```json
{
  "scenario_name": "Add voucher with valid reference number",
  "page": "VoucherEntryPage",
  "steps": [
    {
      "step_no": 1,
      "business_action": "Enter Reference Number",
      "action": "fill",
      "target": "Reference Number field",
      "test_data": "FA-2024-00123",
      "locator_strategy": "get_by_label",
      "locator": "Reference Number",
      "status": "VERIFIED"
    }
  ],
  "overall_status": "READY_FOR_AUTOMATION"
}
```

## Format — end-to-end flow (multiple roles/pages)
`automation/automation_mapping/<flow-name>.json`:
```json
{
  "flow_name": "Voucher Entry -> Approval -> Acknowledgment",
  "roles": ["HOFIN User", "HOFA Approver"],
  "steps": [
    {
      "step_no": 1,
      "role": "HOFIN User",
      "page": "VoucherEntryPage",
      "business_action": "Create voucher with reference number",
      "locator_strategy": "get_by_label",
      "locator": "Reference Number",
      "produces_data": "voucher_ref_no",
      "status": "VERIFIED"
    },
    {
      "step_no": 2,
      "role": "HOFA Approver",
      "page": "VoucherApprovalPage",
      "business_action": "Find and approve the voucher",
      "locator_strategy": "get_by_role",
      "locator": "button:Approve",
      "consumes_data": "voucher_ref_no",
      "status": "VERIFIED"
    }
  ],
  "overall_status": "READY_FOR_AUTOMATION"
}
```
`produces_data` / `consumes_data` name the variable the Automation
Engineer threads between steps — see the `e2e-automation-flows` skill.

No `test_case_id` or Zephyr Key field in either shape — `scenario_name`/
`flow_name` (matching the Excel Name column or the flow file) is the only
reference, used only for the filename/human traceability.

## Status values
`VERIFIED`, `LOCATOR_REQUIRES_REVIEW`, `DATA_REQUIRES_REVIEW`, `BLOCKED`,
`READY_FOR_AUTOMATION`. Automation Engineer only builds from steps marked
`VERIFIED`.
