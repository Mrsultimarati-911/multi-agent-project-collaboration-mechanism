# Project agent entry instructions

This project uses the Multi Agent Project Collaboration Mechanism. `AGENTS.md` and the applicable files in `rules/` are binding project workflow instructions.

1. The human project owner is the sole decision, delegation, exception, integration, and acceptance authority.
2. Read the applicable `rules/` before substantive work. The most restrictive applicable rule wins.
3. `monitor` accepts instructions only from the project owner and may maintain only `AGENTS.md` and `rules/` from owner-confirmed content.
4. `assistant` may plan, dispatch only after owner approval, and audit. It must not directly modify project content without explicit owner authorization.
5. Each `employee` writes only to `ai_workspace/<task-name>/` and only within its approved task package.
6. `record` is the only role permitted to write `work_logs/`; it records submitted facts and audit outcomes only.
7. No agent contacts `monitor`. Escalate exceptions, rule changes, and cross-role conflicts to the owner.
8. No employee task is dispatched without explicit owner approval and a complete task package.

## Project-specific rules

<!-- The monitor adds owner-confirmed project rules here or in rules/. Do not add assumptions. -->
