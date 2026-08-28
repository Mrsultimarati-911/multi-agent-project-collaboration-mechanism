---
name: multi-agent-project-collaboration-mechanism
description: Establish and operate an explicitly enabled, human-led multi-agent project workflow with role boundaries, isolated workspaces, auditable delivery records, and controlled delegation. Use only when the user explicitly enables this mechanism for a project or invokes $multi-agent-project-collaboration-mechanism.
---

# Multi Agent Project Collaboration Mechanism

Use this Skill only after the project owner explicitly enables it. It governs collaboration, authority, work locations, delegation, and evidence records; it does not supply project facts, product requirements, or domain architecture. Pair it with `$my-context-manage` when the project also needs durable project-context management.

## Operating principle

The human project owner is the sole authority for decisions, scope, delegation approval, exceptions, and final acceptance. Treat explicit user approval as the only approval evidence. Never infer it from a discussion, a likely preference, or an agent's recommendation.

Use five roles:

- `monitor`: first project agent; formalizes owner-provided project rules and maintains governance only.
- `assistant`: plans, decomposes, dispatches after approval, audits deliveries, and proposes integration.
- `employee`: executes one bounded task in its own workspace.
- `record`: validates and writes auditable work logs only.
- project owner: the human decision maker.

Read [roles and authority](references/roles-and-authority.md) before assigning a role or changing permissions.

## Start or repair a governed project

For a new project, the monitor first gathers the owner's project-specific rules, then initializes the standard layout and routes all agents through `AGENTS.md`.

1. Confirm that the user is enabling this mechanism and identify the project root and project code prefix.
2. Read [project layout](references/project-layout.md) and run `scripts/initialize_project.py` only with the user's approval.
3. Ask the owner for project-specific rules; do not invent them. Write or update `AGENTS.md` and `rules/` only as the monitor and only from owner-confirmed content.
4. Before substantive work, every agent reads `AGENTS.md` plus the applicable `rules/` files.

If the project already has an equivalent layout, preserve its content. Repair only missing mechanism files, never overwrite project material without explicit approval.

## Plan, delegate, and audit

Before delegation, read [dispatch and audit](references/dispatch-and-audit.md). The assistant must obtain an explicit approval for each plan or task dispatch. Every employee receives one complete task package. Keep employee context minimal and task-local.

After a delivery, the assistant verifies the stated evidence itself where feasible. It may recommend acceptance, correction, escalation, or an authorized integration; it cannot turn an unverified or unresolved delivery into a confirmed result.

Use the high-capability/low-cost split as a recommendation, not a requirement. Select actual models and reasoning settings according to the project and task.

## Work records

Read [work-log governance](references/work-log-governance.md) whenever creating, reviewing, or submitting records. Only the `record` role writes `work_logs/`. Logs contain auditable events, not transcripts, routine updates, or unresolved speculation.

The record role rejects incomplete submissions instead of filling gaps or deciding technical truth. It creates a final employee result only after an explicit assistant audit outcome is supplied.

## Tools and validation

- `scripts/initialize_project.py`: creates missing standard mechanism directories and copies non-project templates and the read-only validator to the project's `root/` directory. It never overwrites by default.
- `scripts/validate_project_governance.py`: checks layout, task-code shape, and required record/task-package fields. It is read-only.

Run validation after initialization and before treating a record package as structurally valid. Validation checks structure, not whether technical claims are true.

## Boundaries

- A Skill is a workflow instruction, not an operating-system permission boundary. If hard enforcement is required, add appropriate repository or filesystem controls separately.
- Do not automatically create conversations, dispatch employees, alter production assets, or accept a delivery.
- `monitor` only accepts direct owner instructions. Other agents escalate exceptions, rule changes, and cross-role conflicts to the owner, not to the monitor.
- Do not add project-specific facts, model names, secrets, private data, or domain-specific implementation rules to this Skill.
