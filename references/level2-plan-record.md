# Level-2 plan record

`level2_plan` is the authoritative execution authorization for exactly one employee task. Its `dispatch_authority` is either `owner-approved` or `envelope-authorized`. The detailed `TASK_PACKAGE.md` is an operational derivative, not a substitute.

## Creation gate

An assistant submits the record after the owner-approved parent `level1_plan` exists and one of two gates is satisfied: explicit owner dispatch approval with evidence, or a matching owner-approved Authority Envelope with its reference and all limits verified. Employee identity, concrete code, inputs, workspace, scopes, deliverable, audit evidence and escalation conditions must be known. Record invokes the engine before the employee conversation is created or instructed. Owner dispatch fields are conditional on `owner-approved`; envelope references are required for `envelope-authorized`.

## Frozen plan and task identity

The baseline is frozen after the engine writes it. Bounded retry, correction, re-run, bug fixes, test rework, local refactoring and employee replacement use the approved envelope, with evidence appended rather than a fresh owner gate. A change beyond its permission/scope limits or to Level 1 objectives, material deliverables or acceptance requires explicit owner approval. A different employee-task objective or deliverable receives a new serial, task code and plan; if still inside the Level 1 envelope, that new plan may be envelope-authorized. Historical baselines remain unchanged.

Changing frozen task scopes, dependencies or authority requires a newly authorized plan with a new task identity and `supersedes_reference`. Narrative amendments do not update executable fields. Supersession does not end old task state automatically; use an allowed cancellation/completion transition separately. This release has no generic in-place plan amendment mechanism.

## Delivery route

The employee delivers evidence to its creating assistant and requests audit. The assistant alone submits plan, mid-result, result, warning, and error records to record. After accepted audit, the employee may submit only its own `level2_summary` to record.
