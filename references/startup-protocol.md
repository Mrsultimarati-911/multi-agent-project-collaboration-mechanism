# Startup protocol

`monitor` owns the startup sequence after the human enables this Skill in the first project conversation.

## 1. Repair the V2 mechanism layout

Inspect the project root and create every missing standard Skill path immediately, including `common_data/`, `common_artifacts/`, `assistant_workspace/` and `plan/interfaces/`. Enabling this Skill is authorization to create missing governance scaffolding, never to overwrite existing project content.

## 2. Ask for the initialization input

Ask the owner for these six items in one concise initialization request:

1. **Project identifier — required.** It becomes the global task-code identifier. Monitor may offer one or more suggestions based on the project name, but only the owner may select or confirm it. Do not substitute `A` or any other value when the owner has not confirmed one.
2. **Record default model and reasoning — optional.** Use `gpt-5.6-luna` / `medium` when omitted.
3. **Assistant default model and reasoning — optional.** Use `gpt-5.6-terra` / `high` when omitted.
4. **Employee default model and reasoning — optional.** Use `gpt-5.6-luna` / `high` when omitted.
5. **Project-specific rules — optional.** An omitted answer means no additional rules at this time.
6. **Work language — optional.** Use Chinese (`zh-CN`) when omitted. When Chinese is selected, all record narrative text is Chinese and record uses `_CN` templates.
7. **Feishu notifications — optional.** Enabled by default. The owner may disable them during initialization. When enabled, monitor checks `root/notifications/feishu_config.json`; only the local notification service may read it. If present, send one startup monitoring check. On failure, report that monitoring is not connected and offer configuration guidance or disablement.

Do not create `assistant_00` until item 1 is owner-confirmed. Record defaults for omitted optional items, including `work-language: zh-CN`, in `rules/00-core-governance.md`.

## 3. Bootstrap assistant_00

After recording the initialization, create two bootstrap conversations:

1. `record|工作记录`, using the configured record default. Instruct it that it is the sole `work_logs/` writer; it receives assistant-audited log events and may receive a `level2_summary` only from that task's employee.
2. `assistant_00|<initial-scope>`, using the configured assistant default. Give it `assets/templates/root/templates/ASSISTANT_00_STARTUP.md` as its task instruction, with the project-relative locations substituted where useful.

This does not grant monitor permission to create any further role conversation, nor grant `assistant_00` permission to dispatch employees or modify formal project content.

`assistant_00` reads existing project reference material, source/data, rules, plans, drafts, and applicable Skills before it asks the owner a prioritized requirement-alignment set of one to ten questions. Fewer than ten questions is allowed; more than ten is not. It waits for the owner's answers before proposing a plan or requesting delegation approval.
