# Multi Agent Project Collaboration Mechanism

An explicit-only Codex Skill for human-led, auditable multi-agent projects.

It separates decision-making, planning, execution, governance, and durable records into five roles:

- human project owner: approvals, decisions, exceptions, and final acceptance;
- monitor: the default first project conversation; checks the layout, obtains authorization before creating missing paths, and maintains owner-confirmed rules;
- assistant: plans, dispatches approved work, and audits deliveries;
- employee: performs one bounded task in an isolated workspace and requests assistant audit when complete;
- record: validates and writes auditable work logs only.

The Skill provides a standard project layout (including `raw_data/`), `AGENTS.md` and rule templates, two-level work-log conventions, bounded task-package templates, and optional initialization and read-only validation scripts. Monitor directly creates missing standard paths, then requests an owner-confirmed global task identifier (for example `QSV5` or `TLTK`), optional role defaults, and optional project-specific rules. It may propose but never self-assign the identifier. It then creates `assistant_00` for initial project familiarization and requirement alignment. The defaults are GPT-5.6 Terra/high for assistant, GPT-5.6 Luna/high for employee, and GPT-5.6 Luna/medium for record. Defaults may be amended only by the owner through `monitor`.

Before every assistant plan, action decision, or employee dispatch request, the Skill automatically applies a four-quadrant alignment review: confirmed shared context; material owner-context gaps; agent-supplied knowledge, risks, and alternatives; and jointly unknown items converted into testable assumptions. It asks no questions when context is sufficient and never asks more than ten material alignment questions.

## Use

Install the Skill into your Codex skills directory, then explicitly invoke:

```text
$multi-agent-project-collaboration-mechanism
```

or tell Codex that a project is enabling this mechanism. The Skill deliberately does not activate implicitly.

For long-lived project facts, requirements, and architecture context, use it alongside a project-context system such as `my-context-manage`.

## License

[MIT](LICENSE)
