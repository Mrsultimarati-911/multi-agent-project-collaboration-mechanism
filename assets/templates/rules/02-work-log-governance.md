# Work-log governance

`record` is the sole semantic `work_logs/` writer. Logs record auditable events only. Use level 1 for project stages/assistant initiatives and level 2 for employee tasks. Keep `level2_results_mid` append-only; create a final level 2 result only after assistant audit.

V2 engine and validator share `root/governance_schema.py`. Record submits JSON; the engine reads authoritative history, validates task code, type fields, references, dependency readiness and transitions, then generates Markdown metadata and narrative. `record_status` is recorded/final, `plan_status` is frozen for plans, `execution_status` is the task/stage lifecycle; generic `status` is not a V2 field. Historical task identity is immutable. Level 1 is owner-approved; Level 2 is owner-approved or envelope-authorized. Feishu requires owner intervention except the enabled startup connectivity check; credentials are environment-only and business success must be verified. Feishu never grants approval.
