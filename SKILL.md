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

1. Confirm that the user is enabling this mechanism and identify the project root and task-code prefix.
2. Read [project layout](references/project-layout.md) and inspect whether the required directories, `AGENTS.md`, and rules exist.
3. If anything is missing, report the exact missing paths and request the owner's authorization before running `scripts/initialize_project.py` or creating anything.
4. Ask the owner for project-specific rules or changes to the defaults. Write or update `AGENTS.md` and `rules/` only as the monitor and only from owner-confirmed content.
5. Before substantive work, every agent reads `AGENTS.md` plus the applicable `rules/` files.

If the project already has an equivalent layout, preserve its content. Repair only missing mechanism files, never overwrite project material without explicit approval.

## Plan, delegate, and audit

Before delegation, read [dispatch and audit](references/dispatch-and-audit.md). The assistant must obtain an explicit approval for each plan or task dispatch. Every employee receives one complete task package and must request assistant audit after completing its bounded delivery. Keep employee context minimal and task-local.

After a delivery, the assistant verifies the stated evidence itself where feasible. It may recommend acceptance, correction, escalation, or an authorized integration; it cannot turn an unverified or unresolved delivery into a confirmed result.

When creating an employee, use the model level explicitly specified by the owner. If none is specified, default to `gpt-5.6-luna` with `high` reasoning. The high-capability/low-cost split remains a recommended staffing pattern, not a replacement for owner authority.

## Work records

Read [work-log governance](references/work-log-governance.md) whenever creating, reviewing, or submitting records. Only the `record` role writes `work_logs/`. Logs contain auditable events, not transcripts, routine updates, or unresolved speculation.

The record role rejects incomplete submissions instead of filling gaps or deciding technical truth. It creates a final employee result only after an explicit assistant audit outcome is supplied.

## Tools and validation

- `scripts/initialize_project.py`: creates missing standard mechanism directories and copies non-project templates and the read-only validator to the project's `root/` directory. Run it only after monitor has found missing paths and the owner has authorized creation. It never overwrites by default.
- `scripts/validate_project_governance.py`: checks layout, task-code shape, and required record/task-package fields. It is read-only.

Run validation after initialization and before treating a record package as structurally valid. Validation checks structure, not whether technical claims are true.

## Boundaries

- A Skill is a workflow instruction, not an operating-system permission boundary. If hard enforcement is required, add appropriate repository or filesystem controls separately.
- Do not automatically create conversations, dispatch employees, alter production assets, or accept a delivery.
- `monitor` only accepts direct owner instructions. Other agents escalate exceptions, rule changes, and cross-role conflicts to the owner, not to the monitor.
- Do not add project-specific facts, model names, secrets, private data, or domain-specific implementation rules to this Skill.
