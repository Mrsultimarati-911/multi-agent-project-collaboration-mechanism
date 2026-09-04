# Level-1 plan record

`level1_plan` is the authoritative, owner-approved action contract for one stage. It is neither a conversation summary nor a mutable task board.

## Creation gate

An assistant submits it to `record` only after all of these conditions are met:

1. the owner explicitly approves the stage plan;
2. material four-quadrant questions are answered or converted to an owner-accepted exploration assumption;
3. scope, non-goals, acceptance criteria, planned delegation, audit path, and escalation conditions are known;
4. no employee for this stage has been created or dispatched.

Use aggregate task code `<project>_<level1>-##-###-####`, for example `QSV5_00-##-###-####`.

## Required content

Use `LEVEL1_PLAN.md`. The contract records: authorization evidence; confirmed objective, deliverables, completion definition, and non-goals; known context and allowed/prohibited scope; four-quadrant alignment conclusion; implementation and validation path; a planned employee/task map; audit, integration, and owner acceptance criteria; risks and escalation triggers; and the frozen baseline.

## Frozen baseline and amendments

The initial baseline is immutable. A material change to goals, scope, planned employee map, acceptance criteria, or escalation policy requires owner approval. The assistant submits that evidence to record, which appends a row to the plan's amendment ledger. The row identifies the reason, impact, decision, and linked replacement records. It does not rewrite or delete the initial plan content.

Routine execution progress, minor wording corrections, and employee implementation details do not belong here; use the appropriate level-2 or result record instead.
