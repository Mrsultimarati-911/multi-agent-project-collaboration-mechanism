# Level-1 aggregate final result

This JSON is an event submitted to `root/record_engine.py`. Replace DEMO identities/references and establish real prerequisite records/evidence first; do not write it directly to `work_logs/`. The engine generates IDs, timestamps, sequence, hashes, `record_status`, `execution_status`, and plan freeze metadata. Fold the narrative outline below into `event_description`.

```json
{
  "record_type": "level1_results",
  "task_code": "DEMO_00-##-###-####",
  "requested_status": "accepted",
  "level1_plan_reference": "work_logs/level1_plan_DEMO_00-##-###-####.md",
  "source_level1_summaries": [
    "work_logs/level1_summary_DEMO_00-00-###-####.md"
  ],
  "source_level2_results": [
    "work_logs/level2_results_DEMO_00-00-000-0000.md"
  ],
  "owner_acceptance_reference": "rules/owner-acceptance.md",
  "reusable_outputs": [],
  "task_name": "Example task (replace with the real objective)",
  "responsible_role": "assistant_00",
  "event_description": "Supply the full factual narrative, verification evidence, limitations and next action; sample text is not approval evidence."
}
```

## Owner-accepted objective outcome

## Consolidated deliverables and validation evidence

## Reusable outputs, decisions, and handoff inputs

## Exceptions, limitations, and next-stage constraints

Record condenses only supplied summaries, final results, audit evidence, and owner acceptance; it does not infer success or add technical conclusions.
