# Remaining work-record types

## Execution and finalization

- `level2_results_mid`: records dispatched/running/submitted/audited and later permitted execution events submitted through the assistant. Each transition is a separate engine event. Deliveries and audits share an attempt number; rework increases it. Audit status is `not_requested`, `pending`, `accepted` or `rejected`; only an `audited` event may accept delivery. Never overwrite earlier events.
- `level2_results`: record creates it only when an assistant accepts the scoped delivery in its mid record. It cites the accepted attempt and contains final deliverables, validation evidence, scope, and limitations.
- `level2_summary`: only the responsible employee may use the direct employee-to-record route, after scoped assistant acceptance and the final result. It cites that result's same audit; stage owner acceptance is a separate later gate. Record remains the sole `work_logs/` writer and invokes the engine.

## Exceptions

- `level2_warning`: assistant records an interruption with a viable recovery path. It affects only that employee task unless a separate level-1 event exists.
- `level2_error`: assistant records a task blockage requiring owner intervention. It pauses only that employee task. It may be created directly when the need for owner action is already established.
- `level1_warning`: a participating assistant records a recoverable interruption affecting a stage-wide scope.
- `level1_error`: a participating assistant records a stage blockage requiring an owner decision. It lists every paused employee and pauses the level-1 task.

Warnings and errors are immutable evidence. Later recovery links to them; it never deletes, renames, or downgrades them. Warning-to-error escalation creates a new error linked to the warning.

## Stage close

- `level1_summary`: a participating assistant records scoped stage activation, progress or completion evidence using `<project>_<level1>-<assistant>-###-####`. It may report an already accepted stage but cannot establish initial owner acceptance; that transition requires `level1_results` with owner evidence.
- `level1_results`: record creates the aggregate stage result only after owner acceptance, from the level-1 summaries and accepted level-2 results. Use aggregate code `<project>_<level1>-##-###-####`. Record condenses supplied facts; it does not invent a technical conclusion.

Every template supplies a JSON event, not front matter to copy into a log. The shared canonical schema defines its required fields and allowed states; the engine supplies timestamps, record finality and hash-chain metadata. Type names, task-code shape, actual history, accepted audit links and dependency readiness are validated together.
