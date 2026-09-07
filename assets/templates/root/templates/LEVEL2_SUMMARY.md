# Level 2 employee summary

This JSON is an event submitted to `root/record_engine.py`. Replace DEMO identities/references and establish real prerequisite records/evidence first; do not write it directly to `work_logs/`. The engine generates IDs, timestamps, sequence, hashes, `record_status`, `execution_status`, and plan freeze metadata. Fold the narrative outline below into `event_description`.

The engine pins audit references to `.md#event_id`. Final results follow the actual accepted audit, which must match the latest submitted attempt, delivery path and content hash. Summaries reference that result's same audit; neither can bypass state or accept an unsubmitted file.

```json
{
  "record_type": "level2_summary",
  "task_code": "DEMO_00-00-000-0000",
  "requested_status": "accepted",
  "responsible_role": "employee_00",
  "assistant_audit_reference": "work_logs/level2_results_mid_DEMO_00-00-000-0000.md",
  "level2_results_reference": "work_logs/level2_results_DEMO_00-00-000-0000.md",
  "task_name": "Example task (replace with the real objective)",
  "event_description": "Supply the full factual narrative, verification evidence, limitations and next action; sample text is not approval evidence."
}
```

## Completed scope

## Final implementation approach and workflow

## Evidence, verification, and audit outcome

## Exceptions, limitations, and follow-up

Submit this document only to `record` after the creating assistant has accepted the scoped delivery. `record` writes the authoritative copy to `work_logs/`; this workspace copy is a submission artifact, not an authoritative log.
