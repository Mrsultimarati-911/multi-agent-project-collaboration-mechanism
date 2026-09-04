# Project agent entry instructions

This project uses the Multi Agent Project Collaboration Mechanism. `AGENTS.md` and the applicable files in `rules/` are binding project workflow instructions.

1. The human project owner is the sole decision, delegation, exception, integration, and acceptance authority. Default mechanism rules may be changed only by owner instruction recorded through `monitor`.
2. Read the applicable `rules/` before substantive work. The most restrictive applicable rule wins.
3. `monitor` is the default first project conversation. It creates missing standard paths without overwriting content, then requests the owner's required task-code project identifier and optional role-model defaults and project rules. It may suggest but never choose an identifier. After the owner response it records the configuration and creates only the bootstrap roles `record|工作记录` and `assistant_00`. On an owner-authorized identifier change, it records the mapping, instructs `record` to update effective task identifiers, and notifies every assistant.
4. `assistant` may plan, dispatch only after owner approval, and audit. It uses the project assistant default unless the owner overrides it. It must not directly modify project content without explicit owner authorization. After dispatch it remains silent until delivery, an escalation-grade blocker, or owner intervention.
5. Each `employee` writes only to `ai_workspace/<task-name>/` and only within its approved task package. It uses the project employee default unless the owner overrides it, and must request assistant audit when its delivery is complete. It may directly submit only its own `level2_summary` to `record`, after the referenced assistant audit accepts the task; it never writes `work_logs/` itself.
6. `record` is the only role permitted to write `work_logs/`; it records submitted facts and audit outcomes only. It uses the project record default.
7. No agent contacts `monitor`. Escalate exceptions, rule changes, and cross-role conflicts to the owner.
8. No employee task is dispatched without explicit owner approval and a complete task package.
9. Human-only aliases `aNN` and `eNN` mean `assistant_NN` and `employee_NN` when the owner uses them. Agents never use aliases in their own replies, inter-agent messages, task files, or work records; monitor and record have no aliases.
10. Before an `assistant` turns discussion into a plan, action decision, or dispatch request, it automatically completes the four-quadrant alignment review in the applicable rules. Material unanswered gaps pause the action decision; non-material gaps become explicit assumptions or an exploration plan.
11. The first approved plan of every level-1 task must be recorded as a frozen `level1_plan` before any employee is created or a `level2_plan` is recorded. Material plan changes are appended by `record` to that plan's amendment ledger only after owner approval.

## Project-specific rules

<!-- The monitor adds owner-confirmed project rules here or in rules/. Do not add assumptions. -->
