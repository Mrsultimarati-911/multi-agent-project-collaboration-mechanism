# 二级可恢复中断记录

以下 JSON 是提交给 `root/record_engine.py` 的事件示例。替换 DEMO 身份和引用，先建立真实前置记录/证据，再提交；不要直接写入 `work_logs/`。引擎生成事件编号、时间、序列、hash、`record_status`、`execution_status` 及计划的 `plan_status`/冻结时间。下方叙述提纲应整理入 `event_description`。

```json
{
  "record_type": "level2_warning",
  "task_code": "DEMO_00-00-000-0000",
  "requested_status": "paused",
  "level2_plan_reference": "work_logs/level2_plan_DEMO_00-00-000-0000.md",
  "recovery_owner": "assistant_00",
  "recovery_plan": "在已批准授权边界内执行恢复方案。",
  "resumption_condition": "修正后的命令通过任务内验证。",
  "task_name": "示例任务（按真实目标填写）",
  "responsible_role": "assistant_00",
  "event_description": "在此填写完整的中文事件叙述、验证证据、限制和下一步；不能将示例当作已确认事实。"
}
```

## 中断现象与证据

## 原因判断

## 恢复方案、检查与预期影响

## 关联记录与下一状态

恢复后本 warning 仍保留；若恢复路径失效，创建关联的 `level2_error`，不得覆盖本记录。
