# 二级最终结果

以下 JSON 是提交给 `root/record_engine.py` 的事件示例。替换 DEMO 身份和引用，先建立真实前置记录/证据，再提交；不要直接写入 `work_logs/`。引擎生成事件编号、时间、序列、hash、`record_status`、`execution_status` 及计划的 `plan_status`/冻结时间。下方叙述提纲应整理入 `event_description`。

引擎自动将审核引用固定为 `.md#event_id`。结果必须紧随真实 accepted audit；该审核已匹配最近提交的轮次、路径及内容 hash。摘要必须引用该结果的同一审核，不能跳过状态或接受未提交文件。

```json
{
  "record_type": "level2_results",
  "task_code": "DEMO_00-00-000-0000",
  "requested_status": "accepted",
  "level2_plan_reference": "work_logs/level2_plan_DEMO_00-00-000-0000.md",
  "level2_results_mid_reference": "work_logs/level2_results_mid_DEMO_00-00-000-0000.md",
  "assistant_audit_reference": "work_logs/level2_results_mid_DEMO_00-00-000-0000.md",
  "assistant_audit_status": "accepted",
  "task_name": "示例任务（按真实目标填写）",
  "responsible_role": "assistant_00",
  "event_description": "在此填写完整的中文事件叙述、验证证据、限制和下一步；不能将示例当作已确认事实。"
}
```

## 最终完成情况与交付物

## 验证与审核证据

## 已接受范围与不得外推边界

## 限制、遗留项与下一状态
