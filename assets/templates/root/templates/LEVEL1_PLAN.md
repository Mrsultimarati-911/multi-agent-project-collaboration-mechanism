# Level-1 action plan

This JSON is an event submitted to `root/record_engine.py`. Replace DEMO identities/references and establish real prerequisite records/evidence first; do not write it directly to `work_logs/`. The engine generates IDs, timestamps, sequence, hashes, `record_status`, `execution_status`, and plan freeze metadata. Fold the narrative outline below into `event_description`.

The sample envelope shows structure only; its actual values require explicit owner approval. owner_approval_evidence must reference real approval evidence. Preserve amendments as appended events, never overwrite the baseline.

```json
{
  "record_type": "level1_plan",
  "task_code": "DEMO_00-##-###-####",
  "requested_status": "planned",
  "accountable_assistant": "assistant_00",
  "coordinating_assistant": "assistant_00",
  "participating_assistants": [
    "assistant_00"
  ],
  "workstreams": {
    "MAIN": {
      "owner": "assistant_00",
      "depends_on": []
    }
  },
  "authority_envelope": {
    "auto_dispatch": true,
    "max_module_assistants": 0,
    "max_parallel_employees_per_assistant": 5,
    "allowed_task_types": [
      "data_processing",
      "testing"
    ],
    "allowed_reads": [
      "raw_data",
      "common_data",
      "common_artifacts",
      "ai_workspace"
    ],
    "allowed_writes": [
      "ai_workspace"
    ],
    "publish_permissions": {
      "common_data": true,
      "common_artifacts": true
    },
    "integration_permissions": {
      "assistant_workspace": true,
      "project_demo": false,
      "project_final": false
    },
    "prohibited_without_owner": [
      "change_project_goal",
      "material_scope_expansion",
      "change_core_research_hypothesis",
      "material_methodology_change",
      "new_final_deliverable",
      "overwrite_raw_data",
      "destructive_delete",
      "external_publish",
      "paid_external_action",
      "production_action",
      "project_final_write_or_acceptance",
      "authority_envelope_breach",
      "unresolved_cross_assistant_conflict",
      "unresolved_final_integration_blocker"
    ]
  },
  "owner_approval_evidence": "rules/owner-approval.md",
  "task_name": "Example task (replace with the real objective)",
  "responsible_role": "assistant_00",
  "event_description": "Supply the full factual narrative, verification evidence, limitations and next action; sample text is not approval evidence."
}
```

## 1. Owner-confirmed objective

- problem to solve:
- final deliverables:
- definition of done:
- acceptance criteria:
- explicit non-goals:

## 2. Confirmed context, boundaries, and inputs

- confirmed background:
- required references and inputs:
- allowed project scope:
- prohibited scope:
- dependencies and prerequisites:

## 3. Four-quadrant alignment conclusion

- shared confirmed context:
- material owner-context questions and answers:
- explicit non-material assumptions / exploration approach:
- assistant-supplied risks, corrections, alternatives, and trade-offs:
- shared unknowns, testable assumptions, and minimum experiments:

## 4. Implementation and validation path

- planned approach:
- integration boundaries:
- verification commands or experiments:
- recovery or fallback strategy:

## 5. Planned delegation map

| Employee | Planned task code | Objective | Expected deliverable | Workspace | Dependencies | Auditor |
|---|---|---|---|---|---|---|
| | | | | | | |

## 5.1 Module interfaces and integration

- interface contract references: `plan/interfaces/`
- module ownership / Stage DAG:
- integration authority: coordinating assistant only

## 6. Audit, integration, and owner acceptance

- employee delivery evidence required:
- assistant audit method:
- project_demo admission criteria:
- owner final acceptance criteria:
- conclusions that must not be extrapolated:

## 7. Risks and escalation conditions

- known risks:
- recoverable warning conditions:
- owner-intervention conditions:
- level1_error / full-pause conditions:

## 8. Frozen baseline

The recorded baseline is immutable. Material goal/envelope changes require an owner-approved new stage plan with `supersedes_reference`; the following outline records reasons and links only and cannot modify prior executable authority.

## Replacement evidence outline (submit as narrative, never edit the frozen plan)

| Date | Reason | Owner approval evidence | Impact | Decision / replacement records | Recorded by |
|---|---|---|---|---|---|
| | | | | | record |
