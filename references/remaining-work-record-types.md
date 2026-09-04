# Remaining work-record types

## Execution and finalization

- `level2_results_mid`: record creates it on the employee's first auditable delivery after assistant submission. Each later delivery, audit verdict, correction request, and rework is appended as a new attempt. Never overwrite an attempt.
- `level2_results`: record creates it only when an assistant accepts the scoped delivery in its mid record. It cites the accepted attempt and contains final deliverables, validation evidence, scope, and limitations.
- `level2_summary`: only the responsible employee submits it directly to record after final acceptance. It cites the final result and audit. Record remains the sole `work_logs/` writer.

## Exceptions

- `level2_warning`: assistant records an interruption with a viable recovery path. It affects only that employee task unless a separate level-1 event exists.
- `level2_error`: assistant records a task blockage requiring owner intervention. It pauses only that employee task. It may be created directly when the need for owner action is already established.
- `level1_warning`: a participating assistant records a recoverable interruption affecting a stage-wide scope.
- `level1_error`: a participating assistant records a stage blockage requiring an owner decision. It lists every paused employee and pauses the level-1 task.

Warnings and errors are immutable evidence. Later recovery links to them; it never deletes, renames, or downgrades them. Warning-to-error escalation creates a new error linked to the warning.

## Stage close

- `level1_summary`: each participating assistant records its own assistant-scoped completion account after the stage is complete. Use code `<project>_<level1>-<assistant>-###-####`.
- `level1_results`: record creates the aggregate stage result only after owner acceptance, from the level-1 summaries and accepted level-2 results. Use aggregate code `<project>_<level1>-##-###-####`. Record condenses supplied facts; it does not invent a technical conclusion.
