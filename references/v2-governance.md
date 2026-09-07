# V2 治理主干

## 受控共享

`raw_data/` 是只读原始事实；employee 的隔离交付经 assistant 审核后，使用 `root/publish_artifact.py` 发布为不可覆盖的 `common_data/<artifact>/vNNNN/` 或 `common_artifacts/<artifact>/vNNNN/`。新版本统一生成 `manifest.json`，包括 SHA-256、合法生产任务和已接受的 scoped delivery 审核引用。校验器重新计算 hash 并检查 provenance。消费者必须在 Level 2 计划中引用 artifact ID 和准确版本，不得默认读取 latest。旧 JSON 内容的 `manifest.yaml` 仅供兼容读取。

发布源和目标都必须留在项目允许路径内；artifact ID 和版本不得携带路径，版本为 `v0001` 这类至少四位数字编号。拒绝目录穿越、外部源路径和 symlink 逃逸；已有版本不可覆盖。

发布源必须恰好是 accepted audit 的 `employee_delivery_reference` 指定的完整文件或目录，不允许从已审核目录中隐式切出子路径。引擎在 submitted 时生成 delivery SHA-256 快照；audited 必须对应最近 submitted 的同一 attempt_number 和路径，接受时还必须匹配提交快照，不能换成未提交文件。发布前比较快照，发布后校验 payload、manifest 和 audit 三者一致。离线 provenance 校验不要求原工作区永久保留。要发布不同范围，先提交并审核该完整范围。

发布授权独立于 employee 派发：`owner-approved` dispatch 本身不授予共享发布权。目标类型必须在父阶段 `authority_envelope.publish_permissions` 中为 true，或 Level 2 plan 包含真实 `owner_publication_approval_evidence` 文件引用。

## 多 assistant 与集成

只有 coordinating assistant 管理当前 Level 1 的 Stage DAG、跨模块接口和 `project_demo/`。Module assistant 有唯一模块所有权，可管理所属 employee 并在 `assistant_workspace/<assistant-id>/` 整合。material cross-module change 先由 coordinating assistant 判断是否仍在 Authority Envelope 内；越界则升级负责人。

进入 `integrated` 的新状态转换必须提供 `integration_target`。模块集成限于 `assistant_workspace/<responsible-assistant>/`；`project_demo/` 仅 coordinating assistant 可写，并须匹配 Envelope 的 integration_permissions。`project_final/` 或未获 Envelope 授权的集成需要真实 `owner_integration_approval_evidence`，但该证据不放宽角色/目录所有权边界，不能授权模块 assistant 写别人的工作区或绕过 coordinator。

## Authority Envelope

Level 1 必须由负责人明确批准，包括其中的 Authority Envelope。Level 2 合法授权来源只有 `owner-approved` 或 `envelope-authorized`。后者必须引用匹配的、已获负责人批准的 Level 1 Envelope，并满足所有限制，不需要为每个 employee 再次请求负责人。

在 Envelope 内，assistant 默认可以自主进行：employee 创建、派发和替换；retry、correction、re-run、bug fix、test failure rework、task-local refactoring；`common_data` / `common_artifacts` 发布；模块集成；获授权的 `project_demo` 集成。前提是不改变 Level 1 目标和实质交付、不突破 task type、并行上限、读写范围和风险等级。R0 为读取/分析/测试，R1 为工作区内修正，R2 必须在 Envelope 内，R3 始终需要明确人工批准。

以下行为必须由负责人明确介入：

```text
change_project_goal
material_scope_expansion
change_core_research_hypothesis
material_methodology_change
new_final_deliverable
overwrite_raw_data
destructive_delete
external_publish
paid_external_action
production_action
project_final_write_or_acceptance
authority_envelope_breach
unresolved_cross_assistant_conflict
unresolved_final_integration_blocker
```

## 记录与通知

record Agent 将事实整理为 JSON governance event；Record Engine 使用与 validator 相同的 `governance_schema.py`，验证字段、引用、实际历史状态、依赖和追加合法性，生成可读 Markdown 及统一机器元数据。`expected_previous_status` 只是一项断言；真实前态来自权威记录。状态、计划冻结与记录落盘分别使用 `execution_status`、`plan_status`、`record_status`，详见 [记录规范](work-log-governance.md)。Stage DAG 和 Level 2 DAG 必须无环；workstream 所有者唯一；依赖达到要求状态后才可运行。

引擎会将记录引用固定为 `.md#event_id`，避免后续追加改变引用含义。`required_dependency_status` 只接受 `accepted`、`integrated`、`closed`，默认 accepted；不能用 planned/running 等状态放行下游任务。

若暂停/失败链包含 `owner_intervention_required: true`，恢复或终止前必须提供真实 `owner_resolution_reference` 文件证据；后续 warning 不能清除该人工介入条件，飞书 resolved 状态也不能替代该证据。

飞书只用于提醒，普通事件必须满足 `owner_intervention_required: true`；默认开启时的一次启动连通性检查是明确的启动例外。真实 URL/SECRET 仅来自 `FEISHU_WEBHOOK_URL` / `FEISHU_WEBHOOK_SECRET` 环境变量。项目的 `feishu_config_example.json` 和可选 `feishu_config.json` 只能含非敏感 `enabled` 开关，禁止存储凭据。初始化会持久化负责人的开关选择，重复运行保留原选择；显式修改通过追加治理配置覆盖生效。

通知状态为 `pending`、`sent`、`failed`、`resolved`。HTTP 200 还需飞书业务返回成功才记为 sent；失败和缺环境变量均返回项目负责人对话说明。相同未解决 event 默认不重复发送，`material_update: true` 允许重新提醒；处理后可标记 resolved。没有飞书审批功能。

修正环境变量后使用 `python root/notifications/feishu.py . --startup --material-update` 重试启动连通性。`--resolve EVENT_ID` 只闭合通知状态；正式决定仍在项目对话和记录中完成。

初始化器仅幂等追加固定 `.gitignore` 行以保护通知运行时状态和遗留配置，不删改既有规则。

## V1 兼容

`governance-version: 1` 项目可只读校验，缺少 V2 目录、Envelope、manifest 只警告；初始化可补齐缺失脚手架且不覆盖旧记录。`governance-version: 2` 执行严格规则。项目改名由 monitor 保存原标识、当前标识和负责人确认的 aliases；旧任务码、文件名和引用永久保留，新任务可以使用当前标识。
