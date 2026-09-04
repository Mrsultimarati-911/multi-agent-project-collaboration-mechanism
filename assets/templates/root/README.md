# 根目录机制工具

此目录保存由“多智能体项目协作机制”安装到项目内的本地工具和模板。它不是交付工作区，也不是生产源码目录。

- `validate_project_governance.py`：执行 V1/V2 兼容的只读目录、记录与 manifest 校验。
- `record_engine.py`：对结构化治理事件执行确定性校验与 append-only 写入。
- `publish_artifact.py`：将已审核工件发布为不可覆盖的共享版本。
- `notifications/feishu.py`：只对 `owner_intervention_required: true` 的去重升级事件发送飞书提醒；凭证只从环境变量读取。
- `templates/`：保存任务包、记录、接口契约、artifact manifest 与治理事件源模板。
