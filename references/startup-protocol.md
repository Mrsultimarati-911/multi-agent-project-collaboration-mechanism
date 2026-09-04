# Startup protocol

`monitor` owns the startup sequence after the human enables this Skill in the first project conversation.

## 1. Repair the mechanism layout

Inspect the project root and create every missing standard Skill path immediately. Preserve every existing path and file. The missing layout itself is not a decision that needs another owner approval.

## 2. Ask for the initialization input

Ask the owner for these five items in one concise initialization request:

1. **Project identifier — required.** It becomes the global task-code identifier. Monitor may offer one or more suggestions based on the project name, but only the owner may select or confirm it. Do not substitute `A` or any other value when the owner has not confirmed one.
2. **Record default model and reasoning — optional.** Use `gpt-5.6-luna` / `medium` when omitted.
3. **Assistant default model and reasoning — optional.** Use `gpt-5.6-terra` / `high` when omitted.
4. **Employee default model and reasoning — optional.** Use `gpt-5.6-luna` / `high` when omitted.
5. **Project-specific rules — optional.** An omitted answer means no additional rules at this time.

Do not create `assistant_00` until item 1 is owner-confirmed. Record defaults for omitted optional items in `rules/00-core-governance.md`.

## 3. Bootstrap assistant_00

After recording the initialization, create exactly one conversation named `assistant_00|<initial-scope>`, using the configured assistant default. Give it `assets/templates/root/templates/ASSISTANT_00_STARTUP.md` as its task instruction, with the project-relative locations substituted where useful. This does not grant it permission to dispatch employees or modify formal project content.

`assistant_00` reads existing project reference material, source/data, rules, plans, drafts, and applicable Skills before it asks the owner a prioritized requirement-alignment set of one to ten questions. Fewer than ten questions is allowed; more than ten is not. It waits for the owner's answers before proposing a plan or requesting delegation approval.
