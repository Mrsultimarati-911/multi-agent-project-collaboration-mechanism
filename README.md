# Multi Agent Project Collaboration Mechanism

An explicit-only Codex Skill for human-led, auditable multi-agent projects.

It separates decision-making, planning, execution, governance, and durable records into five roles:

- human project owner: approvals, decisions, exceptions, and final acceptance;
- monitor: initializes and maintains owner-confirmed project rules;
- assistant: plans, dispatches approved work, and audits deliveries;
- employee: performs one bounded task in an isolated workspace;
- record: validates and writes auditable work logs only.

The Skill provides a standard project layout, `AGENTS.md` and rule templates, two-level work-log conventions, bounded task-package templates, and optional initialization and read-only validation scripts.

## Use

Install the Skill into your Codex skills directory, then explicitly invoke:

```text
$multi-agent-project-collaboration-mechanism
```

or tell Codex that a project is enabling this mechanism. The Skill deliberately does not activate implicitly.

For long-lived project facts, requirements, and architecture context, use it alongside a project-context system such as `my-context-manage`.

## License

[MIT](LICENSE)
