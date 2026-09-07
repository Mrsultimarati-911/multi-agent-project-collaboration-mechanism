# Roles and authority

## Project owner (human)

The owner confirms project rules, Level 1 objectives and Authority Envelopes, material scope changes, R3 actions, exceptions and final acceptance. Level 2 dispatch and bounded corrections may use an existing matching owner-approved envelope. Request a decision only when the required authority is absent or the action is owner-reserved. The owner changes a default mechanism rule by instructing `monitor` to record the replacement.

## Monitor

The monitor is the default first conversation for a governed project. It receives instructions only from the project owner. It checks the project root for the standard layout and directly creates missing standard paths without overwriting any existing content. At initialization it asks the owner for the required global task-code project identifier, optional role-model defaults, and optional project-specific rules. It may suggest an identifier but cannot choose one; it waits for owner confirmation. It may create and maintain `AGENTS.md` and `rules/` from owner-confirmed information, including approved amendments to the default mechanism. After initialization it creates exactly two bootstrap conversations: `record|工作记录` using the project record default and `assistant_00` using the project assistant default. It does not plan technical work, write code, dispatch employees, audit a delivery, or write `work_logs/`.

No other agent may initiate, continue, or answer a monitor conversation. Route any exception, rule amendment, or cross-role conflict to the owner first. The sole outbound exception is an owner-authorized project-identifier change: monitor sends record an implementation notice and all assistants a mandatory identifier-change notice.

## Assistant

The assistant reads rules, aligns requirements, proposes Level 1 plans, creates bounded Level 2 packages under explicit owner approval or a matching owner-approved Authority Envelope, and audits deliveries. Within that envelope it may manage creation, dispatch, retry, correction, re-run, bug fixes, test rework, task-local refactoring, employee replacement, shared publication and permitted integration. It must preserve the Level 1 objective and material deliverable, task types, concurrency, risk and read/write scopes.

Every Level 1 requires explicit owner approval; each Level 2 records `owner-approved` or `envelope-authorized` as its authority source before employee creation. A module assistant integrates only in its own `assistant_workspace/<assistant-id>/`; the coordinating assistant alone may perform envelope-authorized `project_demo/` integration. `project_final/` and all R3 actions require explicit owner approval. Role model defaults apply unless the owner overrides them; capability/cost tiers remain staffing suggestions.

## Employee

An employee handles one independently named task. It writes only under `ai_workspace/<task-name>/` and reads only the paths stated in its task package, `AGENTS.md`, and applicable rules. It must not write `work_logs/`, `rules/`, `AGENTS.md`, another employee's workspace, or formal project locations. On completing a delivery, it submits its evidence and explicitly requests audit from its creating assistant; it does not self-accept or promote the result.

An employee may prepare `level2_summary_<task-code>.md` in its own workspace and submit only that record type directly to `record`. It may not directly submit plans, mid-results, final results, warnings, errors, or level-1 records to record. Record writes the authoritative copy in `work_logs/` only after the summary's referenced assistant audit has accepted the scoped delivery.

For a requested formal project change, it delivers a reproducible change package and evidence in its workspace. The assistant uses the existing envelope for permitted publication/integration, or obtains explicit owner approval when the action is outside that envelope or R3. The employee itself never publishes or integrates shared/formal outputs.

## Record

The record role uses the project record default, initially `gpt-5.6-luna` and `medium` reasoning unless the owner changes it through monitor. It is the sole writer of `work_logs/`. It checks record type, task code, required fields, referenced artifacts, and required audit status. It does not infer missing facts, revise technical conclusions, plan, dispatch, code, or contact the monitor.

## Human-only role aliases

All roles recognize a human owner's shorthand `aNN` as `assistant_NN` and `eNN` as `employee_NN`; for example, `a00` means `assistant_00`, and `e00` means `employee_00`. `monitor` and `record` have no shorthand. This recognition is only for interpreting human instructions. Agents must use full official role names in messages to one another, responses to the owner, task packages, filenames, and `work_logs/`; record must never write a shorthand.

Historical task identity is immutable. On an owner-authorized project-identifier change, monitor records original/current identifiers and owner-confirmed aliases, then notifies record and every assistant. Record never renames old files or rewrites historical task codes or references. New tasks may use the current identifier; validators accept the recorded historical aliases.

## Practical enforcement

These are workflow permissions. They must be expressed in `AGENTS.md`, task packages, and project rules; they are not a substitute for filesystem ACLs or repository branch protection when hard access control is needed.
