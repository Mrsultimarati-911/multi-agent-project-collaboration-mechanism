# Level-2 execution plan

This JSON is an event submitted to `root/record_engine.py`. Replace DEMO identities/references and establish real prerequisite records/evidence first; do not write it directly to `work_logs/`. The engine generates IDs, timestamps, sequence, hashes, `record_status`, `execution_status`, and plan freeze metadata. Fold the narrative outline below into `event_description`.

The example uses `envelope-authorized`. For direct approval use `owner-approved` and an actual `owner_dispatch_approval_evidence` file reference. Bounded rework/replacement needs no repeated approval; envelope breaches and R3 require explicit owner approval.

The engine pins plan/audit references to `.md#event_id`. `required_dependency_status` permits only `accepted`, `integrated` or `closed` (default accepted), never planned/running. Shared publication additionally requires the parent's matching `publish_permissions` or an actual `owner_publication_approval_evidence` in this plan; owner-approved dispatch alone is insufficient.

```json
{
  "record_type": "level2_plan",
  "task_code": "DEMO_00-00-000-0000",
  "requested_status": "planned",
  "responsible_assistant": "assistant_00",
  "responsible_employee": "employee_00",
  "level1_plan_reference": "work_logs/level1_plan_DEMO_00-##-###-####.md",
  "dispatch_authority": "envelope-authorized",
  "authority_envelope_reference": "work_logs/level1_plan_DEMO_00-##-###-####.md",
  "task_type": "data_processing",
  "risk_level": "R1",
  "workspace": "ai_workspace/DEMO_00-00-000-0000",
  "allowed_reads": [
    "raw_data"
  ],
  "allowed_writes": [
    "ai_workspace/DEMO_00-00-000-0000"
  ],
  "depends_on": [],
  "required_dependency_status": {},
  "consumes": [],
  "produces": [],
  "interface_references": [],
  "task_name": "Example task (replace with the real objective)",
  "responsible_role": "assistant_00",
  "event_description": "Supply the full factual narrative, verification evidence, limitations and next action; sample text is not approval evidence."
}
```

## 1. Authorized task

- parent level-1 objective:
- task objective:
- expected deliverable:
- definition of done:
- explicit non-goals:

## 2. Inputs and permitted scope

- required reads:
- supplied input artifacts:
- allowed_reads:
- allowed_writes:
- prohibited writes / actions:
- confirmed decisions and fixed assumptions:

## 3. Execution path

- recommended approach:
- key steps:
- dependencies:
- dependency DAG / blocking condition:
- write lease (when Git worktree is unavailable):
- permitted exploration boundary:
- intermediate artifacts to retain:

## 4. Verification and audit

- required evidence:
- verification commands or experiments:
- assistant audit criteria:
- correction / rework criteria:
- project_demo admission conditions:
- owner_publication_approval_evidence (optional, required only when publishing without matching stage publish permission):
- integration_target and envelope permission / owner_integration_approval_evidence (when integration is planned):
- conclusions that must not be extrapolated:

## 5. Delivery and record route

1. Employee submits delivery evidence to the creating assistant and explicitly requests audit.
2. Assistant submits `level2_results_mid`, warning, error, and accepted final result records to record as applicable.
3. After accepted audit, employee submits only `level2_summary` to record.

## 6. Escalation and pause conditions

- employee autonomous troubleshooting boundary:
- assistant escalation conditions:
- recoverable warning conditions:
- owner-intervention / level2_error conditions:
- owner_intervention_required: false
- long-task estimate and check cadence:

## 7. Frozen baseline

This baseline is immutable. Append bounded corrections using existing envelope authority; explicit owner approval is required only beyond that authority or for R3/material Level 1 changes. A different task objective/deliverable gets a new code and plan, which may still be envelope-authorized. Record submits changes through the engine rather than editing an earlier JSON block.

Frozen scope/dependency/authority changes also need a new task identity and `supersedes_reference`. The reference links history only; old task cancellation is a separate legal state transition.

## Replacement evidence outline (submit as narrative, never edit the frozen plan)

| Date | Reason | Approval or Envelope reference | Impact | Decision / replacement records | Recorded by |
|---|---|---|---|---|---|
| | | | | | record |
