# Level-2 execution plan

- record_type: level2_plan
- task_code: `<project-identifier>_<level1-task>-<assistant>-<employee>-<employee-task>`
- task_name:
- responsible_role: assistant
- responsible_assistant:
- responsible_employee:
- event_date:
- status: approved-dispatched
- plan_status: frozen
- level1_plan_reference:
- owner_dispatch_approval_date:
- owner_dispatch_approval_evidence:
- employee_model:
- employee_reasoning:
- expected_duration:
- workspace: `ai_workspace/<task-name>/`
- related_plan:
- supersedes:
- frozen_at:
- frozen_by: human

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
- permitted exploration boundary:
- intermediate artifacts to retain:

## 4. Verification and audit

- required evidence:
- verification commands or experiments:
- assistant audit criteria:
- correction / rework criteria:
- project_demo admission conditions:
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
- long-task estimate and check cadence:

## 7. Frozen baseline

This baseline must not be silently edited. A material owner-approved change for the same task identity is appended below by `record`; a changed objective or deliverable requires a new task code and new level-2 plan.

## Dispatch amendment ledger (record append-only)

| Date | Reason | Owner approval evidence | Impact | Decision / replacement records | Recorded by |
|---|---|---|---|---|---|
| | | | | | record |
