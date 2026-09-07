# Level-1 owner-decision blockage

This JSON is an event submitted to `root/record_engine.py`. Replace DEMO identities/references and establish real prerequisite records/evidence first; do not write it directly to `work_logs/`. The engine generates IDs, timestamps, sequence, hashes, `record_status`, `execution_status`, and plan freeze metadata. Fold the narrative outline below into `event_description`.

```json
{
  "record_type": "level1_error",
  "task_code": "DEMO_00-00-###-####",
  "requested_status": "paused",
  "level1_plan_reference": "work_logs/level1_plan_DEMO_00-##-###-####.md",
  "direct_error_evidence": "rules/stage-blocker.md",
  "owner_intervention_required": true,
  "all_paused_employees": [
    "employee_00"
  ],
  "task_name": "Example task (replace with the real objective)",
  "responsible_role": "assistant_00",
  "event_description": "Supply the full factual narrative, verification evidence, limitations and next action; sample text is not approval evidence."
}
```

## Stage blockage and evidence

## Why authorized recovery is unavailable

## Exact owner decision required

## Full pause scope and resumption procedure

## Linked records and next state

This error pauses every employee under the level-1 task until the owner decision is supplied.
