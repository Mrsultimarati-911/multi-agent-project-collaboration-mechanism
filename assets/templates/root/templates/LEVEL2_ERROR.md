# Level-2 owner-intervention blockage

This JSON is an event submitted to `root/record_engine.py`. Replace DEMO identities/references and establish real prerequisite records/evidence first; do not write it directly to `work_logs/`. The engine generates IDs, timestamps, sequence, hashes, `record_status`, `execution_status`, and plan freeze metadata. Fold the narrative outline below into `event_description`.

```json
{
  "record_type": "level2_error",
  "task_code": "DEMO_00-00-000-0000",
  "requested_status": "paused",
  "level2_plan_reference": "work_logs/level2_plan_DEMO_00-00-000-0000.md",
  "direct_error_evidence": "ai_workspace/DEMO_00-00-000-0000/blocker.txt",
  "owner_intervention_required": true,
  "paused_scope": [
    "DEMO_00-00-000-0000"
  ],
  "task_name": "Example task (replace with the real objective)",
  "responsible_role": "assistant_00",
  "event_description": "Supply the full factual narrative, verification evidence, limitations and next action; sample text is not approval evidence."
}
```

## Blockage and evidence

## Why authorized recovery is unavailable

## Exact owner decision, access, or input required

## Pause impact and safe resumption procedure

## Linked records and next state

This error pauses only this employee task. It remains after recovery and is never downgraded or deleted.
