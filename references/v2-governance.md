# V2 治理主干

## 受控共享

`raw_data/` 是只读原始事实；employee 的隔离交付经 assistant 审核后，使用 `root/publish_artifact.py` 发布为不可覆盖的 `common_data/<artifact>/vNNNN/` 或 `common_artifacts/<artifact>/vNNNN/`。每个版本具有 manifest、sha256、生产任务和审核引用。消费者必须在 Level 2 计划中引用准确版本。

## 多 assistant 与集成

只有 coordinating assistant 管理当前 Level 1 的 Stage DAG、跨模块接口和 `project_demo/`。Module assistant 有唯一模块所有权，可管理所属 employee 并在 `assistant_workspace/<assistant-id>/` 整合。material cross-module change 先由 coordinating assistant 判断是否仍在 Authority Envelope 内；越界则升级负责人。

## Authority Envelope

负责人批准 Level 1 时可授权限定的任务类型、并行量、共享发布、模块集成与 project_demo 集成。R0 读取/分析/测试、R1 workspace 内返工可自主；R2 需 Envelope；R3（project_final、破坏性删除、外部发布、付费或不可逆动作）始终要负责人明确批准。

## 记录与通知

record Agent 负责语义整理；Record Engine 负责字段、引用、状态、依赖和 append-only 合法性。只在 `owner_intervention_required: true` 时，通过 `root/notifications/feishu.py` 发送去重的决策包。webhook/secret 仅来自 `FEISHU_WEBHOOK_URL` / `FEISHU_WEBHOOK_SECRET` 环境变量，缺失或发送失败只产生 warning 并在负责人对话说明。

## V1 兼容

V1 项目仍可读取。缺失 V2 目录和字段仅警告；运行初始化器安全补齐缺失脚手架。项目改名使用 alias，不改写历史任务码。
