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

Use `LEVEL1_PLAN.md` or `_CN`. The contract records owner approval evidence; objective, material deliverables, completion definition and non-goals; scope; four-quadrant alignment; implementation/validation; participating assistants and Stage DAG; audit/integration/acceptance; risks; and an owner-approved Authority Envelope defining task types, concurrency, read/write scope, publication and integration permissions. Level 2 plans within this envelope do not require another owner approval.

## Frozen baseline and replacement

The initial baseline is immutable. A change to stage goals, material deliverables, acceptance criteria or envelope limits requires an owner-approved new plan with a new stage identity and `supersedes_reference` to the previous plan. Appended discussion records reasons/evidence only; it never changes old authority, dependencies or scopes. Supersession is provenance, not automatic cancellation: end old task/stage states through legal transitions. Bounded staffing changes, employee replacement and corrections covered by the envelope remain autonomous at Level 2. Never rewrite or delete the initial plan.

Routine execution progress, minor wording corrections, and employee implementation details do not belong here; use the appropriate level-2 or result record instead.
