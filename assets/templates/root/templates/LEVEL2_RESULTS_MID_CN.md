# 二级可审核交付台账

以下 JSON 是提交给 `root/record_engine.py` 的事件示例。替换 DEMO 身份和引用，先建立真实前置记录/证据，再提交；不要直接写入 `work_logs/`。引擎生成事件编号、时间、序列、hash、`record_status`、`execution_status` 及计划的 `plan_status`/冻结时间。下方叙述提纲应整理入 `event_description`。

同一台账记录 dispatched、running、submitted、audited 等事件，每个状态单独提交。派发/运行时 `employee_delivery_reference` 可为 null，audit 为 `not_requested`；提交时为 `pending`；审核时状态为 `audited`，audit 必须是 `accepted` 或 `rejected`。返工后递增 attempt_number，旧事件不改。

引擎自动将记录引用固定为 `.md#event_id`，并在 submitted 时生成交付 hash。audited 必须匹配最近 submitted 的同一轮次和完整路径；接受审核还需与提交快照内容相同。换文件或改内容后必须先重新提交，不能直接接受未提交交付。

首次进入 `integrated` 必填 `integration_target`：负责 assistant 自有的 `assistant_workspace/<assistant-id>/`，或仅 coordinator 可写的 `project_demo/`，同时匹配 Envelope 集成权限。`project_final/` 或 Envelope 未授权的集成须提供真实 `owner_integration_approval_evidence`；该批准不放宽角色和目录所有权边界。必须记录经验证的完整目标，不能只声明“已集成”。

```json
{
  "record_type": "level2_results_mid",
  "task_code": "DEMO_00-00-000-0000",
  "requested_status": "submitted",
  "level2_plan_reference": "work_logs/level2_plan_DEMO_00-00-000-0000.md",
  "attempt_number": 1,
  "employee_delivery_reference": "ai_workspace/DEMO_00-00-000-0000/delivery.txt",
  "assistant_audit_status": "pending",
  "task_name": "示例任务（按真实目标填写）",
  "responsible_role": "assistant_00",
  "event_description": "在此填写完整的中文事件叙述、验证证据、限制和下一步；不能将示例当作已确认事实。"
}
```

## 第 1 轮

- attempt_number: 1
- submission_timestamp:
- employee_delivery_reference:
- 交付范围：
- artifact_paths:
- verification_commands_or_experiments:
- 观察到的输出：
- 员工报告的限制：
- assistant_audit_status: pending / accepted / rejected（按实际审核状态填写）
- assistant_audit_timestamp:
- assistant_audit_reference:
- 审核发现：
- 返工要求或下一步：

## 后续轮次（仅 record 追加）
