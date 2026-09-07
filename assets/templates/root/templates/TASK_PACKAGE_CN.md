# Employee 任务包

- task_code: `<project-identifier>_<level1-task>-<assistant>-<employee>-<employee-task>`
- task_name:
- dispatch_authority: `owner-approved | envelope-authorized`
- owner_dispatch_approval_evidence: 仅 owner-approved 时填写
- authority_envelope_reference: envelope-authorized 时引用匹配且负责人已批准的 Level 1
- level1_plan_reference:
- level2_plan_reference:
- responsible_employee:
- expected_duration:
- depends_on: []
- required_dependency_status: {}（仅 accepted / integrated / closed，默认 accepted）
- consumes: []
- produces: []
- interface_references: []
- task_type:
- risk_level: R0 / R1 / R2 / R3
- base_revision:
- worktree_or_branch:
- conflict_scope:

## 目标与必须读取的内容

- 任务目标：
- required_reads:
- supplied_input_artifacts:

## 允许范围

- allowed_reads:
- allowed_writes: `ai_workspace/<task-name>/`
- 禁止操作：不得直接发布或覆盖 `common_data/`、`common_artifacts/`、`work_logs/`、其他 workspace 或 raw_data。
- 保持 Level 1 目标和实质交付、任务类型、并发与读写边界；共享输入指定 artifact_id 和准确 version，不读取 latest。边界内返工/修正/测试重试/任务内重构使用已有授权；超出 Envelope 或 R3 必须负责人明确批准。
- 发布独立于派发授权，须父阶段对应 publish_permissions 或 Level 2 计划的真实 owner_publication_approval_evidence。先提交完整交付，接受审核必须匹配提交轮次、路径与 hash。集成必须声明 integration_target 及对应授权，并保持 assistant/coordinator 的目录所有权。

## 已确认决策、验收和验证

- 不可变更的确认决策：
- 四象限对齐摘要：
- 验收标准与验证命令：

## 交付、审核与升级

完成后必须向创建自己的 assistant 提交工件、证据并明确请求审核。通过审核前，完成不等于验收。只有 assistant 接受后，才可向 record 直接提交本任务的 `level2_summary`。

- Authority Envelope 边界：
- owner_intervention_required 触发条件：
- 通知路径：仅 governance / record event 可调用飞书适配器；employee 不得直接通知飞书。
