# Project agent entry instructions

This project uses the Multi Agent Project Collaboration Mechanism. `AGENTS.md` and the applicable files in `rules/` are binding project workflow instructions.

1. The human project owner is the sole decision, delegation, exception, integration, and acceptance authority. Default mechanism rules may be changed only by owner instruction recorded through `monitor`.
2. Read the applicable `rules/` before substantive work. The most restrictive applicable rule wins.
3. `monitor` is the default first project conversation. It creates missing standard paths without overwriting content, then requests the owner's required task-code project identifier and optional role-model defaults and project rules. It may suggest but never choose an identifier. After the owner response it records the configuration and creates only the bootstrap roles `record|工作记录` and `assistant_00`. On an owner-authorized identifier change, it records the mapping, instructs `record` to update effective task identifiers, and notifies every assistant.
4. `assistant` may plan, audit and dispatch within an owner-approved Level 1 Authority Envelope; outside that envelope it requires owner approval. The coordinating assistant owns Level 1 integration and `project_demo/`; module assistants own only their declared module and `assistant_workspace/<assistant-id>/`. It uses the project assistant default unless the owner overrides it.
5. Each `employee` writes only to `ai_workspace/<task-name>/` and only within its approved task package. It may consume only cited shared artifact versions, never directly publish or overwrite `common_data/` / `common_artifacts/`, and must request assistant audit when complete. It may directly submit only its own accepted `level2_summary` to `record`; it never writes `work_logs/` itself.
6. `record` is the only role permitted to write human-readable `work_logs/`; `root/record_engine.py` decides structural and state legality. It uses the project record default.
7. No agent contacts `monitor`. Escalate exceptions, rule changes, and cross-role conflicts to the owner.
8. No employee task is dispatched without a complete task package and either explicit owner approval or an applicable approved Authority Envelope.
9. Human-only aliases `aNN` and `eNN` mean `assistant_NN` and `employee_NN` when the owner uses them. Agents never use aliases in their own replies, inter-agent messages, task files, or work records; monitor and record have no aliases.
10. Before an `assistant` turns discussion into a plan, action decision, or dispatch request, it automatically completes the four-quadrant alignment review in the applicable rules. Material unanswered gaps pause the action decision; non-material gaps become explicit assumptions or an exploration plan.
11. The first approved plan of every level-1 task must be recorded as a frozen `level1_plan` before any employee is created or a `level2_plan` is recorded. Material plan changes are appended by `record` to that plan's amendment ledger only after owner approval.
12. Every employee requires its own frozen `level2_plan` before the employee conversation is created or instructed. It must cite the parent `level1_plan`; a changed objective or deliverable receives a new task code and plan rather than rewriting the original.
13. `level2_results_mid` is the only append-only attempt ledger. Warning and error records remain after recovery; final results and summary/result records are new authoritative files, not renamed versions of prior records.
14. `work-language` is configured in `rules/00-core-governance.md` and defaults to `zh-CN`. In Chinese projects, record uses `_CN` templates and all record narrative text is Chinese; stable metadata keys remain English.
15. Shared data/artifacts are immutable versioned publishes with manifests. Cross-module interface contracts live in `plan/interfaces/`; material interface changes route through the coordinating assistant and escalate if beyond the Authority Envelope.
16. Only `owner_intervention_required: true` governance events may invoke the Feishu adapter. Secrets are environment-only; notification failure is a warning and must be surfaced in the owner conversation.

## Project-specific rules

<!-- The monitor adds owner-confirmed project rules here or in rules/. Do not add assumptions. -->
