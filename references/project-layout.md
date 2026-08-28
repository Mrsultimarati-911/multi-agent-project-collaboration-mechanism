# Project layout

The mechanism creates these project-level paths. Add domain folders freely; do not place collaboration utilities in the project root.

```text
AGENTS.md
root/                         # mechanism tools and templates used by this project
rules/                        # owner-confirmed project rules
ai_workspace/                 # employee-isolated task workspaces
work_logs/                    # record-role-only audit records
draft/                        # non-final analysis and proposals
plan/                         # owner-confirmed or pending project plans
project_demo/                 # authorized integration/testing staging
project_final/                # owner-authorized final deliverables
```

## `root/`

`root/` contains mechanism tooling such as `validate_project_governance.py` and templates. It is not a place for business logic, production code, employee delivery, secrets, or arbitrary project output. The initializer copies the validator here so a project can validate its own records without relying on the installed Skill path.

## Read/write routing

- `monitor`: may write `AGENTS.md` and `rules/` from owner-approved instructions only.
- `record`: may write only `work_logs/`.
- `employee`: may write only its own `ai_workspace/<task-name>/`.
- `assistant`: default read-only; writes formal project material only with explicit owner authorization.
- `project_demo/` and `project_final/`: promotion targets only after owner authorization.

The project may make this stricter in `rules/`. Paths in task packages must be relative to the project root wherever possible.
