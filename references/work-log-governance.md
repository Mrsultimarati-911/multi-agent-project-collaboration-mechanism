# Work-log governance

Only the `record` role writes `work_logs/`. A record is concise evidence for a durable event, not a transcript.

## Event threshold

Record only an owner-confirmed plan or dispatch, substantive audited delivery, correction/recovery trajectory, warning, error, stage completion, or audit outcome. Do not record routine coordination, raw conversation, unconfirmed ideas, or an employee's unverified self-report as a final result.

## Levels and filenames

Level 1 represents an owner-approved project stage or assistant-level initiative:

- `level1_plan_<aggregate-code>.md`
- `level1_summary_<aggregate-code>.md`
- `level1_warning_<aggregate-code>.md`
- `level1_error_<aggregate-code>.md`
- `level1_results_<aggregate-code>.md`

Level 2 represents one employee task:

- `level2_plan_<task-code>.md`
- `level2_results_mid_<task-code>.md`
- `level2_results_<task-code>.md`
- `level2_summary_<task-code>.md`
- `level2_warning_<task-code>.md`
- `level2_error_<task-code>.md`

Use concrete task codes for level 2. `level2_results_mid` is append-only audit history. Do not overwrite prior audit entries. Create `level2_results` only after a supplied assistant audit says the scoped delivery is accepted.

Only the responsible employee may directly submit a `level2_summary` to record. It must reference the accepted assistant audit and its `level2_results`; record rejects or holds a premature summary. All other log submissions, including plans, mid-results, results, warnings, and errors, go to record only through the assistant.

## Required content

Every log contains: record type, code, task/stage name, responsible role, event date, status, source/parent references, a concise factual event description, evidence paths or commands, limitations, and next state. Result records also state whether the evidence is final, scoped, unresolved, rejected, or requires owner action.

Warnings remain visible if they become errors. A correction is a new append or related record, never silent replacement of the earlier event.

## Owner-authorized identifier change

Task-code history is normally append-only. An owner-approved project-identifier change, recorded by monitor, is the sole exception: record updates the identifier in every effective log filename, `task_code` field, and internal record reference. It must not change any other historical fact. Monitor sends the same mapping to every assistant before new tasks or audit records use the new identifier.

## Validation boundary

The validator can confirm names, fields, and references. It cannot prove an artifact's correctness or validate a claim that an agent has not independently audited.
