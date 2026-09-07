from __future__ import annotations
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / 'scripts'))
from record_engine import append_event
from governance_schema import load_history

STAGE = 'DEMO_00-##-###-####'
TASK = 'DEMO_00-00-000-0000'


def initialize(root: Path):
    root.mkdir(parents=True, exist_ok=True)
    result = subprocess.run([sys.executable, '-B', str(REPO/'scripts/initialize_project.py'), str(root), '--prefix', 'DEMO', '--feishu-notifications', 'disabled'], capture_output=True, text=True, encoding='utf-8')
    if result.returncode:
        raise AssertionError(result.stdout + result.stderr)
    (root/'rules/owner-approval.md').write_text('Test fixture: owner approved stage and envelope.\n', encoding='utf-8')
    return root


def reference(event):
    return event['_path'] + '#' + event['event_id']


def base(kind, code, state, role='assistant_00', **fields):
    return dict(record_type=kind, task_code=code, task_name='测试任务', responsible_role=role,
                requested_status=state, event_description='已确认的测试事件。', **fields)


def make_stage(root: Path, **changes):
    payload = base('level1_plan', STAGE, 'planned', accountable_assistant='assistant_00',
                   coordinating_assistant='assistant_00', participating_assistants=['assistant_00'],
                   workstreams={'MAIN': {'owner': 'assistant_00', 'depends_on': []}},
                   authority_envelope={'auto_dispatch': True, 'max_module_assistants': 0,
                       'allowed_reads': ['raw_data', 'common_data', 'common_artifacts', 'ai_workspace'],
                       'allowed_writes': ['ai_workspace'],
                      'max_parallel_employees_per_assistant': 5, 'allowed_task_types': ['data_processing','testing'],
                      'publish_permissions': {'common_data': True,'common_artifacts': True},
                      'integration_permissions': {'assistant_workspace': True, 'project_demo': True, 'project_final': False}},
                   owner_approval_evidence='rules/owner-approval.md')
    payload.update(changes)
    return append_event(root, payload)


def make_task(root: Path, task_code=TASK, workspace=None, **changes):
    events, _ = load_history(root)
    stages = [e for e in events if e['record_type'] == 'level1_plan']
    stage = stages[-1] if stages else make_stage(root)
    workspace = workspace or 'ai_workspace/' + task_code.replace('#', 'x')
    (root/workspace).mkdir(parents=True, exist_ok=True)
    nums = task_code.rsplit('_',1)[1].split('-')
    assistant, employee = 'assistant_'+nums[1], f'employee_{int(nums[2]):02d}'
    payload = base('level2_plan', task_code, 'planned', assistant,
                   responsible_assistant=assistant, responsible_employee=employee,
                   level1_plan_reference=reference(stage), dispatch_authority='envelope-authorized',
                   authority_envelope_reference=reference(stage), task_type='data_processing', risk_level='R1',
                   workspace=workspace, allowed_reads=['raw_data'], allowed_writes=[workspace],
                   depends_on=[], consumes=[], produces=[], interface_references=[])
    payload.update(changes)
    return append_event(root, payload)


def advance(root: Path, plan: dict, state: str, *, attempt=1, audit='not_requested', **changes):
    delivery = plan['workspace'] + '/delivery.txt'
    if not (root/delivery).exists():
        (root/delivery).write_text('validated fixture output\n', encoding='utf-8')
    payload = base('level2_results_mid', plan['task_code'], state, plan['responsible_assistant'],
                   level2_plan_reference=reference(plan), attempt_number=attempt,
                   employee_delivery_reference=delivery if state in {'submitted','audited'} else None,
                   assistant_audit_status=audit)
    payload.update(changes)
    return append_event(root, payload)


def accepted_task(root: Path, task_code=TASK, workspace=None):
    plan = make_task(root, task_code, workspace)
    for state in ('dispatched','running','submitted'):
        advance(root, plan, state)
    audit = advance(root, plan, 'audited', audit='accepted')
    append_event(root, base('level2_results', task_code, 'accepted', plan['responsible_assistant'],
                 level2_plan_reference=reference(plan), level2_results_mid_reference=reference(audit),
                 assistant_audit_reference=reference(audit), assistant_audit_status='accepted'))
    return reference(audit)
