# 一级任务汇总最终结果

以下 JSON 是提交给 `root/record_engine.py` 的事件示例。替换 DEMO 身份和引用，先建立真实前置记录/证据，再提交；不要直接写入 `work_logs/`。引擎生成事件编号、时间、序列、hash、`record_status`、`execution_status` 及计划的 `plan_status`/冻结时间。下方叙述提纲应整理入 `event_description`。

```json
{
  "record_type": "level1_results",
  "task_code": "DEMO_00-##-###-####",
  "requested_status": "accepted",
  "level1_plan_reference": "work_logs/level1_plan_DEMO_00-##-###-####.md",
  "source_level1_summaries": [
    "work_logs/level1_summary_DEMO_00-00-###-####.md"
  ],
  "source_level2_results": [
    "work_logs/level2_results_DEMO_00-00-000-0000.md"
  ],
  "owner_acceptance_reference": "rules/owner-acceptance.md",
  "reusable_outputs": [],
  "task_name": "示例任务（按真实目标填写）",
  "responsible_role": "assistant_00",
  "event_description": "在此填写完整的中文事件叙述、验证证据、限制和下一步；不能将示例当作已确认事实。"
}
```

## 经负责人验收的目标结果

## 汇总交付物与验证证据

## 可复用产物、决策与交接输入

## 异常、限制与下一阶段约束
