# Multi Agent Project Collaboration Mechanism

An explicit-only Codex Skill for human-led, auditable multi-agent projects.

It separates decision-making, planning, execution, governance, and durable records into five roles:

- human project owner: approvals, decisions, exceptions, and final acceptance;
- monitor: the default first project conversation; checks the layout, obtains authorization before creating missing paths, and maintains owner-confirmed rules;
- assistant: plans, dispatches approved work, and audits deliveries;
- employee: performs one bounded task in an isolated workspace and requests assistant audit when complete;
- record: validates and writes auditable work logs only.

The Skill provides a standard project layout (including `raw_data/`), `AGENTS.md` and rule templates, two-level work-log conventions, bounded task-package templates, and optional initialization and read-only validation scripts. Monitor directly creates missing standard paths, then requests an owner-confirmed global task identifier (for example `QSV5` or `TLTK`), optional role defaults, and optional project-specific rules. It may propose but never self-assign the identifier. It then creates `record|工作记录` and `assistant_00` for governed logging and initial project familiarization. Employees may submit only their own assistant-audited `level2_summary` directly to record; record remains the sole `work_logs/` writer. The defaults are GPT-5.6 Terra/high for assistant, GPT-5.6 Luna/high for employee, and GPT-5.6 Luna/medium for record. Defaults may be amended only by the owner through `monitor`.

Before every assistant plan, action decision, or employee dispatch request, the Skill automatically applies a four-quadrant alignment review: confirmed shared context; material owner-context gaps; agent-supplied knowledge, risks, and alternatives; and jointly unknown items converted into testable assumptions. It asks no questions when context is sufficient and never asks more than ten material alignment questions.

Every approved stage begins with a frozen `level1_plan` contract before any employee dispatch. It captures authorization evidence, scope, acceptance, alignment, delegation, validation, and escalation; later material owner-approved changes are appended to its amendment ledger rather than silently rewriting history.

Every dispatched employee also has a frozen concrete `level2_plan`, linked to its level-1 plan and followed by an operational task package. Material revisions are appended only with owner approval; a changed objective or deliverable receives a new task code.

The Skill supplies dedicated templates for append-only employee audit attempts, final results, summaries, warning/error recovery and pause records, assistant stage summaries, and record-generated stage results.

Monitor also requests an optional project work language during initialization. It defaults to Chinese (`zh-CN`); Chinese projects use the supplied `_CN` record templates and Chinese narrative text, while stable metadata keys remain uniform for validation.

## Use

Install the Skill into your Codex skills directory, then explicitly invoke:

```text
$multi-agent-project-collaboration-mechanism
```

or tell Codex that a project is enabling this mechanism. The Skill deliberately does not activate implicitly.

For long-lived project facts, requirements, and architecture context, use it alongside a project-context system such as `my-context-manage`.

## License

[MIT](LICENSE)
