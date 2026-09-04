# V2 升级说明

## 基线

- V1 基线分支：`main`
- V1 基线提交：`d2ad33f5df7efaa96b14bb41704fc6f472a78831`
- V2 开发分支：`v2`
- 分支创建日期：2026-09-04

## V2 目标

V2 在保留 V1 的人类最终决策、隔离 employee 工作区、两级计划、可审计记录和受控交付原则的基础上，增加：受控共享工件、多 assistant 模块协作、Authority Envelope、确定性 Record Engine，以及仅用于负责人升级提醒的飞书通知适配层。

## 兼容策略

- `main` 保持 V1，不在 V2 验收前合并、重写或删除。
- 初始化器仅创建缺失的 V2 治理脚手架，绝不覆盖项目已有内容。
- V1 `work_logs/` 继续可读；缺失 V2 字段或目录时，校验器以 legacy warning 而非无理由的致命错误处理。
- V2 发布的共享数据和工件使用版本目录与 manifest，不将 `common_data/` 或 `common_artifacts/` 变成自由共享写目录。
- V1 中“项目标识变更后改写既有任务码”的规则在 V2 中被历史身份不可变规则取代：改名通过 alias/mapping 表达，不改写旧记录。

## 设计边界

V2 不实现飞书审批、无限 assistant 层级、自由共享写目录、分布式消息队列或自动生产环境变更。飞书仅在 `owner_intervention_required: true` 时发送去重后的决策提醒，审批仍必须在项目对话中完成。
