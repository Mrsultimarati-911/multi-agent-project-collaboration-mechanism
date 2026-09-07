# Level-2 recoverable interruption

This JSON is an event submitted to `root/record_engine.py`. Replace DEMO identities/references and establish real prerequisite records/evidence first; do not write it directly to `work_logs/`. The engine generates IDs, timestamps, sequence, hashes, `record_status`, `execution_status`, and plan freeze metadata. Fold the narrative outline below into `event_description`.

```json
{
  "record_type": "level2_warning",
  "task_code": "DEMO_00-00-000-0000",
  "requested_status": "paused",
  "level2_plan_reference": "work_logs/level2_plan_DEMO_00-00-000-0000.md",
  "recovery_owner": "assistant_00",
  "recovery_plan": "Correct the command inside the approved envelope.",
  "resumption_condition": "The corrected command passes the task-local check.",
  "task_name": "Example task (replace with the real objective)",
  "responsible_role": "assistant_00",
  "event_description": "Supply the full factual narrative, verification evidence, limitations and next action; sample text is not approval evidence."
}
```

## Interruption and evidence

## Cause assessment

## Recovery plan, checks, and expected impact

## Linked records and next state

This warning remains after recovery. If the recovery path proves unavailable, create a linked `level2_error`; never replace this record.
