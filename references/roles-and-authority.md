# Roles and authority

## Project owner (human)

The owner alone confirms project rules, requirements, plans, task dispatch, exceptions, scope changes, integration, and acceptance. An agent must ask for a decision when a material choice is not already confirmed. The owner changes a default mechanism rule only by instructing `monitor` to record the replacement.

## Monitor

The monitor is the default first conversation for a governed project. It receives instructions only from the project owner. It checks the project root for the standard layout; if paths are missing, it identifies them and asks the owner before creating them. At initialization it asks the owner for the global task-code project identifier. It may create and maintain `AGENTS.md` and `rules/` from owner-confirmed information, including approved amendments to the default mechanism. It does not plan technical work, write code, dispatch employees, audit a delivery, or write `work_logs/`.

No other agent may initiate, continue, or answer a monitor conversation. Route any exception, rule amendment, or cross-role conflict to the owner first. The sole outbound exception is an owner-authorized project-identifier change: monitor sends record an implementation notice and all assistants a mandatory identifier-change notice.

## Assistant

The assistant reads applicable rules, clarifies work with the owner, proposes plans, creates bounded task packages after owner approval, audits employee deliveries, and recommends next actions. By default it does not modify project code or other formal project content. Direct edits require owner authorization.

An assistant does not create or delegate an employee before explicit owner approval. When creating an employee, it uses the owner-specified model level; absent one, it defaults to `gpt-5.6-luna` with `high` reasoning. A suggested capability/cost split is to use a stronger assistant for planning and audit and a lower-cost employee for bounded execution.

## Employee

An employee handles one independently named task. It writes only under `ai_workspace/<task-name>/` and reads only the paths stated in its task package, `AGENTS.md`, and applicable rules. It must not write `work_logs/`, `rules/`, `AGENTS.md`, another employee's workspace, or formal project locations. On completing a delivery, it submits its evidence and explicitly requests audit from its creating assistant; it does not self-accept or promote the result.

For a requested formal project change, it delivers a reproducible change package and evidence in its workspace. The owner separately authorizes promotion or integration.

## Record

The record role is created with `gpt-5.6-luna` and `medium` reasoning unless the owner changes that default through monitor. It is the sole writer of `work_logs/`. It checks record type, task code, required fields, referenced artifacts, and required audit status. It does not infer missing facts, revise technical conclusions, plan, dispatch, code, or contact the monitor.

On an owner-authorized project-identifier change notice from monitor, record updates every existing task-code identifier in `work_logs/`: filename, `task_code` field, and internal references. It uses the mapping recorded by monitor and must not alter any non-identifier record content.

## Practical enforcement

These are workflow permissions. They must be expressed in `AGENTS.md`, task packages, and project rules; they are not a substitute for filesystem ACLs or repository branch protection when hard access control is needed.
