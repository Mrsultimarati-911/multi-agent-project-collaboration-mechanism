"""Canonical V2 records, safe paths, history parsing and governance validation.

The JSON front matter is a deliberately small YAML subset requiring no packages.
All consumers use this module; legacy text is readable but never grants authority.
"""
from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime
from pathlib import Path, PureWindowsPath

V1_DIRS = ('root', 'rules', 'ai_workspace', 'work_logs', 'draft', 'plan', 'project_demo', 'project_final', 'raw_data')
V2_DIRS = ('common_data', 'common_artifacts', 'assistant_workspace', 'plan/interfaces')
IDENTIFIER = r'[A-Za-z][A-Za-z0-9_]*'
TASK_CODE = re.compile(rf'^{IDENTIFIER}_\d{{2}}-\d{{2}}-\d{{3}}-\d{{4}}$')
AGGREGATE_CODE = re.compile(rf'^{IDENTIFIER}_\d{{2}}-##-###-####$')
ASSISTANT_CODE = re.compile(rf'^{IDENTIFIER}_\d{{2}}-\d{{2}}-###-####$')
ASSISTANT_ID = re.compile(r'^assistant_\d{2,}$')
RECORD_PATTERNS = {
    'level1_plan': AGGREGATE_CODE, 'level1_results': AGGREGATE_CODE,
    'level1_summary': ASSISTANT_CODE, 'level1_warning': ASSISTANT_CODE, 'level1_error': ASSISTANT_CODE,
    **{f'level2_{name}': TASK_CODE for name in ('plan', 'results_mid', 'results', 'summary', 'warning', 'error')},
}
REQUIRED_FIELDS = {
    'level1_plan': ('accountable_assistant', 'coordinating_assistant', 'participating_assistants', 'workstreams', 'authority_envelope', 'owner_approval_evidence', 'plan_status'),
    'level2_plan': ('responsible_assistant', 'responsible_employee', 'level1_plan_reference', 'dispatch_authority', 'task_type', 'risk_level', 'workspace', 'allowed_reads', 'allowed_writes', 'depends_on', 'consumes', 'produces', 'interface_references', 'plan_status'),
    'level2_results_mid': ('level2_plan_reference', 'attempt_number', 'submission_timestamp', 'employee_delivery_reference', 'assistant_audit_status'),
    'level2_results': ('level2_plan_reference', 'level2_results_mid_reference', 'assistant_audit_reference', 'assistant_audit_status', 'final_completion_timestamp'),
    'level2_summary': ('assistant_audit_reference', 'level2_results_reference'),
    'level2_warning': ('level2_plan_reference', 'interruption_detected_at', 'recovery_owner', 'recovery_plan', 'resumption_condition'),
    'level2_error': ('level2_plan_reference', 'interruption_detected_at', 'direct_error_evidence', 'owner_intervention_required', 'paused_scope'),
    'level1_warning': ('level1_plan_reference', 'interruption_detected_at', 'recovery_owner', 'recovery_plan', 'affected_scope'),
    'level1_error': ('level1_plan_reference', 'interruption_detected_at', 'direct_error_evidence', 'owner_intervention_required', 'all_paused_employees'),
    'level1_summary': ('level1_plan_reference', 'participating_assistant', 'completion_assessment', 'audit_evidence', 'exception_references'),
    'level1_results': ('level1_plan_reference', 'source_level1_summaries', 'source_level2_results', 'owner_acceptance_reference', 'reusable_outputs'),
}
STAGE_TRANSITIONS = {
    None: {'planned'}, 'planned': {'active', 'cancelled'}, 'active': {'paused', 'failed', 'accepted'},
    'paused': {'active', 'cancelled'}, 'failed': {'active', 'cancelled'}, 'accepted': {'closed'}, 'closed': set(), 'cancelled': set(),
}
TASK_TRANSITIONS = {
    None: {'planned'}, 'planned': {'dispatched', 'cancelled'}, 'dispatched': {'running', 'paused', 'cancelled'},
    'running': {'submitted', 'paused', 'failed'}, 'submitted': {'audited', 'running', 'paused', 'failed'},
    'audited': {'accepted', 'running', 'paused', 'failed'}, 'accepted': {'integrated', 'closed'},
    'integrated': {'closed'}, 'paused': {'running', 'dispatched', 'cancelled'}, 'failed': {'running', 'cancelled'},
    'closed': set(), 'cancelled': set(),
}
TYPE_STATES = {
    'level1_plan': {'planned'}, 'level2_plan': {'planned'},
    'level1_summary': {'active', 'accepted', 'closed'}, 'level1_results': {'accepted', 'closed'},
    'level1_warning': {'active', 'paused'}, 'level1_error': {'paused', 'failed', 'active', 'cancelled'},
    'level2_results_mid': {'dispatched', 'running', 'submitted', 'audited', 'integrated', 'closed'},
    'level2_results': {'accepted'}, 'level2_summary': {'accepted', 'integrated', 'closed'},
    'level2_warning': {'running', 'paused'}, 'level2_error': {'paused', 'failed', 'running', 'cancelled'},
}
CONSUMABLE = {'accepted', 'integrated', 'closed'}
OWNER_ACTIONS = {'change_project_goal', 'material_scope_expansion', 'change_core_research_hypothesis', 'material_methodology_change', 'new_final_deliverable', 'overwrite_raw_data', 'destructive_delete', 'external_publish', 'paid_external_action', 'production_action', 'project_final_write_or_acceptance', 'authority_envelope_breach', 'unresolved_cross_assistant_conflict', 'unresolved_final_integration_blocker'}
EVENT_SEPARATOR = '\n<!-- governance-event -->\n'


def contained_path(root: Path, relative, must_exist: bool = False) -> Path:
    """Reject absolute paths, traversal and symlink escapes without reading secrets."""
    root = Path(root).resolve()
    raw = str(relative)
    path = Path(raw)
    win = PureWindowsPath(raw)
    if not raw or path.is_absolute() or win.is_absolute() or win.drive or '..' in win.parts or '..' in path.parts:
        raise ValueError('path must be a non-traversing project-relative path')
    target = (root / path).resolve()
    if not target.is_relative_to(root):
        raise ValueError('path escapes allowed root')
    if must_exist and not target.exists():
        raise ValueError(f'missing referenced path: {raw}')
    return target


def read_project_config(root: Path) -> dict:
    core = contained_path(root, 'rules/00-core-governance.md')
    text = core.read_text(encoding='utf-8-sig') if core.is_file() else ''
    values = {}
    for key, value in re.findall(r'^\s*-?\s*([a-z][a-z-]+):\s*(.*?)\s*$', text, re.M):
        values[key] = value.strip('`')
    identifiers = set()
    for key in ('project-code-prefix', 'original-project-identifier', 'current-project-identifier'):
        value = values.get(key, '')
        if re.fullmatch(IDENTIFIER, value):
            identifiers.add(value)
    alias = values.get('project-identifier-aliases', '[]')
    try:
        aliases = json.loads(alias)
    except ValueError:
        aliases = [x.strip(' \"\'') for x in alias.strip('[]').split(',') if x.strip()]
    if isinstance(aliases, list):
        identifiers.update(x for x in aliases if isinstance(x, str) and re.fullmatch(IDENTIFIER, x))
    # YAML block aliases remain readable without a general-purpose YAML parser.
    block = re.search(r'^\s*-?\s*project-identifier-aliases:\s*\n((?:[ \t]+-[ \t]+[^\n]+\n?)*)', text, re.M)
    if block:
        identifiers.update(re.findall(r'^\s*-\s*([A-Za-z][A-Za-z0-9_]*)\s*$', block.group(1), re.M))
    enabled = not bool(re.search(r'enabled\s*:\s*false', values.get('notifications', ''), re.I))
    if 'notifications-enabled' in values:
        enabled = values['notifications-enabled'].lower() == 'true'
    return {'governance_version': int(values.get('governance-version', '1')), 'identifiers': identifiers,
            'current_identifier': values.get('current-project-identifier', values.get('project-code-prefix', '')),
            'notifications_enabled': enabled}


def event_digest(event: dict) -> str:
    data = {k: v for k, v in event.items() if k != 'event_hash' and not k.startswith('_')}
    return hashlib.sha256(json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def parse_record(path: Path) -> list[dict]:
    text = path.read_text(encoding='utf-8-sig')
    if not text.startswith('---\n'):
        return []
    events = []
    for block in text.split(EVENT_SEPARATOR):
        if not block.startswith('---\n') or '\n---\n' not in block[4:]:
            raise ValueError(f'malformed record block: {path.name}')
        front, body = block[4:].split('\n---\n', 1)
        try:
            event = json.loads(front)
        except ValueError:
            if re.search(r'"?schema_version"?\s*:', front):
                raise ValueError(f'invalid canonical front matter: {path.name}')
            return []  # Alpha/V1 are read-only legacy, never trusted as state.
        if not isinstance(event, dict) or event.get('schema_version') != 2:
            raise ValueError(f'unsupported canonical schema: {path.name}')
        expected_body = f"\n# {event.get('record_type')}｜{event.get('task_name')}\n\n{event.get('event_description')}\n"
        if body != expected_body:
            raise ValueError(f'narrative does not match authoritative metadata: {path.name}')
        events.append(event)
    return events


def load_history(root: Path) -> tuple[list[dict], list[str]]:
    logs = contained_path(root, 'work_logs')
    events, warnings = [], []
    if not logs.is_dir():
        return events, warnings
    for path in sorted(logs.glob('*.md')):
        safe = contained_path(root, path.relative_to(root), True)
        parsed = parse_record(safe)
        if not parsed:
            warnings.append(f'legacy record (read-only, no authoritative state): {path.name}')
        for event in parsed:
            if path.name != record_filename(event):
                raise ValueError(f'filename/identity mismatch: {path.name}')
            events.append({**event, '_path': path.relative_to(root).as_posix()})
    try:
        events.sort(key=lambda e: e['sequence'])
    except (KeyError, TypeError) as exc:
        raise ValueError('invalid event sequence') from exc
    previous = None
    ids = set()
    for number, event in enumerate(events, 1):
        if event.get('sequence') != number or event.get('previous_event_hash') != previous:
            raise ValueError('record history sequence/hash chain is broken')
        if event.get('event_hash') != event_digest(event):
            raise ValueError('record history content hash mismatch')
        if not event.get('event_id') or event['event_id'] in ids:
            raise ValueError('missing or duplicate event_id')
        ids.add(event['event_id'])
        previous = event['event_hash']
    return events, warnings


def record_filename(event: dict) -> str:
    kind, code = event.get('record_type'), event.get('task_code')
    if kind not in RECORD_PATTERNS or not isinstance(code, str) or not RECORD_PATTERNS[kind].fullmatch(code):
        raise ValueError('invalid record_type or task_code for record type')
    return f'{kind}_{code}.md'


def stage_code(code: str) -> str:
    return code.split('-', 1)[0] + '-##-###-####'


def state_key(event: dict) -> str:
    return stage_code(event['task_code']) if event['record_type'].startswith('level1_') else event['task_code']


def current_state(events: list[dict], code: str) -> str | None:
    for event in reversed(events):
        if state_key(event) == code:
            return event['execution_status']
    return None


def ref_event(events: list[dict], ref: str, kinds=None, task_code: str | None = None) -> dict:
    if not isinstance(ref, str) or not ref:
        raise ValueError('empty record reference')
    path, eid = split_reference(ref)
    # Absolute or traversal refs must never be accepted by an exact string match.
    if PureWindowsPath(path).drive or path.startswith('/') or '..' in PureWindowsPath(path).parts:
        raise ValueError('unsafe record reference')
    allowed = {kinds} if isinstance(kinds, str) else set(kinds or RECORD_PATTERNS)
    for event in reversed(events):
        if (event.get('_path') == path and (not eid or eid == event['event_id'])
                and event['record_type'] in allowed and (task_code is None or event['task_code'] == task_code)):
            return event
    raise ValueError(f'missing, future or mismatched canonical record reference: {ref}')


def split_reference(reference: str) -> tuple[str, str]:
    # Aggregate task filenames contain literal # placeholders before .md.
    path, separator, fragment = reference.rpartition('.md#')
    return (path + '.md', fragment) if separator else (reference, '')


def require_evidence(root: Path, value) -> None:
    refs = value if isinstance(value, list) else [value]
    if not refs:
        raise ValueError('evidence cannot be empty')
    for ref in refs:
        if not isinstance(ref, str):
            raise ValueError('evidence must be project-relative file references')
        path = contained_path(root, split_reference(ref)[0], True)
        if not path.is_file():
            raise ValueError('evidence must refer to a file')
        if not path.read_bytes().strip():
            raise ValueError('evidence file cannot be empty')


def validate_dag(graph: dict[str, list[str]]) -> None:
    visiting, visited = set(), set()
    def visit(node):
        if node in visiting:
            raise ValueError('dependency cycle detected')
        if node in visited:
            return
        visiting.add(node)
        for dependency in graph[node]:
            if dependency == node:
                raise ValueError('self dependency')
            if dependency not in graph:
                raise ValueError(f'missing dependency: {dependency}')
            visit(dependency)
        visiting.remove(node)
        visited.add(node)
    for node in graph:
        visit(node)


def validate_workstreams(plan: dict) -> None:
    participants = plan['participating_assistants']
    coordinator = plan['coordinating_assistant']
    if not isinstance(participants, list) or len(set(participants)) != len(participants):
        raise ValueError('participating_assistants must be a unique list')
    if coordinator not in participants or any(not isinstance(x, str) or not ASSISTANT_ID.fullmatch(x) for x in participants):
        raise ValueError('invalid/missing participating assistant or coordinator')
    if plan['accountable_assistant'] != coordinator:
        raise ValueError('accountable assistant must be coordinating assistant')
    streams = plan['workstreams']
    if not isinstance(streams, dict):
        raise ValueError('workstreams must map each unique module to one owner')
    for stream in streams.values():
        if not isinstance(stream, dict) or stream.get('owner') not in participants or not isinstance(stream.get('depends_on'), list):
            raise ValueError('workstream owner/dependencies invalid')
    validate_dag({name: row['depends_on'] for name, row in streams.items()})
    envelope = plan['authority_envelope']
    if not isinstance(envelope, dict):
        raise ValueError('authority_envelope must be an object')
    for field in ('max_module_assistants', 'max_parallel_employees_per_assistant'):
        value = envelope.get(field, 0 if field == 'max_module_assistants' else 5)
        if type(value) is not int or value < 0:
            raise ValueError('envelope limits must be non-negative integers')
    if len(participants) - 1 > envelope.get('max_module_assistants', 0):
        raise ValueError('module assistant count exceeds Authority Envelope')
    for field in ('allowed_reads', 'allowed_writes'):
        if not isinstance(envelope.get(field), list) or not envelope[field] or any(not isinstance(x, str) for x in envelope[field]):
            raise ValueError('Authority Envelope must declare explicit read/write scopes')


def validate_interface(root: Path, reference: str, participants=None) -> dict:
    path = contained_path(root, reference, True)
    base = contained_path(root, 'plan/interfaces')
    if not path.is_relative_to(base) or not path.is_file():
        raise ValueError('interface must be in plan/interfaces')
    try:
        value = json.loads(path.read_text(encoding='utf-8-sig'))
    except ValueError as exc:
        raise ValueError('interface contract must use JSON') from exc
    if not isinstance(value, dict) or any(k not in value for k in ('interface_id', 'version', 'owner_assistant', 'consumers')):
        raise ValueError('interface contract lacks required fields')
    if not value['interface_id'] or type(value['version']) is not int or value['version'] < 1 or not isinstance(value['consumers'], list):
        raise ValueError('interface identity/version/consumers invalid')
    ids = [value['owner_assistant'], *value['consumers']]
    if any(not isinstance(x, str) or not ASSISTANT_ID.fullmatch(x) for x in ids):
        raise ValueError('invalid interface assistant')
    if participants and any(x not in participants for x in ids):
        raise ValueError('interface references undeclared assistant')
    return value


def validate_schema(event: dict) -> None:
    record_filename(event)
    kind = event['record_type']
    for key in ('task_name', 'responsible_role', 'event_description'):
        if not isinstance(event.get(key), str) or not event[key].strip():
            raise ValueError(f'missing/non-text required field: {key}')
    for key in REQUIRED_FIELDS[kind]:
        if key not in event:
            raise ValueError(f'{kind} missing field: {key}')
    if 'status' in event or 'previous_status' in event:
        raise ValueError('ambiguous status/previous_status forbidden; use requested_status and expected_previous_status')
    if event.get('record_status') != 'final' or event.get('execution_status') not in TYPE_STATES[kind]:
        raise ValueError('invalid record/execution status for record type')
    if kind.endswith('_plan') and event.get('plan_status') != 'frozen':
        raise ValueError('plan must be frozen')
    for field in ('created_at', 'frozen_at', 'submission_timestamp', 'final_completion_timestamp', 'interruption_detected_at'):
        if field in event:
            if not isinstance(event[field], str) or not event[field]:
                raise ValueError(f'{field} must be an ISO timestamp')
            try:
                datetime.fromisoformat(event[field].replace('Z', '+00:00'))
            except ValueError as exc:
                raise ValueError(f'{field} must be an ISO timestamp') from exc
    for field in ('depends_on', 'consumes', 'produces', 'interface_references', 'artifact_references'):
        if field in event and not isinstance(event[field], list):
            raise ValueError(f'{field} must be a list')
    if 'owner_intervention_required' in event and type(event['owner_intervention_required']) is not bool:
        raise ValueError('owner_intervention_required must be a boolean')
    if EVENT_SEPARATOR.strip() in event['event_description'] or '\n---\n' in event['task_name']:
        raise ValueError('reserved record delimiters in narrative')
    if kind == 'level2_results_mid':
        if type(event['attempt_number']) is not int or event['attempt_number'] < 1:
            raise ValueError('attempt_number must be positive integer')
        if event['assistant_audit_status'] not in {'not_requested', 'pending', 'accepted', 'rejected'}:
            raise ValueError('invalid assistant_audit_status')
    if kind == 'level2_results' and event['assistant_audit_status'] != 'accepted':
        raise ValueError('final results require accepted assistant audit')


def get_task_plan(events: list[dict], code: str) -> dict:
    for event in events:
        if event['record_type'] == 'level2_plan' and event['task_code'] == code:
            return event
    raise ValueError(f'task plan missing: {code}')


def dependency_ready(actual, required) -> bool:
    progress = ['accepted', 'integrated', 'closed']
    if required in progress:
        return actual in progress and progress.index(actual) >= progress.index(required)
    return actual == required


def validate_event(root: Path, event: dict, history: list[dict], *, check_artifacts=True, live=False) -> None:
    validate_schema(event)
    kind, code, state = event['record_type'], event['task_code'], event['execution_status']
    config = read_project_config(root)
    prefix = code.rsplit('_', 1)[0]
    if not config['identifiers']:
        raise ValueError('owner-confirmed project identifier is required before recording')
    if prefix not in config['identifiers']:
        raise ValueError('unrecognized project identifier')
    key = state_key(event)
    actual = current_state(history, key)
    if 'expected_previous_status' in event and event['expected_previous_status'] != actual:
        raise ValueError('expected_previous_status disagrees with authoritative history')
    if event.get('actual_previous_status') != actual:
        raise ValueError('stored previous state disagrees with history')
    transitions = STAGE_TRANSITIONS if kind.startswith('level1_') else TASK_TRANSITIONS
    if state != actual and state not in transitions.get(actual, set()):
        raise ValueError(f'illegal transition: {actual} -> {state}')
    if actual in {'paused', 'failed'} and state not in {'paused', 'failed'}:
        for prior in reversed(history):
            if state_key(prior) != key:
                continue
            if prior['execution_status'] not in {'paused', 'failed'}:
                break
            if prior.get('owner_intervention_required') is True:
                require_evidence(root, event.get('owner_resolution_reference'))
                break
    if 'owner_resolution_reference' in event:
        require_evidence(root, event['owner_resolution_reference'])
    if kind.endswith('_plan') and actual is not None:
        raise ValueError('frozen plan already exists')
    if actual is None and not kind.endswith('_plan'):
        raise ValueError('plan must be recorded first')
    if 'supersedes_reference' in event:
        if not kind.endswith('_plan'):
            raise ValueError('only a new plan may declare supersedes_reference')
        ref_event(history, event['supersedes_reference'], kind)
    if kind == 'level1_plan':
        require_evidence(root, event['owner_approval_evidence'])
        validate_workstreams(event)
        for field in ('allowed_reads', 'allowed_writes'):
            for path in event['authority_envelope'][field]:
                contained_path(root, path)
        if event['responsible_role'] != event['coordinating_assistant']:
            raise ValueError('stage plan submitter must be coordinator')
    parent = None
    if kind != 'level1_plan' and kind.startswith('level1_'):
        parent = ref_event(history, event['level1_plan_reference'], 'level1_plan', stage_code(code))
        if kind != 'level1_results' and event['responsible_role'] not in parent['participating_assistants']:
            raise ValueError('stage record must be submitted by participating assistant')
        if kind != 'level1_results' and event['responsible_role'] != 'assistant_' + code.rsplit('_', 1)[1].split('-')[1]:
            raise ValueError('assistant-scope task code does not match submitter')
        if kind == 'level1_summary' and event['participating_assistant'] != event['responsible_role']:
            raise ValueError('summary participant must match submitter')
        if state != actual and state in {'accepted', 'closed'} and kind != 'level1_results':
            raise ValueError('only owner-accepted stage results may finalize stage')
    if kind == 'level2_plan':
        parent = ref_event(history, event['level1_plan_reference'], 'level1_plan', stage_code(code))
        assistant = event['responsible_assistant']
        if assistant not in parent['participating_assistants'] or event['responsible_role'] != assistant:
            raise ValueError('task assistant is not a declared participant')
        parts = code.rsplit('_', 1)[1].split('-')
        if assistant != f'assistant_{parts[1]}' or not re.fullmatch(r'employee_\d{2,}', event['responsible_employee']):
            raise ValueError('task identity and assistant/employee mismatch')
        if int(event['responsible_employee'].rsplit('_', 1)[1]) != int(parts[2]):
            raise ValueError('task code employee number mismatch')
        workspace = contained_path(root, event['workspace'])
        base = contained_path(root, 'ai_workspace')
        if workspace == base or not workspace.is_relative_to(base):
            raise ValueError('employee workspace must be isolated under ai_workspace')
        if not event['allowed_writes'] or not isinstance(event['allowed_reads'], list) or not isinstance(event['allowed_writes'], list):
            raise ValueError('task scopes must be explicit lists')
        for path in event['allowed_reads']:
            contained_path(root, path)
        for path in event['allowed_writes']:
            if not contained_path(root, path).is_relative_to(workspace):
                raise ValueError('employee write scope escapes its workspace')
        for plan in history:
            if plan['record_type'] == 'level2_plan':
                other = contained_path(root, plan['workspace'])
                if workspace.is_relative_to(other) or other.is_relative_to(workspace):
                    raise ValueError('employee workspace overlaps another task')
        if event['risk_level'] not in {'R0', 'R1', 'R2', 'R3'}:
            raise ValueError('invalid risk level')
        authority = event['dispatch_authority']
        if authority == 'owner-approved':
            require_evidence(root, event.get('owner_dispatch_approval_evidence'))
        elif authority == 'envelope-authorized':
            ref_event(history, event.get('authority_envelope_reference'), 'level1_plan', parent['task_code'])
            envelope = parent['authority_envelope']
            auto = envelope.get('auto_dispatch', False)
            if isinstance(auto, dict):
                auto = auto.get('enabled', False)
            if auto is not True or event['task_type'] not in envelope.get('allowed_task_types', []):
                raise ValueError('dispatch not allowed by Authority Envelope')
            if event['risk_level'] == 'R3' or event['task_type'] in OWNER_ACTIONS or event['task_type'] in envelope.get('prohibited_without_owner', []):
                raise ValueError('owner explicit approval required')
            for field in ('allowed_reads', 'allowed_writes'):
                scopes = [contained_path(root, p) for p in envelope[field]]
                if any(not any(contained_path(root, p).is_relative_to(scope) for scope in scopes) for p in event[field]):
                    raise ValueError('task scope exceeds Authority Envelope')
        else:
            raise ValueError('invalid dispatch authority')
        graph = {p['task_code']: p.get('depends_on', []) for p in history if p['record_type'] == 'level2_plan'}
        graph[code] = event['depends_on']
        validate_dag(graph)
        requirements = event.get('required_dependency_status', {})
        if (not isinstance(requirements, dict) or set(requirements) - set(event['depends_on'])
                or any(state not in CONSUMABLE for state in requirements.values())):
            raise ValueError('required dependency state must be accepted, integrated or closed')
        if 'owner_publication_approval_evidence' in event:
            require_evidence(root, event['owner_publication_approval_evidence'])
        for ref in event['interface_references']:
            validate_interface(root, ref, parent['participating_assistants'])
    if kind.startswith('level2_') and kind != 'level2_plan':
        plan = get_task_plan(history, code)
        if 'level2_plan_reference' in event:
            ref_event(history, event['level2_plan_reference'], 'level2_plan', code)
        if kind != 'level2_summary' and event['responsible_role'] != plan['responsible_assistant']:
            raise ValueError('task event must be submitted through its assistant')
        if kind == 'level2_summary' and event['responsible_role'] not in {plan['responsible_employee'], plan['responsible_assistant']}:
            raise ValueError('summary submitter is not task employee or assistant')
        stage = ref_event(history, plan['level1_plan_reference'], 'level1_plan')
        if current_state(history, stage['task_code']) in {'paused', 'failed', 'cancelled', 'closed'} and state in {'dispatched', 'running', 'submitted', 'audited', 'accepted', 'integrated'}:
            raise ValueError('parent stage pauses/ends task execution')
        if state in {'dispatched', 'running'}:
            for dependency in plan['depends_on']:
                required = plan.get('required_dependency_status', {}).get(dependency, 'accepted')
                if required not in CONSUMABLE or not dependency_ready(current_state(history, dependency), required):
                    raise ValueError('dependency has not reached required state')
            limit = stage['authority_envelope'].get('max_parallel_employees_per_assistant', 5)
            active = {p['task_code'] for p in history if p['record_type'] == 'level2_plan' and p['responsible_assistant'] == plan['responsible_assistant'] and p['task_code'] != code and current_state(history, p['task_code']) in {'dispatched', 'running', 'submitted', 'audited'}}
            if len(active) >= limit:
                raise ValueError('parallel employee limit exceeded')
        if kind == 'level2_results_mid':
            if state in {'submitted', 'audited'}:
                delivery = contained_path(root, event['employee_delivery_reference'], live)
                if not delivery.is_relative_to(contained_path(root, plan['workspace'])):
                    raise ValueError('delivery escapes task workspace')
            if state == 'audited' and event['assistant_audit_status'] not in {'accepted', 'rejected'}:
                raise ValueError('audited event requires explicit assistant decision')
            if state == 'submitted' or (state == 'audited' and event['assistant_audit_status'] == 'accepted'):
                snapshot = event.get('employee_delivery_hash', {})
                if (not isinstance(snapshot, dict) or snapshot.get('algorithm') != 'sha256'
                        or snapshot.get('mode') not in {'file', 'tree-v1'}
                        or not re.fullmatch(r'[0-9a-f]{64}', str(snapshot.get('value', '')))):
                    raise ValueError('accepted audit requires engine-generated delivery hash')
            if state == 'audited':
                submissions = [e for e in history if e['record_type'] == kind and e['task_code'] == code and e['execution_status'] == 'submitted']
                submitted = ref_event(history, event.get('submission_reference'), kind, code)
                if not submissions or submitted['event_id'] != submissions[-1]['event_id']:
                    raise ValueError('audit must reference the latest submitted delivery')
                if (event['attempt_number'] != submitted['attempt_number']
                        or contained_path(root, event['employee_delivery_reference']) != contained_path(root, submitted['employee_delivery_reference'])):
                    raise ValueError('audit attempt/delivery must match submission')
                if event['assistant_audit_status'] == 'accepted' and event['employee_delivery_hash'] != submitted['employee_delivery_hash']:
                    raise ValueError('delivery changed after submission; resubmit before acceptance')
            if state != 'audited' and event['assistant_audit_status'] == 'accepted':
                raise ValueError('only audited state can contain acceptance')
            attempts = [e['attempt_number'] for e in history if e['record_type'] == kind and e['task_code'] == code]
            if attempts and event['attempt_number'] < max(attempts):
                raise ValueError('attempt ledger cannot go backwards')
        if kind in {'level2_results', 'level2_summary'}:
            audit = ref_event(history, event['assistant_audit_reference'], 'level2_results_mid', code)
            if audit['execution_status'] != 'audited' or audit['assistant_audit_status'] != 'accepted':
                raise ValueError('referenced assistant audit has not accepted delivery')
            if kind == 'level2_results':
                mid = ref_event(history, event['level2_results_mid_reference'], 'level2_results_mid', code)
                latest = next(e for e in reversed(history) if state_key(e) == code)
                if mid['event_id'] != audit['event_id'] or latest['event_id'] != audit['event_id'] or actual != 'audited':
                    raise ValueError('final result must follow current accepted audit')
            else:
                result = ref_event(history, event['level2_results_reference'], 'level2_results', code)
                result_audit = ref_event(history, result['assistant_audit_reference'], 'level2_results_mid', code)
                if result_audit['event_id'] != audit['event_id']:
                    raise ValueError('summary and final result refer to different audits')
        if state == 'integrated' and actual != state:
            if event['responsible_role'] != plan['responsible_assistant']:
                raise ValueError('only the responsible assistant records integration')
            target = contained_path(root, event.get('integration_target', ''))
            module_root = contained_path(root, 'assistant_workspace/' + plan['responsible_assistant'])
            demo_root, final_root = contained_path(root, 'project_demo'), contained_path(root, 'project_final')
            if target.is_relative_to(module_root):
                permission = 'assistant_workspace'
            elif target.is_relative_to(demo_root) or target.is_relative_to(final_root):
                if plan['responsible_assistant'] != stage['coordinating_assistant']:
                    raise ValueError('only coordinator integrates project-level deliverables')
                permission = 'project_demo' if target.is_relative_to(demo_root) else 'project_final'
            else:
                raise ValueError('integration target is outside this assistant role scope')
            owner_evidence = event.get('owner_integration_approval_evidence')
            if permission == 'project_final' or stage['authority_envelope'].get('integration_permissions', {}).get(permission) is not True:
                require_evidence(root, owner_evidence)
            elif owner_evidence is not None:
                require_evidence(root, owner_evidence)
    if kind == 'level1_results':
        if event['responsible_role'] != parent['coordinating_assistant']:
            raise ValueError('only coordinator submits stage results')
        require_evidence(root, event['owner_acceptance_reference'])
        for ref in event['source_level1_summaries']:
            summary = ref_event(history, ref, 'level1_summary')
            if stage_code(summary['task_code']) != stage_code(code):
                raise ValueError('summary belongs to another stage')
        for ref in event['source_level2_results']:
            result = ref_event(history, ref, 'level2_results')
            if stage_code(result['task_code']) != stage_code(code):
                raise ValueError('result belongs to another stage')
        tasks = [p for p in history if p['record_type'] == 'level2_plan' and stage_code(p['task_code']) == code]
        if any(current_state(history, p['task_code']) not in CONSUMABLE for p in tasks):
            raise ValueError('stage cannot finish with unfinished tasks')
    for field in ('direct_error_evidence', 'audit_evidence'):
        if field in event:
            require_evidence(root, event[field])
    if check_artifacts:
        from artifact_support import validate_artifact_reference
        for ref in event.get('consumes', []) + event.get('artifact_references', []):
            validate_artifact_reference(root, ref, history)


def replay_history(root: Path, events: list[dict], *, check_artifacts=True) -> None:
    previous = []
    for event in events:
        validate_event(root, event, previous, check_artifacts=check_artifacts)
        previous.append(event)
