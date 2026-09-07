# 一级可恢复中断记录

以下 JSON 是提交给 `root/record_engine.py` 的事件示例。替换 DEMO 身份和引用，先建立真实前置记录/证据，再提交；不要直接写入 `work_logs/`。引擎生成事件编号、时间、序列、hash、`record_status`、`execution_status` 及计划的 `plan_status`/冻结时间。下方叙述提纲应整理入 `event_description`。

```json
{
  "record_type": "level1_warning",
  "task_code": "DEMO_00-00-###-####",
  "requested_status": "active",
  "level1_plan_reference": "work_logs/level1_plan_DEMO_00-##-###-####.md",
  "recovery_owner": "assistant_00",
  "recovery_plan": "在已批准授权边界内执行恢复方案。",
  "affected_scope": [
    "DEMO_00-00-000-0000"
  ],
  "task_name": "示例任务（按真实目标填写）",
  "responsible_role": "assistant_00",
  "event_description": "在此填写完整的中文事件叙述、验证证据、限制和下一步；不能将示例当作已确认事实。"
}
```

## 阶段性中断与证据

## 原因判断及受影响员工/流程

## 恢复方案与验证

## 关联记录与下一状态
