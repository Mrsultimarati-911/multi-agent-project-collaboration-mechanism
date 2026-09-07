# Project layout

The mechanism creates these project-level paths. Add domain folders freely; do not place collaboration utilities in the project root.

```text
AGENTS.md
root/                         # mechanism tools and templates used by this project
rules/                        # owner-confirmed project rules
ai_workspace/                 # employee-isolated task workspaces
work_logs/                    # record-role-only audit records
common_data/                  # versioned audited data with manifest.json
common_artifacts/             # versioned audited code/doc/model artifacts
assistant_workspace/          # module assistant's isolated integration workspace
draft/                        # non-final analysis and proposals
plan/                         # owner-confirmed or pending project plans
plan/interfaces/              # versioned material interface contracts (JSON)
project_demo/                 # authorized integration/testing staging
project_final/                # owner-authorized final deliverables
raw_data/                     # source inputs; never silently overwrite
```

## `root/`

`root/` contains `governance_schema.py`, `record_engine.py`, `publish_artifact.py`, `validate_project_governance.py`, `notifications/feishu.py` and templates. It contains no business deliveries or secrets. `notifications/feishu_config_example.json` and optional `feishu_config.json` contain only an `enabled` boolean; actual credentials are environment-only. Notification runtime state is local and ignored. Startup may append fixed missing `.gitignore` rules idempotently; it never removes or rewrites existing rules.

## Read/write routing

- `monitor`: may write `AGENTS.md` and `rules/` from owner-approved instructions only.
- `record`: may write only `work_logs/`.
- `employee`: may write only its own `ai_workspace/<task-name>/`.
- `assistant`: module integration is limited to its declared `assistant_workspace/<assistant-id>/`; shared publication and permitted integration use the owner-approved envelope or explicit approval.
- `project_demo/`: only the coordinating assistant integrates under explicit approval or its matching envelope. `project_final/`: always explicit owner approval.
- `raw_data/`: source inputs. No agent silently overwrites it; project-specific rules define any authorized write path.

The project may make this stricter in `rules/`. Paths in task packages must be relative to the project root wherever possible.
