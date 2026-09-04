# Multi Agent Project Collaboration Mechanism

An explicit-only Codex Skill for human-led, auditable multi-agent projects.

It separates decision-making, planning, execution, governance, and durable records into five roles:

- human project owner: approvals, decisions, exceptions, and final acceptance;
- monitor: the default first project conversation; checks the layout, obtains authorization before creating missing paths, and maintains owner-confirmed rules;
- assistant: plans, dispatches approved work, and audits deliveries;
- employee: performs one bounded task in an isolated workspace and requests assistant audit when complete;
- record: validates and writes auditable work logs only.

The Skill provides a standard project layout (including `raw_data/`), `AGENTS.md` and rule templates, two-level work-log conventions, bounded task-package templates, and optional initialization and read-only validation scripts. Monitor requests an owner-defined global task identifier (for example `QSV5` or `TLTK`) during initialization; it is used in every task code and may later be changed only through an owner-authorized monitor-to-record migration plus assistant notification. The default employee configuration is GPT-5.6 Luna with high reasoning; the default record configuration is GPT-5.6 Luna with medium reasoning. Defaults may be amended only by the owner through `monitor`.

## Use

Install the Skill into your Codex skills directory, then explicitly invoke:

```text
$multi-agent-project-collaboration-mechanism
```

or tell Codex that a project is enabling this mechanism. The Skill deliberately does not activate implicitly.

For long-lived project facts, requirements, and architecture context, use it alongside a project-context system such as `my-context-manage`.

## License

[MIT](LICENSE)
