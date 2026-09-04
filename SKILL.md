---
name: multi-agent-project-collaboration-mechanism
description: Establish and operate an explicitly enabled, human-led V2 multi-agent workflow with isolated execution, controlled shared artifacts, bounded assistant autonomy, deterministic governance, and owner escalation. Use only when the user explicitly enables this mechanism for a project or invokes $multi-agent-project-collaboration-mechanism.
---

# Multi Agent Project Collaboration Mechanism

Use this Skill only after the project owner explicitly enables it. It governs collaboration, authority, work locations, delegation, and evidence records; it does not supply project facts, product requirements, or domain architecture. Pair it with `$my-context-manage` when the project also needs durable project-context management.

## Operating principle

The human project owner is the sole authority for decisions, scope, delegation approval, exceptions, rule amendments, and final acceptance. Treat explicit user approval as the only approval evidence. Never infer it from a discussion, a likely preference, or an agent's recommendation.

The mechanism's rules are defaults, not immutable policy. Only the owner may change a default, by giving the change to `monitor`; monitor records the owner-confirmed replacement in `AGENTS.md` or `rules/`. Until then, the defaults below remain binding.

Use the same five roles, with a bounded execution topology:

- `monitor`: first project agent; formalizes owner-provided project rules and maintains governance only.
- `assistant`: plans, decomposes, dispatches after approval, audits deliveries, and proposes integration.
- `employee`: executes one bounded task in its own workspace.
- `record`: validates and writes auditable work logs only.
- project owner: the human decision maker.

V2 permits `Owner → coordinating assistant → module assistant → employee`, and no deeper automatic assistant nesting. Read [V2 governance](references/v2-governance.md) before multi-assistant delegation, shared publication, Authority Envelope use, record-engine submission, or owner escalation.

Read [roles and authority](references/roles-and-authority.md) before assigning a role or changing permissions.

## Start or repair a governed project

The first conversation of a governed project is normally `monitor`. It establishes the project-specific rules with the owner, inspects the project root for the mechanism layout, and routes all later agents through `AGENTS.md`.

1. Confirm that the user is enabling this mechanism and identify the project root. Read [project layout](references/project-layout.md) and inspect whether the required directories, `AGENTS.md`, and rules exist.
2. Create every missing standard path immediately with `scripts/initialize_project.py`; it is a startup exception and does not require a separate authorization. Never overwrite existing project content.
3. Ask the owner for the following initialization values: required global task-code project identifier; optional `record`, `assistant`, and `employee` default model/reasoning; optional work language; and optional project-specific rules. See [startup protocol](references/startup-protocol.md).
4. The identifier must be explicitly supplied or confirmed by the owner. Monitor may propose a concise identifier based on the project name but must not choose one itself. For every optional item left unspecified, write the Skill default. Work language defaults to Chinese (`zh-CN`), which requires Chinese narrative text and `_CN` record templates. Treat an omitted project-specific rule set as no additional project-specific rules.
5. Write the initialization result to `AGENTS.md` and `rules/` only as monitor and only after the owner reply. Before substantive work, every agent reads `AGENTS.md` plus the applicable `rules/` files.
6. After the required identifier is recorded, monitor creates `record|工作记录` using the configured record default and `assistant_00` using the configured assistant default. It sends `assistant_00` the startup task in `assets/templates/root/templates/ASSISTANT_00_STARTUP.md`. This narrow bootstrap exception does not authorize monitor to create any other assistant or employee.

### Change a project identifier

Only the owner may request a project-identifier change through `monitor`. Monitor records an alias/mapping and effective decision in the rules. Historical task codes, filenames and references remain immutable; only new tasks use the new identifier or mapping. Notify all assistants before creating further tasks.

If the project already has an equivalent layout, preserve its content. Repair only missing mechanism files, never overwrite project material without explicit approval.

## Plan, delegate, and audit

Before turning a discussion into a plan, action decision, or employee dispatch request, the assistant automatically applies [four-quadrant alignment](references/four-quadrant-alignment.md) to the owner's prior discussion and current project state. Do not wait for a separate owner invocation. This is a planning-quality gate, not an additional delegation authority.

Before delegation, read [dispatch and audit](references/dispatch-and-audit.md) and [V2 governance](references/v2-governance.md). Level 1 remains owner-approved, but its Authority Envelope may authorize bounded dispatch, retry, correction, shared publication and integration without repeated owner approval. Every employee receives one complete task package and must request assistant audit after completing its bounded delivery. Keep employee context minimal and task-local.

After a delivery, the assistant verifies the stated evidence itself where feasible. It may recommend acceptance, correction, escalation, or an authorized integration; it cannot turn an unverified or unresolved delivery into a confirmed result.

Use the owner-confirmed project defaults when creating `assistant`, `employee`, and `record`, unless the owner explicitly overrides a single creation. Skill defaults are: `assistant` = `gpt-5.6-terra` / `high`; `employee` = `gpt-5.6-luna` / `high`; `record` = `gpt-5.6-luna` / `medium`. The high-capability/low-cost split remains a recommended staffing pattern, not a replacement for owner authority.

## Work records

Read [work-log governance](references/work-log-governance.md) whenever creating, reviewing, or submitting records. Only the `record` role writes `work_logs/`. Logs contain auditable events, not transcripts, routine updates, or unresolved speculation.

Before an assistant submits the first approved stage plan, read [level-1 plan record](references/level1-plan-record.md) and use `assets/templates/root/templates/LEVEL1_PLAN.md`. A `level1_plan` is the frozen action contract that precedes every employee dispatch; material changes use its record-managed amendment ledger rather than silent edits.

Before an assistant creates or dispatches an employee, read [level-2 plan record](references/level2-plan-record.md) and use `assets/templates/root/templates/LEVEL2_PLAN.md`. A `level2_plan` is the frozen, concrete execution authorization for that employee and must reference its recorded `level1_plan`.

For execution, exception, completion, or stage-close records, read [remaining work-record types](references/remaining-work-record-types.md) and use the matching template. `level2_results_mid` is the only append-only attempt ledger; warning and error preserve an interruption classification; final results and summaries are new records, never renames of earlier ones.

The record role rejects incomplete submissions instead of filling gaps or deciding technical truth. It creates a final employee result only after an explicit assistant audit outcome is supplied. An employee may submit only its own `level2_summary` directly to record; every other work-log event follows the assistant audit route.

## V2 controlled sharing, integration, and escalation

Employees never write shared locations directly. The only shared route is `workspace → assistant audit → publish_artifact.py → versioned common_data/ or common_artifacts/ manifest`. Module assistants integrate only inside their own `assistant_workspace/<assistant-id>/`; the coordinating assistant alone integrates the current Level 1 into `project_demo/`. `project_final/`, destructive/external/paid operations and all R3 actions always require explicit owner approval.

Record prepares factual Chinese events; `record_engine.py` determines structural, state, dependency, reference and append-only legality. Invoke `notifications/feishu.py` only from a governance event with `owner_intervention_required: true`; it reads secrets exclusively from environment variables, deduplicates unresolved events and never treats Feishu as approval.

## Tools and validation

- `scripts/initialize_project.py`: creates missing V2 governance scaffolding, including shared directories, assistant workspaces and root tools; it never overwrites project content.
- `scripts/publish_artifact.py`: publishes an assistant-audited immutable artifact version and manifest.
- `scripts/record_engine.py`: validates and appends structured governance events.
- `scripts/notifications/feishu.py`: sends owner-only escalation decision packages when environment credentials exist.
- `scripts/validate_project_governance.py`: read-only V1/V2 layout, record and manifest checker.

Run validation after initialization and before treating a record package as structurally valid. Validation checks structure, not whether technical claims are true.

## Boundaries

- A Skill is a workflow instruction, not an operating-system permission boundary. If hard enforcement is required, add appropriate repository or filesystem controls separately.
- Do not automatically create conversations, dispatch employees, alter production assets, or accept a delivery, except for monitor's one-time creation of `record|工作记录` and `assistant_00` after the owner completes required initialization. An approved Authority Envelope is the only exception to repeated owner approval for bounded V2 dispatch and correction.
- `monitor` only accepts direct owner instructions. Other agents escalate exceptions, rule changes, and cross-role conflicts to the owner, not to the monitor.
- Do not add project-specific facts, model names, secrets, private data, or domain-specific implementation rules to this Skill.
