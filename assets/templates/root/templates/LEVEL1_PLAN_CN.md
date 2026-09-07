# 一级行动计划

以下 JSON 是提交给 `root/record_engine.py` 的事件示例。替换 DEMO 身份和引用，先建立真实前置记录/证据，再提交；不要直接写入 `work_logs/`。引擎生成事件编号、时间、序列、hash、`record_status`、`execution_status` 及计划的 `plan_status`/冻结时间。下方叙述提纲应整理入 `event_description`。

此示例 Envelope 只展示结构；由负责人明确确认其具体值才生效。owner_approval_evidence 必须指向真实批准证据。冻结后使用事件追加保留变更链，不覆盖基线。

```json
{
  "record_type": "level1_plan",
  "task_code": "DEMO_00-##-###-####",
  "requested_status": "planned",
  "accountable_assistant": "assistant_00",
  "coordinating_assistant": "assistant_00",
  "participating_assistants": [
    "assistant_00"
  ],
  "workstreams": {
    "MAIN": {
      "owner": "assistant_00",
      "depends_on": []
    }
  },
  "authority_envelope": {
    "auto_dispatch": true,
    "max_module_assistants": 0,
    "max_parallel_employees_per_assistant": 5,
    "allowed_task_types": [
      "data_processing",
      "testing"
    ],
    "allowed_reads": [
      "raw_data",
      "common_data",
      "common_artifacts",
      "ai_workspace"
    ],
    "allowed_writes": [
      "ai_workspace"
    ],
    "publish_permissions": {
      "common_data": true,
      "common_artifacts": true
    },
    "integration_permissions": {
      "assistant_workspace": true,
      "project_demo": false,
      "project_final": false
    },
    "prohibited_without_owner": [
      "change_project_goal",
      "material_scope_expansion",
      "change_core_research_hypothesis",
      "material_methodology_change",
      "new_final_deliverable",
      "overwrite_raw_data",
      "destructive_delete",
      "external_publish",
      "paid_external_action",
      "production_action",
      "project_final_write_or_acceptance",
      "authority_envelope_breach",
      "unresolved_cross_assistant_conflict",
      "unresolved_final_integration_blocker"
    ]
  },
  "owner_approval_evidence": "rules/owner-approval.md",
  "task_name": "示例任务（按真实目标填写）",
  "responsible_role": "assistant_00",
  "event_description": "在此填写完整的中文事件叙述、验证证据、限制和下一步；不能将示例当作已确认事实。"
}
```

## 负责人确认的目标

## 已确认背景、边界与输入

## 四象限对齐结论

## 实现与验证路径

## 计划委派地图

| Employee | 计划任务码 | 任务目标 | 预期交付 | 工作区 | 依赖 | 审核人 |
|---|---|---|---|---|---|---|
| | | | | | | |

## 审核、集成与负责人验收

## 风险与升级条件

## 冻结基线

已记录基线不可改写。目标或 Envelope 的实质变更创建负责人批准的新一级计划和新身份，用 `supersedes_reference` 指向旧计划；下表只组织变更原因及引用，不改变旧计划的可执行权限。

## 替代计划证据提纲（作为叙述事件提交，不编辑冻结计划）

| 日期 | 变更原因 | 负责人批准证据 | 影响范围 | 决定/替代记录 | 记录人 |
|---|---|---|---|---|---|
| | | | | | record |
