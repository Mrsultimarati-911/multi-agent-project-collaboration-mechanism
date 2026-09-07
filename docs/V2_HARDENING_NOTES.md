# V2 Hardening 工作记录

## 分支与基线

- 工作日期：2026-09-06；2026-09-07 恢复并完成提交前复验。
- 工作分支：`v2`。
- starting_v2_sha：`21f20f0ddec81beacd51f3d02fdf8b2bb6cd6d05`。
- main / origin/main 保留基线：`d2ad33f5df7efaa96b14bb41704fc6f472a78831`。
- 开始前已 fetch origin，确认 v2 与 origin/v2 一致、工作树干净。
- 仅建立本地 v2 逻辑提交；未修改、merge、rebase、删除、覆盖或 force-push main，也未执行 v2 → main。
- 最终提交 SHA 由交付消息及 `git rev-parse v2` 提供，避免在 commit 内容中自引用其自身 SHA。

## 逐阶段问题与修复

| 计划阶段 | 已发现问题 | 本轮修复 |
|---|---|---|
| 1：规范一致性 | V1 的逐 employee 再次批准与 V2 自治冲突 | Level 1 必须 owner-approved；Level 2 统一 owner-approved / envelope-authorized；限定 task type、读写、并发、风险；R3/实质变化仍升级负责人 |
| 2：项目身份 | 改名规则残留历史任务码重写 | original/current/owner-confirmed aliases 合法；历史 task_code、文件名、引用不改写 |
| 3：共享 schema | 模板、引擎、validator 字段不同 | 新增 governance_schema.py；11 类 enum 与对应任务码模式、字段和状态共用；复制到项目 root/ |
| 4：状态模型 | approved-active 等复合 status 与运行状态冲突 | record_status=final、plan_status=frozen、execution_status 分离；Level 1 与 Level 2 分别定义状态机 |
| 5：真实前态 | caller 可自报 previous_status 绕过状态机 | 从 work_logs 回放真实前态；expected_previous_status 仅断言；拒绝 running→accepted、空审核与 rejected 审核 |
| 6：机器回读 | Markdown 缺统一可解析元数据 | 引擎生成 JSON front matter（YAML 子集）、event_id、全局序号和 hash 链；叙述须与元数据一致；所有记录引用固定为 .md#event_id |
| 7：路径 | 任意 record_type、artifact ID/version 与外部源可注入路径 | 类型 enum、安全 regex、项目相对路径与 resolve containment；检测 symlink/junction；拒绝外部源、越界写入与重叠 employee 工作区 |
| 8：manifest | YAML 文件名配 JSON 内容与 YAML 模板混用 | 新发布和模板仅 manifest.json / ARTIFACT_MANIFEST.json；旧 JSON-compatible manifest.yaml 只读兼容 |
| 9：provenance | 只检查字段和文件存在，未绑定真实审核内容 | 校验 producer/plan、accepted audit、实际状态链；submitted 快照绑定审核；发布前后 hash 与审核一致；版本不可覆盖、准确版本消费 |
| 10：DAG/接口 | 依赖只检查存在，接口仅字符串 | Stage workstream DAG、Level 2 DAG 缺失/自依赖/环检查；依赖只可要求 accepted/integrated/closed；接口 JSON 必含 identity/version/owner/consumers |
| 11：飞书 | 签名参数颠倒、HTTP 200 即成功、凭证 JSON 化 | URL/SECRET 环境变量唯一来源；官方 HMAC；明确业务成功码；pending/sent/failed/resolved 去重、material update 与项目内 fallback |
| 12：初始化配置 | disabled 只打印、不生效 | 写入真实治理配置；重复初始化保留；显式修改已有选择只追加 notifications-enabled |
| 13：忽略规则 | 初始化行为与“禁止改既有文件”模糊 | 明确 startup scaffold exception：仅幂等追加固定通知运行时/遗留配置规则；不删改原字节 |
| 14：兼容 | V1 因缺 V2 目录被整体 FAIL | governance-version:1 缺 V2 特性 warning；legacy 日志只读、不冒充新授权；V2 canonical 严格检查 |
| 15：回归测试 | 依赖人工观察 | 新增 unittest 标准库套件、临时 fixtures、网络 mocks；所有指定测试文件齐全 |
| 16：E2E | 没有完整工具链证据 | 初始化→批准一级计划/Envelope→二级执行→提交/审核/接受→common_data v0001→下游消费→复制到项目的 validator PASS；非法直接接受 REJECTED |
| 17：文档同步 | 文档/模板与代码行为脱节 | 更新 SKILL、中文 README、AGENTS、rules、references、22 个中英文记录模板和统一 JSON 示例 |

### 独立复核追加发现

1. 聚合任务文件名中的 `#` 被当成引用锚点：改为识别 `.md#` 分隔符。
2. 历史回放仍读取原 delivery，清理工作区后无法继续：新事件做实时文件检查，历史回放验证记录 scope/hash；已发布内容可脱离源工作区校验。
3. caller 可将依赖门槛指定为 planned：限制为 accepted / integrated / closed。
4. 裸审核引用会随后续台账追加漂移：引擎自动固定 event_id，摘要比较审核身份。
5. submitted attempt 1 后可直接审核另一个 attempt/文件：audited 必须匹配最近 submitted 的 attempt/path，接受还须匹配提交 hash。
6. integration_permissions 全 false 仍可记 integrated：新增转换必须明确 integration_target，并检查角色所有权、Envelope 或真实 owner 证据；project_final 始终要求 owner。
7. owner-approved dispatch 被误当成共享发布许可：共享发布单独要求 Envelope 类型许可或 plan 中真实 owner_publication_approval_evidence。
8. Publisher 仅校验可重算 hash、不重放语义链：provenance 同时重放 canonical 状态链。
9. 来源可能在 provenance 检查与复制之间变化：复制前、复制后和源复查均须与提交/审核快照一致。
10. 空批准文件被当成有效证据：拒绝空证据；未设置负责人确认项目标识时，拒绝创建权威记录。
11. 人工阻塞可被普通恢复事件跳过：暂停链存在 owner_intervention_required 时，恢复/终止必须提供 owner_resolution_reference；后续 warning 或飞书 resolved 均不能取消该条件。
12. 字段“存在”不等于合法：时间字段拒绝 null/非 ISO 值；一级 assistant-scope 身份必须匹配提交者。

## 关键兼容与安全边界

- V1/alpha 的自由格式日志保留只读，validator 提示 legacy，不将其当作 canonical 状态或授权。旧项目需人工确认迁移，不能凭老文件名伪造新审核。
- 旧 JSON manifest.yaml 优先级低于 manifest.json；兼容文件名不放宽任务、审核和 hash 检查。无法证明来源的旧实验产物不会被静默批准。
- 冻结计划不可覆盖、不可追加修改其权限字段。实质变化使用经授权的新计划/新 identity 和 supersedes_reference；旧任务的取消仍需单独合法事件。
- 原始提交与已接受审核的完整 file/dir 是发布单位，不支持从已审核目录隐式切片。不同发布范围须重新提交审核。
- 只读验证允许已接受 delivery 原工作区清理；长期批准、错误和阶段验收证据仍应保存，不应指向随手删除的临时文件。
- 所有通知凭证退出项目 JSON。旧含凭证配置会被拒绝且提示环境变量迁移；适配器不使用、打印或持久化其中的凭证。负责人自行迁移真实配置。
- 既有项目的初始化仅补缺失，不自动覆盖旧版本工具。检测到保留的旧飞书 adapter 时不自动执行，要求迁移审查。
- 单机文件锁避免并发工具互相覆盖；异常退出遗留锁须确认没有活动写者后人工清理。没有新增分布式调度器。
- hash 链用于结构完整性/意外篡改检测，不是签名系统。拥有文件系统写权限的人仍可重写整套历史；Skill 不是操作系统 ACL。引擎不能替代对真实人类批准和技术正确性的审核。

## 实际验证

环境：Windows / Python 3.14；治理工具和 unittest 无第三方运行时依赖。

```text
python -B -m unittest discover -s tests -v
Ran 113 tests
OK (skipped=3)
```

- 110 PASS，0 FAIL，3 SKIP（2026-09-07 提交前复验 53.340 秒；前次完整运行 36.295 秒）。
- 3 项 SKIP 为本机 Windows 未授予创建真实 symlink 权限（WinError 1314）：artifact 源链接、嵌套链接、通知目录逃逸用例。
- 对应的无特权 symlink guard 模拟测试通过；路径穿越、外部源、版本不可覆盖测试通过。不能将 3 项 SKIP 宣称为真实链接实测通过。
- 11 种记录类型 × 2 套语言模板共 22 个事件示例均实际经 Engine 写入、Validator 回读通过（包含在 schema consistency 测试）。
- E2E 使用初始化复制到项目 root/ 的真实 CLI：PASS；非法 running→accepted 返回退出码 2 和 REJECTED。
- 飞书请求全部 mock，没有读取真实配置、没有真实通知发送；HMAC 固定向量及业务失败/成功、去重、恢复测试通过。
- `git -c core.safecrlf=false diff --check`：PASS。
- 系统 skill-creator 的 `quick_validate.py`：`Skill is valid!`。系统 Python 起初缺 PyYAML；仅在系统临时目录安装 PyYAML 6.0.3 并通过临时 PYTHONPATH 运行校验，没有为治理项目增加依赖。

飞书签名规范参考：[飞书自定义机器人指南](https://open.feishu.cn/document/client-docs/bot-v3/add-custom-bot)。

## 修改文件分类

### governance

- SKILL.md
- assets/templates/AGENTS.md
- assets/templates/rules/{00-core-governance,01-role-and-filesystem,02-work-log-governance}.md
- references/{dispatch-and-audit,four-quadrant-alignment,level1-plan-record,level2-plan-record,project-layout,remaining-work-record-types,roles-and-authority,startup-protocol,v2-governance,work-log-governance}.md

### engine

- scripts/{governance_schema,record_engine,validate_project_governance,initialize_project}.py
- assets/templates/root/templates/GOVERNANCE_EVENT.json
- assets/templates/root/templates/INTERFACE_CONTRACT.json（替换 .yaml）
- assets/templates/root/templates/LEVEL1_{PLAN,SUMMARY,RESULTS,WARNING,ERROR}{,_CN}.md
- assets/templates/root/templates/LEVEL2_{PLAN,RESULTS_MID,FINAL_RESULT,SUMMARY,WARNING,ERROR}{,_CN}.md
- assets/templates/root/templates/{TASK_PACKAGE,TASK_PACKAGE_CN,WORK_LOG,ASSISTANT_00_STARTUP}.md

### artifact

- scripts/{artifact_support,publish_artifact}.py
- assets/templates/root/templates/ARTIFACT_MANIFEST.json（替换 .yaml）

### notification

- scripts/notifications/feishu.py
- assets/templates/root/notifications/feishu_config_example.json

### tests

- tests/__init__.py、tests/helpers.py
- tests/test_initialize_project.py
- tests/test_artifact_publish.py
- tests/test_record_engine.py
- tests/test_record_schema_consistency.py
- tests/test_task_dag.py
- tests/test_identifier_alias.py
- tests/test_v1_compatibility.py
- tests/test_feishu.py
- tests/test_end_to_end.py
- tests/test_review_regressions.py

### docs

- README.md
- assets/templates/root/README.md
- docs/V2_HARDENING_NOTES.md

## 剩余问题与验收状态

- 当前覆盖范围内没有已知未修复的阻断缺陷；真实 symlink 的 3 项平台实测仍需在允许该操作的环境补跑。
- 本轮按要求不发送真实飞书通知，真实线路连通性由负责人配置环境变量后另行验收。
- 既有项目数据/工具迁移未自动执行；不会以“升级”名义改写历史。
- 本轮没有新增禁止项；V3_CANDIDATES 仅保留未来有独立授权时再评估的签名/OS 权限隔离或更复杂检索，不实现。
- Merge readiness：`READY_FOR_OWNER_REVIEW`。这是负责人审核入口，不是批准 merge，也不是“已合并完成”。
