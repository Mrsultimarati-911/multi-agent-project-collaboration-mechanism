# 一级任务 assistant 完成总结

以下 JSON 是提交给 `root/record_engine.py` 的事件示例。替换 DEMO 身份和引用，先建立真实前置记录/证据，再提交；不要直接写入 `work_logs/`。引擎生成事件编号、时间、序列、hash、`record_status`、`execution_status` 及计划的 `plan_status`/冻结时间。下方叙述提纲应整理入 `event_description`。

```json
{
  "record_type": "level1_summary",
  "task_code": "DEMO_00-00-###-####",
  "requested_status": "active",
  "level1_plan_reference": "work_logs/level1_plan_DEMO_00-##-###-####.md",
  "participating_assistant": "assistant_00",
  "completion_assessment": "任务范围内交付及证据已审核，等待负责人阶段验收。",
  "audit_evidence": "ai_workspace/DEMO_00-00-000-0000/delivery.txt",
  "exception_references": [],
  "task_name": "示例任务（按真实目标填写）",
  "responsible_role": "assistant_00",
  "event_description": "在此填写完整的中文事件叙述、验证证据、限制和下一步；不能将示例当作已确认事实。"
}
```

## 完成评估与最终实现路径

## 已完成交付与审核证据

## 异常、限制与遗留项

## 下一阶段交接与建议
