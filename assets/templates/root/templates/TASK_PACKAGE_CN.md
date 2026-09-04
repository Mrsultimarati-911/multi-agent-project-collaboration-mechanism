# Employee 任务包

- task_code: `<project-identifier>_<level1-task>-<assistant>-<employee>-<employee-task>`
- task_name:
- dispatch_status: `owner-approved | envelope-authorized`
- level1_plan_reference:
- level2_plan_reference:
- responsible_employee:
- expected_duration:
- depends_on: []
- consumes: []
- produces: []
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

## 已确认决策、验收和验证

- 不可变更的确认决策：
- 四象限对齐摘要：
- 验收标准与验证命令：

## 交付、审核与升级

完成后必须向创建自己的 assistant 提交工件、证据并明确请求审核。通过审核前，完成不等于验收。只有 assistant 接受后，才可向 record 直接提交本任务的 `level2_summary`。

- Authority Envelope 边界：
- owner_intervention_required 触发条件：
- 通知路径：仅 governance / record event 可调用飞书适配器；employee 不得直接通知飞书。
