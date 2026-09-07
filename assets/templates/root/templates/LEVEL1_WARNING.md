# Level-1 recoverable interruption

This JSON is an event submitted to `root/record_engine.py`. Replace DEMO identities/references and establish real prerequisite records/evidence first; do not write it directly to `work_logs/`. The engine generates IDs, timestamps, sequence, hashes, `record_status`, `execution_status`, and plan freeze metadata. Fold the narrative outline below into `event_description`.

```json
{
  "record_type": "level1_warning",
  "task_code": "DEMO_00-00-###-####",
  "requested_status": "active",
  "level1_plan_reference": "work_logs/level1_plan_DEMO_00-##-###-####.md",
  "recovery_owner": "assistant_00",
  "recovery_plan": "Apply the approved stage recovery procedure.",
  "affected_scope": [
    "DEMO_00-00-000-0000"
  ],
  "task_name": "Example task (replace with the real objective)",
  "responsible_role": "assistant_00",
  "event_description": "Supply the full factual narrative, verification evidence, limitations and next action; sample text is not approval evidence."
}
```

## Stage-wide interruption and evidence

## Cause assessment and affected employees/processes

## Recovery plan and verification

## Linked records and next state

This warning is preserved if it later escalates to `level1_error`.
