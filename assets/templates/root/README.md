# 根目录机制工具

此目录保存由“多智能体项目协作机制”安装到项目内的本地工具和模板。它不是交付工作区，也不是生产源码目录。

- `validate_project_governance.py`：执行 V1/V2 兼容的只读目录、记录与 manifest 校验。
- `record_engine.py`：对结构化治理事件执行确定性校验与 append-only 写入。
- `governance_schema.py`：供记录引擎与校验器共用的记录类型、状态、字段、身份和路径规范。
- `publish_artifact.py`：将已审核工件发布为不可覆盖的共享版本。
- `notifications/feishu.py`：对 `owner_intervention_required: true` 的去重升级事件，以及启用后的启动连通性检查发送飞书提醒；凭证只从环境变量读取，成功须通过飞书业务响应校验。
- `templates/`：保存任务包、记录、接口契约、artifact manifest 与治理事件源模板。

记录模板中的 JSON 交给 Record Engine 校验；不要手工生成权威 Markdown 的机器元数据。新共享版本采用 `manifest.json`，旧 JSON 内容的 `manifest.yaml` 可兼容读取。项目 JSON 只允许通知开关，不保存 URL 或 SECRET；`.gitignore` 只追加固定的本地状态保护项。
