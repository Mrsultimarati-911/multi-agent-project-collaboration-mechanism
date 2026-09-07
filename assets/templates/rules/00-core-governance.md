# Core governance

- status: owner-confirmed baseline required before substantive work
- governance-version: 2
- project-code-prefix: `<SET_BY_OWNER>`
- original-project-identifier: `<SET_BY_OWNER>`
- project-identifier-aliases: []
- task-code-format: `<project-identifier>_<level1-task>-<assistant>-<employee>-<employee-task>`; numeric sequences start at zero
- project-owner: human
- work-language: zh-CN
- default-record-model: `gpt-5.6-luna`
- default-record-reasoning: `medium`
- default-assistant-model: `gpt-5.6-terra`
- default-assistant-reasoning: `high`
- default-employee-model: `gpt-5.6-luna`
- default-employee-reasoning: `high`
- default-rule-amendment: owner instruction -> monitor records replacement
- project-identifier-change: owner -> monitor records alias/mapping -> historical task identities remain immutable
- authority-envelope: owner-approved level1 boundary required for auto-dispatch, shared publishing, or integration
- default-risk-tiers: R0 autonomous read/test; R1 assistant-managed workspace correction; R2 only within authority envelope; R3 owner explicit approval
- notifications: { enabled: true, channels: [feishu], owner-intervention-only: true }
- feishu-notifications: enabled-by-default; persisted startup choice; optional root/notifications/feishu_config.json contains only enabled; credentials environment-only

## Owner-confirmed project-specific rules

<!-- Monitor records only rules explicitly supplied or confirmed by the owner. -->
