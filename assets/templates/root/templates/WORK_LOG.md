# Work-record template routing

Select a dedicated record template; arbitrary record types are not allowed.

| Record type | Template |
| --- | --- |
| level1_plan | LEVEL1_PLAN.md |
| level1_summary | LEVEL1_SUMMARY.md |
| level1_results | LEVEL1_RESULTS.md |
| level1_warning | LEVEL1_WARNING.md |
| level1_error | LEVEL1_ERROR.md |
| level2_plan | LEVEL2_PLAN.md |
| level2_results_mid | LEVEL2_RESULTS_MID.md |
| level2_results | LEVEL2_FINAL_RESULT.md |
| level2_summary | LEVEL2_SUMMARY.md |
| level2_warning | LEVEL2_WARNING.md |
| level2_error | LEVEL2_ERROR.md |

Chinese projects use the corresponding `_CN.md` template. Each contains a JSON event example and narrative outline. Record completes the event with actual facts and references, then calls `root/record_engine.py`. Do not author machine front matter or write raw templates into `work_logs/`; the engine generates and validates canonical metadata using `root/governance_schema.py`.
