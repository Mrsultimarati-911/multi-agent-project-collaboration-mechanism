# Startup protocol

`monitor` owns the startup sequence after the human enables this Skill in the first project conversation.

## 1. Repair the V2 mechanism layout

Inspect the project root and create missing standard Skill paths, including `common_data/`, `common_artifacts/`, `assistant_workspace/` and `plan/interfaces/`. Enabling the Skill authorizes this startup scaffolding and idempotent append of fixed notification runtime `.gitignore` rules. Preserve existing files and ignore rules. Explicit owner configuration changes may append a governance override; ordinary repeated initialization preserves prior choices.

## 2. Ask for the initialization input

Ask the owner for these seven items in one concise initialization request:

1. **Project identifier — required.** It becomes the global task-code identifier. Monitor may offer one or more suggestions based on the project name, but only the owner may select or confirm it. Do not substitute `A` or any other value when the owner has not confirmed one.
2. **Record default model and reasoning — optional.** Use `gpt-5.6-luna` / `medium` when omitted.
3. **Assistant default model and reasoning — optional.** Use `gpt-5.6-terra` / `high` when omitted.
4. **Employee default model and reasoning — optional.** Use `gpt-5.6-luna` / `high` when omitted.
5. **Project-specific rules — optional.** An omitted answer means no additional rules at this time.
6. **Work language — optional.** Use Chinese (`zh-CN`) when omitted. When Chinese is selected, all record narrative text is Chinese and record uses `_CN` templates.
7. **Feishu notifications — optional.** Enabled by default for new projects; preserve the prior choice on repeated initialization unless explicitly changed. Persist the chosen boolean in core governance. Enabled startup permits one connectivity notification, `<identifier>_项目已启动飞书监控`, as a narrow exception to the owner-intervention-only event rule. Invoke the adapter; never read or write credential values. It reads `FEISHU_WEBHOOK_URL` and optional `FEISHU_WEBHOOK_SECRET` from the environment. Optional project JSON contains only `enabled`; it is not a credential file. Missing credentials, business errors or transport failures mean not connected and require a current owner-conversation fallback with configuration/disablement guidance; initialization itself remains usable.

Do not create `assistant_00` until item 1 is owner-confirmed. Record defaults for omitted optional items, including `work-language: zh-CN` and notifications enabled, in `rules/00-core-governance.md`. Explicit `--feishu-notifications disabled` persists false; an existing core receives an append-only `notifications-enabled` override. HTTP success alone does not establish connectivity: the adapter requires a successful Feishu business response.

After the owner repairs configuration/environment, retry with `python root/notifications/feishu.py . --startup --material-update`; plain `--startup` remains deduplicated, including failed unresolved attempts. `--resolve EVENT_ID` closes only the local notification state after the project decision, never grants approval. Event paths supplied through `--event` are project-relative.

## 3. Bootstrap assistant_00

After recording the initialization, create two bootstrap conversations:

1. `record|工作记录`, using the configured record default. Instruct it that it is the sole `work_logs/` writer; it receives assistant-audited log events and may receive a `level2_summary` only from that task's employee.
2. `assistant_00|<initial-scope>`, using the configured assistant default. Give it `assets/templates/root/templates/ASSISTANT_00_STARTUP.md` as its task instruction, with the project-relative locations substituted where useful.

This does not grant monitor permission to create any further role conversation, nor grant `assistant_00` permission to dispatch employees or modify formal project content.

`assistant_00` reads existing project reference material, source/data, rules, plans, drafts, and applicable Skills before it asks the owner a prioritized requirement-alignment set of one to ten questions. Fewer than ten questions is allowed; more than ten is not. It waits for the owner's answers before proposing a plan or requesting delegation approval.
