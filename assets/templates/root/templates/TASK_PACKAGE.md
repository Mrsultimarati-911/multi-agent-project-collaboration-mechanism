# Employee task package

- task_code: `<project-identifier>_<level1-task>-<assistant>-<employee>-<employee-task>`
- task_name:
- dispatch_status: owner-approved
- level1_plan_reference:
- level2_plan_reference:
- responsible_employee:
- employee_model: `owner-specified, or gpt-5.6-luna`
- employee_reasoning: `owner-specified, or high`
- expected_duration:

## Objective

## Required reads and input artifacts

## Allowed scope

- allowed_reads:
- allowed_writes: `ai_workspace/<task-name>/`

## Non-goals and prohibitions

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
