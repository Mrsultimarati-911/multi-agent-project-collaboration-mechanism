# Work-log governance

Only the `record` role writes `work_logs/`. A record is concise evidence for a durable event, not a transcript.

## Work language and templates

Read `work-language` from `rules/00-core-governance.md`, default `zh-CN`. Chinese projects use `_CN` templates and Chinese narrative, evidence explanations, limitations and next-state prose. Stable schema keys remain English. Other configured languages use their matching template, or the base template with translated narrative. Templates contain JSON event payloads for record to complete; only the engine generates Markdown front matter.

## Event threshold

Record owner-approved Level 1 plans, owner-approved or envelope-authorized Level 2 plans, execution transitions, audited deliveries, correction/recovery, warnings/errors and stage outcomes. Do not record raw conversation or treat employee self-reports as accepted results.

## Level-1 plan contract

Create `level1_plan_<project>_<level1>-##-###-####.md` only after explicit owner approval and before the first `level2_plan` or employee dispatch in that level-1 task. It is a frozen action contract, not a discussion transcript. Use [level-1 plan record](level1-plan-record.md) for its required content.

After initial freeze, narrative amendment events may preserve reasons and decisions but never mutate the plan's executable authority. Material changes require an owner-approved new plan/stage identity with `supersedes_reference`, retaining the old baseline and evidence. Supersession does not cancel old state; perform legal state transitions separately.

## Level-2 plan contract

Create `level2_plan_<project>_<level1>-<assistant>-<employee>-<employee-task>.md` before employee creation, with `dispatch_authority` equal to `owner-approved` or `envelope-authorized` and the corresponding evidence/reference. It cites the owner-approved `level1_plan`, uses a concrete code, and fixes employee identity, scopes, objective, deliverable, audit evidence, escalation and delivery route. See [level-2 plan record](level2-plan-record.md).

For the same task identity, record appends execution/correction evidence; bounded corrections remain autonomous. Frozen scopes, dependencies and authority do not change through narrative. A changed task contract gets a new code/plan and `supersedes_reference`, using existing envelope authority when applicable; beyond-envelope or Level 1 material changes require owner approval. No generic in-place plan amendment mechanism is provided.

## Levels and filenames

Level 1 represents an owner-approved project stage or assistant-level initiative:

- `level1_plan_<aggregate-code>.md`
- `level1_summary_<assistant-scope-code>.md`
- `level1_warning_<assistant-scope-code>.md`
- `level1_error_<assistant-scope-code>.md`
- `level1_results_<aggregate-code>.md`

Level 2 represents one employee task:

- `level2_plan_<task-code>.md`
- `level2_results_mid_<task-code>.md`
- `level2_results_<task-code>.md`
- `level2_summary_<task-code>.md`
- `level2_warning_<task-code>.md`
- `level2_error_<task-code>.md`

Use concrete task codes for level 2. `level2_results_mid` is append-only audit history. Do not overwrite prior audit entries. Create `level2_results` only after a supplied assistant audit says the scoped delivery is accepted.

Only the responsible employee may directly submit a `level2_summary` to record. It must reference the accepted assistant audit and its `level2_results`; record rejects or holds a premature summary. All other log submissions, including plans, mid-results, results, warnings, and errors, go to record only through the assistant. V2 adds versioned shared-artifact references, task dependencies, and `owner_intervention_required` notification status to applicable events.

## Required content

Every record follows `root/governance_schema.py`. A caller submits a JSON event with `requested_status`, required type-specific fields, references and narrative. The engine creates `record_status: final` (recorded, not owner-accepted), `execution_status` (the task/stage state), and `plan_status: frozen` on plans. It supplies event identity, sequence, date and hash-chain metadata. There is no generic `status` combining approval, record finality and execution.

Level 1 states are `planned`, `active`, `paused`, `failed`, `accepted`, `closed`, `cancelled`. Level 2 states are `planned`, `dispatched`, `running`, `submitted`, `audited`, `accepted`, `integrated`, `closed`, `paused`, `failed`, `cancelled`. Normal task transitions run planned → dispatched → running → submitted → audited → accepted; rejected audits return to bounded rework before resubmission. The engine restores current state from recorded history. Optional `expected_previous_status` is only an assertion; callers cannot select the authoritative prior state. Dependencies must reach their required consumable state, not merely exist.

Use [remaining work-record types](remaining-work-record-types.md) for the required templates and transitions of `level2_results_mid`, `level2_results`, both warning/error levels, both summary levels, and `level1_results`.

Warnings remain visible if they become errors. A correction is a new append or related record, never silent replacement of the earlier event.

## Owner-authorized identifier change

Historical task identity is immutable, including after an owner-approved rename. Monitor records `original-project-identifier`, the current identifier and owner-confirmed `project-identifier-aliases`; record never renames historical logs or rewrites task codes/references. Existing tasks keep their original code, while new tasks may use the current identifier. The validator accepts the original, current and confirmed alias identifiers. Monitor notifies every assistant before new task allocation.

## Validation boundary

Engine and validator share the canonical schema, typed task-code patterns and history reader. The engine rejects invalid transitions, missing/incorrect plan or audit chains, unsatisfied dependencies and path escapes. A final `level2_results` requires a real matching plan, submission and accepted assistant audit; a field saying "accepted" alone is insufficient. New manifests are `manifest.json`; legacy JSON stored as `manifest.yaml` remains readable. V1 records are read-only legacy sources; missing V2 features are warnings for governance version 1. Schema/provenance checks do not prove technical correctness.
