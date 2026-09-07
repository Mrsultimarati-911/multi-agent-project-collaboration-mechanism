#!/usr/bin/env python3
"""Append canonical V2 events after replaying authoritative Markdown history."""
from __future__ import annotations
import argparse
import json
import os
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

from governance_schema import (
    EVENT_SEPARATOR, contained_path, current_state, event_digest, load_history,
    get_task_plan, ref_event, record_filename, replay_history, state_key, validate_event,
)

RESERVED = {'schema_version', 'event_id', 'sequence', 'created_at', 'event_date',
            'event_hash', 'previous_event_hash', 'actual_previous_status', 'record_status',
            'execution_status', 'employee_delivery_hash', 'submission_reference'}


@contextmanager
def project_lock(root: Path):
    path = contained_path(root, 'root/.record_engine.lock')
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        handle = path.open('x', encoding='utf-8')
    except FileExistsError as exc:
        raise ValueError('record engine is busy; retry after current writer finishes') from exc
    try:
        with handle:
            handle.write(str(os.getpid()))
        yield
    finally:
        path.unlink()


def prepare_event(root: Path, payload: dict, history: list[dict]) -> dict:
    if not isinstance(payload, dict) or any(key in payload for key in RESERVED) or any(key.startswith('_') for key in payload):
        raise ValueError('event payload contains reserved engine metadata')
    event = dict(payload)
    requested = event.pop('requested_status', None)
    if not requested:
        raise ValueError('requested_status is required')
    timestamp = datetime.now(timezone.utc).isoformat()
    record_filename(event)
    event.update(schema_version=2, event_id=uuid.uuid4().hex, sequence=len(history) + 1,
                 created_at=timestamp, event_date=timestamp[:10], record_status='final',
                 execution_status=requested, actual_previous_status=current_state(history, state_key(event)),
                 previous_event_hash=history[-1]['event_hash'] if history else None)
    for field in ('level1_plan_reference', 'authority_envelope_reference', 'level2_plan_reference',
                  'assistant_audit_reference', 'level2_results_mid_reference', 'level2_results_reference',
                  'supersedes_reference'):
        if field in event:
            referenced = ref_event(history, event[field])
            event[field] = referenced['_path'] + '#' + referenced['event_id']
    for field in ('source_level1_summaries', 'source_level2_results', 'exception_references'):
        if field in event:
            pinned = []
            for reference in event[field]:
                referenced = ref_event(history, reference)
                pinned.append(referenced['_path'] + '#' + referenced['event_id'])
            event[field] = pinned
    if event['record_type'].endswith('_plan'):
        event.setdefault('plan_status', 'frozen')
        event.setdefault('frozen_at', timestamp)
    if event['record_type'] == 'level2_results_mid':
        event.setdefault('submission_timestamp', timestamp)
    if event['record_type'] == 'level2_results':
        event.setdefault('final_completion_timestamp', timestamp)
    if event['record_type'].endswith(('_warning', '_error')):
        event.setdefault('interruption_detected_at', timestamp)
    if event['record_type'] == 'level2_results_mid' and (requested == 'submitted' or (requested == 'audited' and event.get('assistant_audit_status') == 'accepted')):
        from artifact_support import hash_artifact
        plan = get_task_plan(history, event['task_code'])
        delivery = contained_path(root, event.get('employee_delivery_reference', ''), True)
        if not delivery.is_relative_to(contained_path(root, plan['workspace'])):
            raise ValueError('delivery escapes task workspace')
        event['employee_delivery_hash'] = {'algorithm': 'sha256',
            'mode': 'file' if delivery.is_file() else 'tree-v1', 'value': hash_artifact(delivery)}
    if event['record_type'] == 'level2_results_mid' and requested == 'audited':
        submission = next((e for e in reversed(history) if e['record_type'] == 'level2_results_mid'
            and e['task_code'] == event['task_code'] and e['execution_status'] == 'submitted'), None)
        if submission is None:
            raise ValueError('audit requires a submitted delivery')
        event['submission_reference'] = submission['_path'] + '#' + submission['event_id']
    validate_event(root, event, history, live=True)
    if event['record_type'] == 'level2_results':
        from artifact_support import hash_artifact
        audit = ref_event(history, event['assistant_audit_reference'], 'level2_results_mid', event['task_code'])
        delivery = contained_path(root, audit['employee_delivery_reference'], True)
        if hash_artifact(delivery) != audit['employee_delivery_hash']['value']:
            raise ValueError('delivery changed after accepted audit')
    event['event_hash'] = event_digest(event)
    return event


def append_event(project_root: Path, payload: dict, *, dry_run=False) -> dict:
    root = Path(project_root).resolve()
    if not root.is_dir():
        raise ValueError('project root must exist')
    with project_lock(root):
        history, _ = load_history(root)
        replay_history(root, history)
        event = prepare_event(root, payload, history)
        relative = 'work_logs/' + record_filename(event)
        destination = contained_path(root, relative)
        if destination.exists() and not any(e['_path'] == relative for e in history):
            raise ValueError('legacy records are read-only; choose a new task identity')
        if event['record_type'].endswith('_plan') and destination.exists():
            raise ValueError('frozen plan cannot be overwritten or appended')
        if dry_run:
            return {**event, '_path': relative}
        destination.parent.mkdir(parents=True, exist_ok=True)
        # All validation is complete before opening the authoritative log.
        document = '---\n' + json.dumps(event, ensure_ascii=False, indent=2) + '\n---\n'
        document += f"\n# {event['record_type']}｜{event['task_name']}\n\n{event['event_description']}\n"
        with destination.open('a' if destination.exists() else 'x', encoding='utf-8', newline='\n') as handle:
            if handle.tell():
                handle.write(EVENT_SEPARATOR)
            handle.write(document)
            handle.flush()
            os.fsync(handle.fileno())
        return {**event, '_path': relative}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('project_root', type=Path)
    parser.add_argument('--event', type=Path, required=True, help='JSON payload, requested_status required')
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args(argv)
    try:
        root = args.project_root.resolve()
        supplied = args.event
        if supplied.is_absolute():
            supplied = supplied.resolve().relative_to(root)
        path = contained_path(root, supplied, True)
        payload = json.loads(path.read_text(encoding='utf-8-sig'))
        result = append_event(root, payload, dry_run=args.dry_run)
        print(('VALID ' if args.dry_run else 'RECORDED ') + result['_path'] + '#' + result['event_id'])
        return 0
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f'REJECTED: {exc}')
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
