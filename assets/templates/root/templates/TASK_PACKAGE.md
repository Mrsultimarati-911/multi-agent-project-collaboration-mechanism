# Employee task package

- task_code: `<project-identifier>_<level1-task>-<assistant>-<employee>-<employee-task>`
- task_name:
- dispatch_authority: `owner-approved | envelope-authorized`
- owner_dispatch_approval_evidence: only for owner-approved
- authority_envelope_reference: matching owner-approved Level 1 for envelope-authorized
- level1_plan_reference:
- level2_plan_reference:
- responsible_employee:
- employee_model: `owner-specified, or gpt-5.6-luna`
- employee_reasoning: `owner-specified, or high`
- expected_duration:
- depends_on: []
- required_dependency_status: {} (only accepted / integrated / closed; default accepted)
- consumes: []
- produces: []
- interface_references: []
- task_type:
- risk_level: R0 / R1 / R2 / R3
- base_revision:
- worktree_or_branch:
- conflict_scope:

## Objective

## Required reads and input artifacts

## Allowed scope

- allowed_reads:
- allowed_writes: `ai_workspace/<task-name>/`

## Non-goals and prohibitions

Preserve the Level 1 objective/material deliverable, task types, concurrency and read/write scope. Shared inputs name artifact_id plus exact version, never latest. Bounded retry/correction, test rework and task-local refactoring use existing authority; envelope breaches and all R3 actions require explicit owner approval.

Publication uses the parent's matching publish permission or explicit `owner_publication_approval_evidence` in the Level 2 plan, independently of dispatch approval. Submit the complete delivery before audit; the engine binds acceptance to that submitted attempt, path and hash. Integration requires a declared `integration_target` and its specific authority while preserving assistant/coordinator path ownership.

## Confirmed decisions and fixed assumptions

## Four-quadrant alignment summary

- shared confirmed context and boundaries:
- material owner-context gaps / questions asked (maximum 10):
- agent-supplied risks, alternatives, or corrections:
- unknowns converted to testable assumptions or minimal experiments:

## Acceptance criteria and verification

## Delivery location and required report

On completion, submit the delivery evidence to the creating assistant and explicitly request assistant audit. Completion is not acceptance or authorization to promote files.

After the assistant accepts the scoped delivery, create `level2_summary_<task-code>.md` in this task workspace from `root/templates/LEVEL2_SUMMARY.md` and submit only that summary directly to `record`. Do not submit any other work-log record type directly to record.

## Escalation conditions

- authority-envelope boundary:
- owner_intervention_required trigger:
- notification route: governance / record event only; employee never contacts Feishu directly
