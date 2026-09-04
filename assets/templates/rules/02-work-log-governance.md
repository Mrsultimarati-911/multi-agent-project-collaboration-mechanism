# Work-log governance

`record` is the sole semantic `work_logs/` writer. Logs record auditable events only. Use level 1 for project stages/assistant initiatives and level 2 for employee tasks. Keep `level2_results_mid` append-only; create a final level 2 result only after assistant audit.

V2 uses `root/record_engine.py` for task-code, required-field, reference, dependency and state-transition legality. Record prepares the human-readable event; the engine accepts or rejects the authoritative append. Historical task identity is immutable. A V2 owner escalation must set `owner_intervention_required: true`; only the notification adapter may send Feishu, and Feishu is never an approval channel.
