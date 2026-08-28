# Dispatch and audit

## Approval gate

The assistant may propose a plan or task package, but only an explicit owner confirmation authorizes dispatch. Discussion, an agent recommendation, or an unreviewed draft is not authorization.

## Task code

Use `P_<phase>-<assistant>-<employee>-<serial>`:

```text
P_01-00-003-0007
```

The prefix is set at project initialization and may be a project abbreviation. Phase, assistant, employee, and serial are zero-padded numeric identifiers. A parent stage may use `##` or `###` only in higher-level aggregate records; employee task records use concrete numeric codes.

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

An employee asks for clarification or escalates if the task conflicts with rules, has missing inputs, needs a new authority, or cannot meet the declared boundary.

## Audit and promotion

The assistant verifies artifacts, validation outputs, scope boundaries, and stated limitations. It then chooses one of: accept as scoped, request correction, report an exception, or recommend owner-authorized promotion.

For long work, the recommended default is: estimate work expected to exceed ten minutes, check status at most once per ten minutes, and have each assistant actively manage no more than five employees. The project rules may override these recommendations.

Employee delivery never by itself authorizes integration, changes a project rule, or establishes a confirmed project fact.
