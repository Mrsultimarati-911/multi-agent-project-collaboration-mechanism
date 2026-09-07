# Dispatch and audit

## Approval gate

The assistant may propose a plan or task package. An explicit owner confirmation, or a matching owner-approved Level 1 Authority Envelope, authorizes dispatch. Discussion, an agent recommendation, or an unreviewed draft is not authorization. On the first dispatch in a level-1 task, it first submits the approved `level1_plan` contract to record; no `level2_plan` or employee conversation may precede that record.

Before an action decision, the assistant applies [four-quadrant alignment](four-quadrant-alignment.md). Its task package or plan captures material assumptions, risks, alternatives and validation experiments; sufficient existing information or envelope authority does not trigger another owner question.

## Task code

Use `<project-identifier>_<level1-task>-<assistant>-<employee>-<employee-task>`:

```text
QSV5_02-04-014-0008
```

The project identifier is set by the owner during monitor initialization, such as `QSV5` or `TLTK`. The four numeric segments are level-1 task (2 digits), assistant (2 digits), employee (3 digits), and employee task (4 digits), starting at zero. Level 1 plans/results use `<project>_<stage>-##-###-####`; Level 1 assistant-scope records use `<project>_<stage>-<assistant>-###-####`; Level 2 uses concrete digits. An owner changes the identifier only through monitor, which records original/current identifiers and aliases and notifies all assistants. Historical task codes, filenames and internal references remain unchanged forever.

Human shorthand such as `a00` and `e00` may help the owner refer to roles during discussion, but never appears in a task code, package, record, filename, or agent-to-agent message.

## Required employee task package

First record a `level2_plan` authorized by explicit owner approval or a matching owner-approved Authority Envelope. Then use `assets/templates/root/templates/TASK_PACKAGE.md` (or `_CN`) as the detailed operational instruction and cite both plan records. A complete package contains:

1. task code and task name;
2. objective, reason for dispatch, `dispatch_authority` and its verifiable approval/envelope reference;
3. required reads and supplied input artifacts;
4. allowed read scope and write scope;
5. explicit non-goals and prohibited actions;
6. confirmed decisions and assumptions that cannot be changed;
7. acceptance criteria and verification commands;
8. required delivery path and output/report format;
9. escalation conditions and expected-duration handling.
10. the requirement to submit evidence and request assistant audit on completion.

An employee asks for clarification or escalates if the task conflicts with rules, has missing inputs, needs a new authority, or cannot meet the declared boundary.

## Audit and promotion

The assistant verifies artifacts, validation outputs, scopes and limitations. It accepts as scoped, requests bounded correction, reports an exception, or performs publication/integration already permitted by the Authority Envelope. Routine retry, bug fix, test failure rework, task-local refactoring and employee replacement within the approved limits do not require renewed owner approval. Changes to Level 1 goals/material deliverables, envelope breaches and R3 actions do. See the complete owner-reserved list in [V2 governance](v2-governance.md).

After dispatch, the assistant remains silent until an employee submits a completion/audit request, an escalation-grade blocker occurs, or the owner intervenes. For long work, the default is: estimate work expected to exceed ten minutes, check status at most once per ten minutes, and have each assistant actively manage no more than five employees. The owner may amend these defaults through monitor.

Employee delivery never by itself authorizes integration, changes a project rule, or establishes a confirmed project fact.

For shared publication, submitted delivery names one complete file/directory as `employee_delivery_reference` and the engine captures its SHA-256 snapshot. Audit must match the most recent submitted attempt/path; acceptance also matches unchanged hash. Publish that exact delivery scope, with stage publish permission or the plan's actual `owner_publication_approval_evidence`; owner-approved dispatch alone is insufficient. Subpath extraction or edits require resubmission and a new scoped audit. Offline validation compares payload/manifest to the recorded audit without depending on the old workspace.
