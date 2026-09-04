# Dispatch and audit

## Approval gate

The assistant may propose a plan or task package, but only an explicit owner confirmation authorizes dispatch. Discussion, an agent recommendation, or an unreviewed draft is not authorization. On the first dispatch in a level-1 task, it first submits the approved `level1_plan` contract to record; no `level2_plan` or employee conversation may precede that record.

Before it asks for this approval, the assistant applies [four-quadrant alignment](four-quadrant-alignment.md). Its task package or plan must capture material assumptions, identified risks, alternatives, or proposed validation experiments from that review.

## Task code

Use `<project-identifier>_<level1-task>-<assistant>-<employee>-<employee-task>`:

```text
QSV5_02-04-014-0008
```

The project identifier is set by the owner during monitor initialization, is global to that project, and may be a concise identifier such as `QSV5` or `TLTK`. The four numeric segments are, in order: level-1 task (2 digits), assistant (2 digits), employee (3 digits), and employee task (4 digits); their sequences start at zero. A parent stage may use `#` only in higher-level aggregate records; employee task records always use concrete numeric codes. An owner may later change the identifier only through monitor; then record updates existing identifiers and monitor notifies all assistants before subsequent work.

Human shorthand such as `a00` and `e00` may help the owner refer to roles during discussion, but never appears in a task code, package, record, filename, or agent-to-agent message.

## Required employee task package

Use `assets/templates/root/templates/TASK_PACKAGE.md` as the source template. A complete package contains:

1. task code and task name;
2. owner-approved objective and reason for dispatch;
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

The assistant verifies artifacts, validation outputs, scope boundaries, and stated limitations. It then chooses one of: accept as scoped, request correction, report an exception, or recommend owner-authorized promotion.

After dispatch, the assistant remains silent until an employee submits a completion/audit request, an escalation-grade blocker occurs, or the owner intervenes. For long work, the default is: estimate work expected to exceed ten minutes, check status at most once per ten minutes, and have each assistant actively manage no more than five employees. The owner may amend these defaults through monitor.

Employee delivery never by itself authorizes integration, changes a project rule, or establishes a confirmed project fact.
