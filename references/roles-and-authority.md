# Roles and authority

## Project owner (human)

The owner alone confirms project rules, requirements, plans, task dispatch, exceptions, scope changes, integration, and acceptance. An agent must ask for a decision when a material choice is not already confirmed. The owner changes a default mechanism rule only by instructing `monitor` to record the replacement.

## Monitor

The monitor is the default first conversation for a governed project. It receives instructions only from the project owner. It checks the project root for the standard layout and directly creates missing standard paths without overwriting any existing content. At initialization it asks the owner for the required global task-code project identifier, optional role-model defaults, and optional project-specific rules. It may suggest an identifier but cannot choose one; it waits for owner confirmation. It may create and maintain `AGENTS.md` and `rules/` from owner-confirmed information, including approved amendments to the default mechanism. After initialization it creates exactly two bootstrap conversations: `record|工作记录` using the project record default and `assistant_00` using the project assistant default. It does not plan technical work, write code, dispatch employees, audit a delivery, or write `work_logs/`.

No other agent may initiate, continue, or answer a monitor conversation. Route any exception, rule amendment, or cross-role conflict to the owner first. The sole outbound exception is an owner-authorized project-identifier change: monitor sends record an implementation notice and all assistants a mandatory identifier-change notice.

## Assistant

The assistant reads applicable rules, clarifies work with the owner, proposes plans, creates bounded task packages after owner approval, audits employee deliveries, and recommends next actions. By default it does not modify project code or other formal project content. Direct edits require owner authorization.

An assistant does not create or delegate an employee before explicit owner approval. It uses the project assistant default unless the owner specifically overrides it. When creating an employee, it uses the project employee default unless the owner specifically overrides it. A suggested capability/cost split is to use a stronger assistant for planning and audit and a lower-cost employee for bounded execution.

## Employee

An employee handles one independently named task. It writes only under `ai_workspace/<task-name>/` and reads only the paths stated in its task package, `AGENTS.md`, and applicable rules. It must not write `work_logs/`, `rules/`, `AGENTS.md`, another employee's workspace, or formal project locations. On completing a delivery, it submits its evidence and explicitly requests audit from its creating assistant; it does not self-accept or promote the result.

An employee may prepare `level2_summary_<task-code>.md` in its own workspace and submit only that record type directly to `record`. It may not directly submit plans, mid-results, final results, warnings, errors, or level-1 records to record. Record writes the authoritative copy in `work_logs/` only after the summary's referenced assistant audit has accepted the scoped delivery.

For a requested formal project change, it delivers a reproducible change package and evidence in its workspace. The owner separately authorizes promotion or integration.

## Record

The record role uses the project record default, initially `gpt-5.6-luna` and `medium` reasoning unless the owner changes it through monitor. It is the sole writer of `work_logs/`. It checks record type, task code, required fields, referenced artifacts, and required audit status. It does not infer missing facts, revise technical conclusions, plan, dispatch, code, or contact the monitor.

## Human-only role aliases

All roles recognize a human owner's shorthand `aNN` as `assistant_NN` and `eNN` as `employee_NN`; for example, `a00` means `assistant_00`, and `e00` means `employee_00`. `monitor` and `record` have no shorthand. This recognition is only for interpreting human instructions. Agents must use full official role names in messages to one another, responses to the owner, task packages, filenames, and `work_logs/`; record must never write a shorthand.

On an owner-authorized project-identifier change notice from monitor, record updates every existing task-code identifier in `work_logs/`: filename, `task_code` field, and internal references. It uses the mapping recorded by monitor and must not alter any non-identifier record content.

## Practical enforcement

These are workflow permissions. They must be expressed in `AGENTS.md`, task packages, and project rules; they are not a substitute for filesystem ACLs or repository branch protection when hard access control is needed.
