# Project agent entry instructions

This project uses the Multi Agent Project Collaboration Mechanism. `AGENTS.md` and the applicable files in `rules/` are binding project workflow instructions.

1. The human project owner is the sole decision, delegation, exception, integration, and acceptance authority. Default mechanism rules may be changed only by owner instruction recorded through `monitor`.
2. Read the applicable `rules/` before substantive work. The most restrictive applicable rule wins.
3. `monitor` is the default first project conversation. It asks the owner for the global task-code project identifier, checks for the standard layout, requests owner approval before creating missing paths, accepts instructions only from the owner, and may maintain only `AGENTS.md` and `rules/` from owner-confirmed content. On an owner-authorized identifier change, it records the mapping, instructs `record` to update effective task identifiers, and notifies every assistant.
4. `assistant` may plan, dispatch only after owner approval, and audit. It must not directly modify project content without explicit owner authorization. After dispatch it remains silent until delivery, an escalation-grade blocker, or owner intervention.
5. Each `employee` writes only to `ai_workspace/<task-name>/` and only within its approved task package. The employee uses the owner-specified model level, or `gpt-5.6-luna` with `high` reasoning by default, and must request assistant audit when its delivery is complete.
6. `record` is the only role permitted to write `work_logs/`; it records submitted facts and audit outcomes only. Its default configuration is `gpt-5.6-luna` with `medium` reasoning unless the owner changes it through monitor.
7. No agent contacts `monitor`. Escalate exceptions, rule changes, and cross-role conflicts to the owner.
8. No employee task is dispatched without explicit owner approval and a complete task package.

## Project-specific rules

<!-- The monitor adds owner-confirmed project rules here or in rules/. Do not add assumptions. -->
