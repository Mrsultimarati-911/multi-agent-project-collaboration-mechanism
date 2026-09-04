---
name: multi-agent-project-collaboration-mechanism
description: Establish and operate an explicitly enabled, human-led multi-agent project workflow with monitor-led initialization, isolated execution, assistant audit gates, and append-only work records. Use only when the user explicitly enables this mechanism for a project or invokes $multi-agent-project-collaboration-mechanism.
---

# Multi Agent Project Collaboration Mechanism

Use this Skill only after the project owner explicitly enables it. It governs collaboration, authority, work locations, delegation, and evidence records; it does not supply project facts, product requirements, or domain architecture. Pair it with `$my-context-manage` when the project also needs durable project-context management.

## Operating principle

The human project owner is the sole authority for decisions, scope, delegation approval, exceptions, rule amendments, and final acceptance. Treat explicit user approval as the only approval evidence. Never infer it from a discussion, a likely preference, or an agent's recommendation.

The mechanism's rules are defaults, not immutable policy. Only the owner may change a default, by giving the change to `monitor`; monitor records the owner-confirmed replacement in `AGENTS.md` or `rules/`. Until then, the defaults below remain binding.

Use five roles:

- `monitor`: first project agent; formalizes owner-provided project rules and maintains governance only.
- `assistant`: plans, decomposes, dispatches after approval, audits deliveries, and proposes integration.
- `employee`: executes one bounded task in its own workspace.
- `record`: validates and writes auditable work logs only.
- project owner: the human decision maker.

Read [roles and authority](references/roles-and-authority.md) before assigning a role or changing permissions.

## Start or repair a governed project

The first conversation of a governed project is normally `monitor`. It establishes the project-specific rules with the owner, inspects the project root for the mechanism layout, and routes all later agents through `AGENTS.md`.

1. Confirm that the user is enabling this mechanism and identify the project root. Read [project layout](references/project-layout.md) and inspect whether the required directories, `AGENTS.md`, and rules exist.
2. Create every missing standard path immediately with `scripts/initialize_project.py`; it is a startup exception and does not require a separate authorization. Never overwrite existing project content.
3. Ask the owner for the following initialization values: required global task-code project identifier; optional `record`, `assistant`, and `employee` default model/reasoning; and optional project-specific rules. See [startup protocol](references/startup-protocol.md).
4. The identifier must be explicitly supplied or confirmed by the owner. Monitor may propose a concise identifier based on the project name but must not choose one itself. For every optional item left unspecified, write the Skill default. Treat an omitted project-specific rule set as no additional project-specific rules.
5. Write the initialization result to `AGENTS.md` and `rules/` only as monitor and only after the owner reply. Before substantive work, every agent reads `AGENTS.md` plus the applicable `rules/` files.
6. After the required identifier is recorded, monitor creates `record|工作记录` using the configured record default and `assistant_00` using the configured assistant default. It sends `assistant_00` the startup task in `assets/templates/root/templates/ASSISTANT_00_STARTUP.md`. This narrow bootstrap exception does not authorize monitor to create any other assistant or employee.

### Change a project identifier

Only the owner may request a task-code project-identifier change through `monitor`. When this occurs, monitor records the old-to-new mapping and effective decision in the rules, instructs `record` to update every already-effective identifier (including filenames, code fields, and internal references), and notifies every assistant before any further task is created or audited. This is a narrow owner-authorized exception to normal append-only record handling; do not apply it to any other historical fact.

If the project already has an equivalent layout, preserve its content. Repair only missing mechanism files, never overwrite project material without explicit approval.

## Plan, delegate, and audit

Before turning a discussion into a plan, action decision, or employee dispatch request, the assistant automatically applies [four-quadrant alignment](references/four-quadrant-alignment.md) to the owner's prior discussion and current project state. Do not wait for a separate owner invocation. This is a planning-quality gate, not an additional delegation authority.

Before delegation, read [dispatch and audit](references/dispatch-and-audit.md). The assistant must obtain an explicit approval for each plan or task dispatch. Every employee receives one complete task package and must request assistant audit after completing its bounded delivery. Keep employee context minimal and task-local.

After a delivery, the assistant verifies the stated evidence itself where feasible. It may recommend acceptance, correction, escalation, or an authorized integration; it cannot turn an unverified or unresolved delivery into a confirmed result.

Use the owner-confirmed project defaults when creating `assistant`, `employee`, and `record`, unless the owner explicitly overrides a single creation. Skill defaults are: `assistant` = `gpt-5.6-terra` / `high`; `employee` = `gpt-5.6-luna` / `high`; `record` = `gpt-5.6-luna` / `medium`. The high-capability/low-cost split remains a recommended staffing pattern, not a replacement for owner authority.

## Work records

Read [work-log governance](references/work-log-governance.md) whenever creating, reviewing, or submitting records. Only the `record` role writes `work_logs/`. Logs contain auditable events, not transcripts, routine updates, or unresolved speculation.

Before an assistant submits the first approved stage plan, read [level-1 plan record](references/level1-plan-record.md) and use `assets/templates/root/templates/LEVEL1_PLAN.md`. A `level1_plan` is the frozen action contract that precedes every employee dispatch; material changes use its record-managed amendment ledger rather than silent edits.

Before an assistant creates or dispatches an employee, read [level-2 plan record](references/level2-plan-record.md) and use `assets/templates/root/templates/LEVEL2_PLAN.md`. A `level2_plan` is the frozen, concrete execution authorization for that employee and must reference its recorded `level1_plan`.

For execution, exception, completion, or stage-close records, read [remaining work-record types](references/remaining-work-record-types.md) and use the matching template. `level2_results_mid` is the only append-only attempt ledger; warning and error preserve an interruption classification; final results and summaries are new records, never renames of earlier ones.

The record role rejects incomplete submissions instead of filling gaps or deciding technical truth. It creates a final employee result only after an explicit assistant audit outcome is supplied. An employee may submit only its own `level2_summary` directly to record; every other work-log event follows the assistant audit route.

## Tools and validation

- `scripts/initialize_project.py`: creates missing standard mechanism directories and copies non-project templates and the read-only validator to the project's `root/` directory. Run it only after monitor has found missing paths and the owner has authorized creation. It never overwrites by default.
- `scripts/validate_project_governance.py`: checks layout, task-code shape, and required record/task-package fields. It is read-only.

Run validation after initialization and before treating a record package as structurally valid. Validation checks structure, not whether technical claims are true.

## Boundaries

- A Skill is a workflow instruction, not an operating-system permission boundary. If hard enforcement is required, add appropriate repository or filesystem controls separately.
- Do not automatically create conversations, dispatch employees, alter production assets, or accept a delivery, except for monitor's one-time creation of `record|工作记录` and `assistant_00` after the owner completes required initialization.
- `monitor` only accepts direct owner instructions. Other agents escalate exceptions, rule changes, and cross-role conflicts to the owner, not to the monitor.
- Do not add project-specific facts, model names, secrets, private data, or domain-specific implementation rules to this Skill.
