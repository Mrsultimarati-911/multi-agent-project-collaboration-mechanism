# Role and filesystem rules

Use the standard role boundaries and filesystem routing from `AGENTS.md`. The default startup role is `monitor`; it creates missing standard paths, requests the owner's required project identifier and optional role defaults/rules, and then creates `assistant_00`. Monitor may suggest but not choose the identifier. Role defaults are held in `00-core-governance.md`: assistant `gpt-5.6-terra` / `high`, employee `gpt-5.6-luna` / `high`, record `gpt-5.6-luna` / `medium`, unless owner-confirmed values replace them. Every employee delivery must request assistant audit. Add only owner-confirmed exceptions below.

<!-- Project-specific exceptions or stricter restrictions. -->
