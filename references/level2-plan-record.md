# Level-2 plan record

`level2_plan` is the authoritative, owner-approved execution authorization for exactly one employee task. The detailed `TASK_PACKAGE.md` is an operational derivative of this record, not a substitute for it.

## Creation gate

An assistant submits this record to `record` only after: the parent `level1_plan` exists; the owner explicitly approves dispatch; the employee identity and concrete task code are allocated; the required inputs, isolated workspace, allowed scopes, expected deliverable, audit evidence, and escalation conditions are known. Record writes it before the employee conversation is created or instructed.

## Frozen plan and task identity

The baseline is frozen after record writes it. A material permission, scope, acceptance, or execution-path change requires owner approval and is appended by record to the amendment ledger. A different objective or deliverable is a new employee task and must receive a new employee-task serial, task code, and `level2_plan`.

## Delivery route

The employee delivers evidence to its creating assistant and requests audit. The assistant alone submits plan, mid-result, result, warning, and error records to record. After accepted audit, the employee may submit only its own `level2_summary` to record.
