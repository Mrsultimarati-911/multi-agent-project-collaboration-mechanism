# Level-2 auditable delivery ledger

This JSON is an event submitted to `root/record_engine.py`. Replace DEMO identities/references and establish real prerequisite records/evidence first; do not write it directly to `work_logs/`. The engine generates IDs, timestamps, sequence, hashes, `record_status`, `execution_status`, and plan freeze metadata. Fold the narrative outline below into `event_description`.

Submit each dispatched/running/submitted/audited transition separately to this ledger. Before delivery, `employee_delivery_reference` may be null and audit is `not_requested`; submission uses `pending`; an audited event requires `accepted` or `rejected`. Increment attempt_number on rework; never replace older events.

The engine pins record references to `.md#event_id` and computes the delivery hash at submission. Audit must match the latest submitted attempt and exact delivery path; acceptance additionally checks unchanged content against that snapshot. A different file or revised content must be submitted before audit.

A new `integrated` transition requires `integration_target`: the responsible assistant's own `assistant_workspace/<assistant-id>/`, or `project_demo/` for the coordinator only, with matching envelope integration permission. `project_final/` or integration outside the envelope requires actual `owner_integration_approval_evidence`; approval does not relax role/path ownership boundaries. Record the full verified target, not merely a claim of integration.

```json
{
  "record_type": "level2_results_mid",
  "task_code": "DEMO_00-00-000-0000",
  "requested_status": "submitted",
  "level2_plan_reference": "work_logs/level2_plan_DEMO_00-00-000-0000.md",
  "attempt_number": 1,
  "employee_delivery_reference": "ai_workspace/DEMO_00-00-000-0000/delivery.txt",
  "assistant_audit_status": "pending",
  "task_name": "Example task (replace with the real objective)",
  "responsible_role": "assistant_00",
  "event_description": "Supply the full factual narrative, verification evidence, limitations and next action; sample text is not approval evidence."
}
```

## Attempt 1

- attempt_number: 1
- submission_timestamp:
- employee_delivery_reference:
- delivered_scope:
- artifact_paths:
- verification_commands_or_experiments:
- observed_output:
- employee_reported_limitations:
- assistant_audit_status: pending / accepted / rejected (as appropriate)
- assistant_audit_timestamp:
- assistant_audit_reference:
- audit_findings:
- required_correction_or_next_action:

## Later attempts (record append-only)

<!-- Repeat the full Attempt block above. Never replace a prior attempt. -->
