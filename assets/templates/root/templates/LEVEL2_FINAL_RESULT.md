# Final employee result

This JSON is an event submitted to `root/record_engine.py`. Replace DEMO identities/references and establish real prerequisite records/evidence first; do not write it directly to `work_logs/`. The engine generates IDs, timestamps, sequence, hashes, `record_status`, `execution_status`, and plan freeze metadata. Fold the narrative outline below into `event_description`.

The engine pins audit references to `.md#event_id`. Final results follow the actual accepted audit, which must match the latest submitted attempt, delivery path and content hash. Summaries reference that result's same audit; neither can bypass state or accept an unsubmitted file.

```json
{
  "record_type": "level2_results",
  "task_code": "DEMO_00-00-000-0000",
  "requested_status": "accepted",
  "level2_plan_reference": "work_logs/level2_plan_DEMO_00-00-000-0000.md",
  "level2_results_mid_reference": "work_logs/level2_results_mid_DEMO_00-00-000-0000.md",
  "assistant_audit_reference": "work_logs/level2_results_mid_DEMO_00-00-000-0000.md",
  "assistant_audit_status": "accepted",
  "task_name": "Example task (replace with the real objective)",
  "responsible_role": "assistant_00",
  "event_description": "Supply the full factual narrative, verification evidence, limitations and next action; sample text is not approval evidence."
}
```

## Final completion and deliverables

## Validation and audit evidence

## Accepted scope and non-extrapolation boundary

## Limitations, unresolved items, and next state
