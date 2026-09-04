# 多智能体项目协作机制

> **人类负责决策，Agent 分级协作，所有关键过程可追溯。**
>
> 一个仅可显式调用的 Codex Skill，用于由人类负责人主导、全程可审计的多智能体项目。

| 调用方式 | 核心角色 | 默认工作语言 | 适用范围 |
| --- | --- | --- | --- |
| 显式调用 | monitor / assistant / employee / record | 中文 `zh-CN` | 任意需要多 Agent 分工与可追溯记录的项目 |

**快速导航：** [启用方式](#使用方式) · [项目启动](#项目启动) · [目录结构](#启用后的目录结构) · [角色权责](#角色权责) · [数据流](#数据流事实与工件如何流动) · [流程流](#流程流从讨论到验收) · [情景演绎](#情景演绎三个并行任务返工与权限阻塞)

---

## V2：受控共享与边界内自治

V2 在 V1 的“人类最终决策、隔离 workspace、两级计划、append-only 记录”之上，增加以下能力：

| V2 能力 | 解决的问题 | 默认边界 |
| --- | --- | --- |
| `common_data/` / `common_artifacts/` | 多 Agent 复用已审核中间产物 | 仅经 audit + 版本化 publish；employee 不可直接写 |
| `assistant_workspace/` 与 Stage DAG | 多 assistant 分模块并行 | coordinator 管跨模块与 `project_demo/`；模块 assistant 只写自身空间 |
| Authority Envelope | 避免负责人逐项审批低风险返工与派发 | Level 1 由负责人预先明确边界；R3 永远人工批准 |
| Record Engine | 将字段、状态、引用、依赖校验变为确定性程序 | record 仍负责可读叙述，不单独裁定合法性 |
| Feishu escalation | 真正需人工决定时主动提醒 | 仅 `owner_intervention_required: true`；飞书不是审批入口 |

> [!IMPORTANT]
> V2 位于独立 `v2` 分支，V1 `main` 不被改写。已有 V1 项目可以安全运行初始化器补齐目录；历史工作记录和任务身份保持可读且不可重写。

共享工件的唯一正式路径是：`employee workspace → assistant audit → publish_artifact.py → immutable common_data/common_artifacts version + manifest`。每一个已发布版本均包含生产任务、审核引用、来源和 SHA-256 内容散列；下游任务必须引用具体版本。

---

它将决策、规划、执行、治理和可追溯记录分为五类角色：

- 人类项目负责人：审批、决策、例外处理与最终验收；
- `monitor`：默认的项目首个对话；检查目录结构、创建缺失的标准路径，并维护负责人确认的规则；
- `assistant`：规划、派发已批准工作，并审核交付；
- `employee`：在隔离工作区完成一个边界明确的任务，结束后请求 assistant 审核；
- `record`：仅负责校验和写入可审计的工作记录。

Skill 提供标准项目目录（含 `raw_data/`）、`AGENTS.md` 与规则模板、两级工作记录约定、边界明确的任务包模板，以及可选的初始化和只读校验脚本。`monitor` 会直接创建缺失的标准路径，随后向负责人索取经确认的全局任务标识（例如 `QSV5` 或 `TLTK`）、可选的角色默认配置、工作语言和项目特色规则。它可以提出任务标识建议，但绝不自行设定。初始化后，它会创建 `record|工作记录` 和 `assistant_00`，分别用于受控记录与项目初始熟悉。employee 仅可将其经 assistant 审核通过的 `level2_summary` 直接提交给 record；`record` 始终是 `work_logs/` 的唯一写入者。默认智能水平为：assistant 使用 GPT-5.6 Terra/high，employee 使用 GPT-5.6 Luna/high，record 使用 GPT-5.6 Luna/medium；只有负责人可通过 `monitor` 修改这些默认值。

每次 assistant 准备制定计划、形成行动决策或派发 employee 前，Skill 会自动应用四象限需求对齐：已确认的共同信息、负责人已知但 agent 未知的关键缺口、agent 可补充的知识/风险/替代方案，以及双方共同未知且应转化为可验证假设的问题。信息充分时不会重复提问，关键对齐问题最多十个。

每个获批准的阶段，在任何 employee 派发之前都必须先建立冻结的 `level1_plan` 契约。它记录授权证据、范围、验收、对齐、委派、验证和升级机制；后续获得负责人批准的实质变更会追加到变更台账，而不是悄然重写历史。

每个被派发的 employee 还必须拥有冻结的、关联 level1 计划的具体 `level2_plan`，随后再获得可执行的任务包。实质修订仅能在负责人批准后追加；目标或交付物发生变化时，必须创建新的任务码。

Skill 提供专用模板，用于追加式的 employee 审核尝试记录、最终结果、摘要、警告/错误恢复与暂停记录、assistant 阶段摘要，以及由 record 生成的阶段结果。

初始化时，`monitor` 还会询问可选的项目工作语言，默认中文（`zh-CN`）。中文项目使用随 Skill 提供的 `_CN` 记录模板，所有叙述性文本均为中文；用于校验的稳定元数据键名保持统一。

## 使用方式

将 Skill 安装到 Codex skills 目录后，显式调用：

```text
$multi-agent-project-collaboration-mechanism
```

或直接告诉 Codex：项目要启用该协作机制。Skill 不会隐式自动启用。

对于项目长期事实、需求与架构上下文，建议与 `my-context-manage` 等项目上下文系统配合使用。

> [!TIP]
> 本 Skill 管理多 Agent 的执行、审核与记录流；`my-context-manage` 管理长期项目事实与会话收口。二者均不替代 Git 的版本历史或文件系统的硬权限控制。

---

## 项目启动

负责人第一次在项目中启用 Skill 后，该对话即作为 `monitor`。monitor 先检查项目根目录并直接创建缺失的标准机制路径，绝不覆盖已有文件；然后一次性向负责人请求以下配置：

1. 项目标识（**必填**）：例如 `QSV5`、`TLTK`。monitor 可以给出建议，但只能由负责人确认，不能自行使用任何默认标识。
2. record 的默认模型与推理强度（可选）：省略时为 GPT-5.6 Luna / medium。
3. assistant 的默认模型与推理强度（可选）：省略时为 GPT-5.6 Terra / high。
4. employee 的默认模型与推理强度（可选）：省略时为 GPT-5.6 Luna / high。
5. 项目特色规则（可选）：省略即当前没有额外规则。
6. 工作语言（可选）：省略时为中文 `zh-CN`。

项目标识被负责人明确确认前，不创建启动 Agent。初始化配置写入 `rules/00-core-governance.md`。中文项目必须选择 `_CN` 记录模板，记录标题、叙述、证据解释、限制与下一步均使用中文；`record_type`、`task_code`、`status` 等稳定元数据键仍保留英文，保证统一校验。

配置完成后，monitor 创建且只创建两个启动对话：

- `record|工作记录`：唯一能写入 `work_logs/` 的角色；
- `assistant_00|<初始范围>`：阅读项目已有资料后向负责人提出一至十个关键需求对齐问题。

> [!IMPORTANT]
> 在项目标识由负责人明确确认前，monitor 不得创建启动 Agent，也不得以 `A` 或其他占位标识替代。

---

## 启用后的目录结构

```text
<项目根目录>/
├── AGENTS.md                         # 全部 Agent 的路由、角色和文件权限
├── rules/                            # 负责人确认后的治理规则
│   ├── 00-core-governance.md          # 项目标识、模型默认值、语言、特色规则
│   ├── 01-role-and-filesystem.md      # 角色职责和路径边界
│   └── 02-work-log-governance.md      # 记录类型、状态机、提交路径
├── root/                             # 机制工具；不是业务源码或交付目录
│   ├── README.md                     # 本目录的中文说明
│   ├── validate_project_governance.py # 只读结构及记录校验器
│   └── templates/                    # 所有计划、任务包、记录模板及 *_CN.md
├── plan/                             # 计划草案；不等同于正式批准记录
├── draft/                            # 临时材料；不等同于项目事实
├── ai_workspace/                     # employee 的隔离工作区
│   └── <任务名>/
├── work_logs/                        # 权威事件记录；只有 record 可写
├── raw_data/                         # 原始输入数据
├── project_demo/                     # 演示性输出
└── project_final/                    # 获负责人授权后的正式交付物
```

employee 默认只能在自己的 `ai_workspace/<任务名>/` 中写入。任何将工作结果提升至源码、`project_demo/`、`project_final/` 或其他正式位置的操作，都需要负责人单独授权。`work_logs/` 不是对话备份，而是对关键事件、证据和状态的权威审计层。

> [!NOTE]
> `plan/` 与 `draft/` 可以承载探索和讨论；只有 record 写入的 `work_logs/` 才承载工作流中的权威事件记录。

---

## 角色权责

| 角色 | 可做什么 | 明确禁止 |
| --- | --- | --- |
| 人类负责人 | 确认规则、范围、计划、派发、例外、整合及最终验收 | 无工作流限制 |
| `monitor` | 初始化目录，记录负责人确认的治理配置，创建 record 与 `assistant_00`，传达负责人批准的任务标识变更 | 规划技术工作、改业务代码、派发 employee、审核、写 `work_logs/` |
| `assistant_NN` | 对齐需求，提出计划，获批后派发 employee，审核交付，向 record 提交记录事件 | 未经负责人批准派发；默认直接修改正式项目内容 |
| `employee_NN` | 完成一个受限任务，提供工件和验证证据，向创建自己的 assistant 请求审核 | 写规则、`AGENTS.md`、`work_logs/`、其他 workspace；自行验收或整合 |
| `record` | 校验记录字段、任务码、引用和审核状态，写入 `work_logs/` | 推断事实、改技术结论、规划、派发、写代码、联系 monitor |

负责人可在对话中用 `a00` 指代 `assistant_00`、用 `e00` 指代 `employee_00`。所有 Agent 必须识别这种简称，但在 Agent 间沟通、回复负责人、任务包、文件名和记录中只能使用完整正式名称。

---

## 任务码、计划与工作包

employee 任务码为：

```text
<项目标识>_<一级任务>-<assistant>-<employee>-<employee任务序号>
QSV5_02-04-014-0008
```

四个数字段依次为一级任务（2 位）、assistant（2 位）、employee（3 位）、employee 任务（4 位），均从零开始。一级聚合记录允许将下游未知段记为 `#`，如 `QSV5_02-##-###-####`；二级记录必须使用完整数字任务码。

| 层级 | 权威记录 | 创建时机 | 冻结内容 |
| --- | --- | --- | --- |
| Level 1 | `level1_plan_<aggregate-code>.md` | 负责人明确批准阶段计划后，任何 employee 创建/派发前 | 阶段目标、范围与非目标、验收、计划委派、风险、验证和升级机制 |
| Level 2 | `level2_plan_<task-code>.md` | 负责人明确批准向某 employee 派发后，employee 对话创建前 | 一个具体任务的输入、可读写范围、工作区、交付物、审核证据和中断处理 |

同一任务的实质变更需要负责人批准，由 record 追加到计划的 amendment ledger；不得悄然改写冻结基线。目标或交付物变更时，应分配新 employee 任务序号、创建新任务码与新的 `level2_plan`。

`TASK_PACKAGE.md` 是从已批准的 level2 计划派生出的操作指令，必须包含任务目标、必读上下文、允许范围、非目标、不可更改的确认决策、验收与验证命令、交付格式、升级条件，以及“完成后必须请求 assistant 审核”的要求。

---

## 数据流：事实与工件如何流动

数据流传递事实、工件、证据与审计结论；它不能绕过角色权限。

```mermaid
flowchart TD
    H[人类负责人] -->|需求、批准、例外、验收| M[monitor]
    M -->|初始化配置、项目标识| R[record]
    M -->|启动指令：阅读项目资料并需求对齐| A[assistant_*]
    H -->|需求问答、计划和派发批准| A
    A -->|已批准计划、审核事件| R
    A -->|任务包：边界、输入、验收、验证| E[employee_*]
    E -->|工作区交付、证据、审核请求| A
    A -->|通过 / 返工 / 升级决定| E
    E -->|仅限已审核的 level2_summary| R
    R -->|权威记录及引用| A
    A -->|阶段结果和验收建议| H
```

对应规则：

- 负责人可直接和 monitor、assistant 对话；monitor 不接收其他 Agent 的指令。
- employee 的日常上级只有其创建 assistant；employee 的每次完成都要带证据请求审核。
- 除 `level2_summary` 外，employee 不能直接向 record 提交记录；计划、中间结果、最终结果、warning/error 均由 assistant 提交。
- employee 直接提交 `level2_summary` 的前提是 assistant 已接受其任务范围内交付，且摘要引用该审核和 `level2_results`。
- record 只在核对任务码、必填字段、引用和审核状态后写入权威副本。

> [!CAUTION]
> 数据可以被读取，不意味着拥有改写或批准权限。任何数据流都不能绕过计划冻结、assistant 审核或人类负责人审批。

---

## 流程流：从讨论到验收

流程流描述任务如何由“讨论”变成“经批准的行动”，再变成“可验收的结果”。

```mermaid
flowchart LR
    S[负责人显式启用] --> M[monitor 初始化目录和配置]
    M --> B[创建 record 与 assistant_00]
    B --> Q[assistant 需求对齐]
    Q --> P[负责人批准 level1_plan]
    P --> L1[record 写入冻结一级计划]
    L1 --> D[负责人批准具体 level2_plan 与派发]
    D --> E[assistant 创建 employee 并交付任务包]
    E --> W[employee 在隔离 workspace 执行]
    W --> A[assistant 审核]
    A -->|通过| F[record 写结果；employee 提交摘要]
    A -->|返工| W
    A -->|升级级阻塞| X[写 warning/error 并暂停相应范围]
    X --> H[负责人提供权限或决定]
    H --> W
    F --> C[assistant 汇总一级阶段]
    C --> Z[负责人最终验收或规划下一阶段]
```

assistant 形成计划、行动决策或准备派发前，自动执行四象限对齐：

1. 共同已知：确认目标、背景、交付标准和边界；充分时不重复询问。
2. 负责人已知、Agent 未知：仅当信息缺失会实质改变结果时提问，最多十个；否则明确合理假设并先做探索。
3. 负责人未知、Agent 已知：主动补充方法、风险、替代方案和取舍；必要时指出前提错误。
4. 共同未知：转化为可验证假设，必要时提出最小实验、单一变量、成败信号与所需数据。

employee 被派发后，assistant 默认不频繁打断工作；预期超过十分钟的任务须给出估时，assistant 至多每十分钟检查一次，且默认最多主动管理五个 employee。

---

## 记录生命周期

一个二级任务的正常记录链：

```text
level1_plan
  → level2_plan
  → level2_results_mid（可重复追加的交付/审核尝试）
  → assistant 接受审核
  → level2_results
  → level2_summary
  → level1_summary / level1_results
```

`level2_results_mid` 是追加式审核历史：每次提交、拒绝、返工和新证据都要保留。只有 assistant 明确接受当前范围内交付后，record 才创建 `level2_results`；之后 employee 才可以提交自己的 `level2_summary`。

异常记录同样只追加：

- `level2_warning`：某一个 employee 任务可恢复的中断，说明恢复负责人、计划与条件；
- `level2_error`：某任务需要负责人提供权限或作出决定，该 employee 暂停；
- `level1_warning`：一级阶段的可恢复风险；
- `level1_error`：一级阶段严重错误，阶段内全部 employee 暂停至负责人决定。

warning 升级为 error 时，warning 不删除，另建关联的 error。所有修复、恢复或结论都作为新的记录或追加条目存在。

> [!IMPORTANT]
> “追加”是本机制的审计底线：不能用覆盖、重命名或删除来掩盖一次失败、阻塞或旧决策。

---

## 情景演绎：三个并行任务、返工与权限阻塞

以下以项目标识 `XXXX` 和第一个一级任务为例，完整演绎协作及记录如何变化。

<details open>
<summary><strong>阶段 A｜启动、需求对齐与计划冻结</strong></summary>

1. 负责人在项目根目录启用 Skill；首个对话成为 monitor。monitor 补齐结构，负责人确认 `XXXX` 及可选配置。
2. monitor 创建 `record|工作记录` 与 `assistant_00`。assistant 阅读已有参考文件、数据、规则、计划和草稿，并经若干轮对话完成需求对齐。
3. `assistant_00` 提出首个 Level 1 计划。负责人批准后，record 写入 `level1_plan_XXXX_00-##-###-####.md`。此前不会有 employee 或二级计划。
4. assistant 为三个执行单元分别提出派发。负责人逐项批准后，record 写入：

```text
level2_plan_XXXX_00-00-000-0000.md
level2_plan_XXXX_00-00-001-0000.md
level2_plan_XXXX_00-00-002-0000.md
```

5. 仅在各自 level2 计划落盘后，assistant 才创建三个 employee，并向其发送相应任务包。三个 employee 只在各自 `ai_workspace/` 下写入。

</details>

<details>
<summary><strong>阶段 B｜employee_00：两次返工后通过审核</strong></summary>

1. `employee_00` 首次交付并请求 `assistant_00` 审核。审核不通过：assistant 向 record 提交第一次 `level2_results_mid_XXXX_00-00-000-0000.md` 尝试，并要求限定范围内返工。
2. 第二次交付仍不通过，record 在同一中间结果记录追加第二次审核尝试；首次证据与失败原因完整保留。
3. 第三次交付通过。assistant 提交接受证据，record 创建 `level2_results_XXXX_00-00-000-0000.md`。employee 随后可把引用审核与最终结果的 `level2_summary_XXXX_00-00-000-0000.md` 直接提交给 record。

</details>

<details>
<summary><strong>阶段 C｜employee_01：修正命令后恢复</strong></summary>

1. `employee_01` 执行遇到中断。assistant 判断仅需修正任务包内的执行命令，不需负责人作新决定，于是向 record 提交 `level2_warning_XXXX_00-00-001-0000.md`，记录中断、恢复计划与恢复条件。
2. assistant 修正指令边界后，employee 恢复执行并正常通过审核。record 继续写入该任务的中间审核、最终结果与摘要。warning 保留并链接最终结果，形成可追溯恢复链。

</details>

<details>
<summary><strong>阶段 D｜employee_02：人工权限介入后恢复</strong></summary>

1. `employee_02` 也遇到中断；assistant 判断必须由负责人手动提供某权限，不能自行越权处理，于是提交 `level2_error_XXXX_00-00-002-0000.md`，注明直接证据、暂停范围和所需负责人动作。
2. 此时暂停的仅是 `employee_02`；`employee_00` 与 `employee_01` 不因 Level 2 error 自动停止。
3. 负责人提供权限或明确授权。assistant 将授权与恢复条件提交 record，employee 继续执行并最终通过审核；record 写入该任务的中间结果、最终结果和摘要。error 不删除，完整保留“阻塞—人工处理—恢复—完成”链。

</details>

<details>
<summary><strong>阶段 E｜一级汇总与负责人验收</strong></summary>

三个二级任务均完成后，assistant 汇总交付、验证、遗留限制和风险，提交 `level1_summary_XXXX_00-00-###-####.md`。record 基于二级结果和负责人验收材料写入 `level1_results_XXXX_00-##-###-####.md`。assistant 向负责人请求验收；负责人确认后，一级任务才真正结束，并可规划下一阶段。

若发生的是 Level 1 error 而非某个 employee 的二级错误，则 record 记录 `level1_error_XXXX_00-00-###-####.md`，并暂停该一级阶段的全部 employee，直到负责人决定恢复、调整或终止。

</details>

---

## 模板与校验边界

`root/templates/` 包含 `LEVEL1_PLAN[_CN].md`、`LEVEL2_PLAN[_CN].md`、`TASK_PACKAGE.md`、各类 `RESULTS`、`SUMMARY`、`WARNING`、`ERROR` 模板。中文项目优先使用所有 `_CN` 版本。

`root/validate_project_governance.py` 是只读校验器，可检查目录、规则文件、任务码、记录字段和引用关系。它无法替代 assistant 对真实工件的技术审核，也不能证明没有独立证据支撑的结论。

## 许可证

[MIT](LICENSE)
