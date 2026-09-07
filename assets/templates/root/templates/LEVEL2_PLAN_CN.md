# 二级执行计划

以下 JSON 是提交给 `root/record_engine.py` 的事件示例。替换 DEMO 身份和引用，先建立真实前置记录/证据，再提交；不要直接写入 `work_logs/`。引擎生成事件编号、时间、序列、hash、`record_status`、`execution_status` 及计划的 `plan_status`/冻结时间。下方叙述提纲应整理入 `event_description`。

示例采用 `envelope-authorized`。若使用直接批准，改为 `owner-approved`，填写真实 `owner_dispatch_approval_evidence` 文件引用；不得把讨论当成授权。边界内返工和替换无需重复批准；超出 Envelope 或 R3 必须负责人明确批准。

引擎将计划/审核引用固定为 `.md#event_id`。`required_dependency_status` 仅允许 accepted、integrated、closed，默认 accepted；不能填写 planned/running。共享发布还需父阶段对应的 `publish_permissions` 为 true，或本计划内真实 `owner_publication_approval_evidence`；仅批准派发不等于批准发布。

```json
{
  "record_type": "level2_plan",
  "task_code": "DEMO_00-00-000-0000",
  "requested_status": "planned",
  "responsible_assistant": "assistant_00",
  "responsible_employee": "employee_00",
  "level1_plan_reference": "work_logs/level1_plan_DEMO_00-##-###-####.md",
  "dispatch_authority": "envelope-authorized",
  "authority_envelope_reference": "work_logs/level1_plan_DEMO_00-##-###-####.md",
  "task_type": "data_processing",
  "risk_level": "R1",
  "workspace": "ai_workspace/DEMO_00-00-000-0000",
  "allowed_reads": [
    "raw_data"
  ],
  "allowed_writes": [
    "ai_workspace/DEMO_00-00-000-0000"
  ],
  "depends_on": [],
  "required_dependency_status": {},
  "consumes": [],
  "produces": [],
  "interface_references": [],
  "task_name": "示例任务（按真实目标填写）",
  "responsible_role": "assistant_00",
  "event_description": "在此填写完整的中文事件叙述、验证证据、限制和下一步；不能将示例当作已确认事实。"
}
```

## 已授权任务

## 输入与允许范围

- required_reads:
- supplied_input_artifacts:
- allowed_reads:
- allowed_writes:
- 禁止写入或操作：
- 已确认决策与固定假设：

## 执行路径

## 验证与审核

- owner_publication_approval_evidence：仅父阶段未授权该发布类型而负责人另行批准时填写真实证据引用。
- 计划集成时注明 integration_target，以及匹配的 Envelope 权限或 owner_integration_approval_evidence；批准不改变角色目录边界。

## 交付与记录链路

## 升级与暂停条件

## 冻结基线

基线不可覆盖。边界内的修正使用已有 Envelope；越界、R3 或 Level 1 实质变更才需要负责人明确批准。不同任务目标/交付使用新任务码和计划，可继续使用匹配的 Envelope。变更通过引擎追加事件，不手工修改旧 JSON 块。

冻结后的范围、依赖或授权变更同样创建新身份和计划，用 `supersedes_reference` 关联；旧任务需另行按合法状态取消，不能由引用自动改变状态。

## 替代计划证据提纲（作为叙述事件提交，不编辑冻结计划）

| 日期 | 变更原因 | 批准证据或 Envelope 引用 | 影响范围 | 决定/替代记录 | 记录人 |
|---|---|---|---|---|---|
| | | | | | record |
