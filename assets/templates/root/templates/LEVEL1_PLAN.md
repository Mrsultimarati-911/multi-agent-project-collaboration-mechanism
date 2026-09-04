# Level-1 action plan

- record_type: level1_plan
- task_code: `<project-identifier>_<level1-task>-##-###-####`
- task_name:
- responsible_role: assistant
- event_date:
- status: approved-active
- project_identifier:
- responsible_owner: human
- accountable_assistant:
- owner_approval_date:
- owner_approval_evidence:
- plan_status: frozen
- related_plan:
- supersedes:
- frozen_at:
- frozen_by: human
- coordinating_assistant: assistant_00
- participating_assistants: []
- authority_envelope_reference:

## V2 Authority Envelope and workstreams

```yaml
authority_envelope:
  auto_dispatch: false
  max_module_assistants: 0
  max_parallel_employees_per_assistant: 5
  allowed_task_types: []
  publish_permissions: { common_data: false, common_artifacts: false }
  integration_permissions: { assistant_workspace: true, project_demo: false, project_final: false }
  prohibited_without_owner: [change_project_goal, overwrite_raw_data, destructive_delete, external_publish, paid_external_action, project_final]
workstreams: {}
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

This baseline is owner-approved and must not be silently edited. `record` alone appends material owner-approved changes below.

## Amendment ledger (record append-only)

| Date | Reason | Owner approval evidence | Impact | Decision / replacement records | Recorded by |
|---|---|---|---|---|---|
| | | | | | record |
