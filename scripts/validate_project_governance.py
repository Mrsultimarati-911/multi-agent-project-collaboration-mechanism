#!/usr/bin/env python3
"""Read-only V1 compatibility and strict canonical V2 governance verification."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from governance_schema import (
    V1_DIRS, V2_DIRS, contained_path, load_history, read_project_config,
    replay_history, validate_dag, validate_interface, validate_workstreams,
)
from artifact_support import validate_manifest


def validate_project(project_root: Path) -> tuple[list[str], list[str]]:
    root = Path(project_root).resolve()
    errors, warnings = [], []
    if not root.is_dir():
        return ['project root does not exist'], warnings
    try:
        config = read_project_config(root)
    except (ValueError, OSError) as exc:
        return [f'governance config: {exc}'], warnings
    version = config['governance_version']
    if version not in (1, 2):
        errors.append('unsupported governance-version')
    for directory in V1_DIRS + V2_DIRS:
        try:
            target = contained_path(root, directory)
            if not target.is_dir():
                (warnings if version == 1 and directory in V2_DIRS else errors).append('missing directory: ' + directory)
        except ValueError as exc:
            errors.append(f'{directory}: {exc}')
    for relative in ('AGENTS.md', 'rules/00-core-governance.md', 'rules/01-role-and-filesystem.md', 'rules/02-work-log-governance.md'):
        try:
            if not contained_path(root, relative).is_file():
                errors.append('missing file: ' + relative)
        except ValueError as exc:
            errors.append(f'{relative}: {exc}')
    try:
        events, legacy = load_history(root)
        warnings.extend(legacy)
    except (ValueError, OSError, TypeError, KeyError) as exc:
        return errors + [f'history: {exc}'], warnings
    try:
        # Whole-graph checks catch cycles even before replaying individual records.
        validate_dag({e['task_code']: e.get('depends_on', []) for e in events if e['record_type'] == 'level2_plan'})
        for event in events:
            if event['record_type'] == 'level1_plan':
                validate_workstreams(event)
        replay_history(root, events)
    except (ValueError, OSError, TypeError, KeyError) as exc:
        errors.append(f'governance: {exc}')
    for kind in ('common_data', 'common_artifacts'):
        try:
            directory = contained_path(root, kind)
            if not directory.is_dir():
                continue
            for artifact in sorted(directory.iterdir()):
                contained_path(root, artifact.relative_to(root), True)
                if not artifact.is_dir():
                    continue
                for ver in sorted(artifact.iterdir()):
                    contained_path(root, ver.relative_to(root), True)
                    if not ver.is_dir():
                        continue
                    manifest = ver/'manifest.json'
                    if not manifest.is_file():
                        manifest = ver/'manifest.yaml'
                        if manifest.is_file():
                            warnings.append('legacy JSON-compatible manifest: ' + manifest.relative_to(root).as_posix())
                    if not manifest.is_file():
                        errors.append('missing manifest: ' + ver.relative_to(root).as_posix())
                        continue
                    try:
                        validate_manifest(root, manifest, events)
                    except (ValueError, OSError, TypeError, KeyError) as exc:
                        errors.append(f'artifact {manifest.relative_to(root)}: {exc}')
        except (ValueError, OSError) as exc:
            errors.append(f'{kind}: {exc}')
    try:
        interface_dir = contained_path(root, 'plan/interfaces')
        if interface_dir.is_dir():
            participants = {x for e in events if e['record_type'] == 'level1_plan' for x in e['participating_assistants']}
            for path in sorted(interface_dir.iterdir()):
                if path.is_file() and path.suffix in ('.json', '.yaml'):
                    validate_interface(root, path.relative_to(root).as_posix(), participants)
    except (ValueError, OSError, TypeError, KeyError) as exc:
        errors.append(f'interface: {exc}')
    if version == 1:
        warnings.append('V1 compatibility mode: legacy narrative records are not canonical authorization evidence')
    return errors, warnings


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('project_root', type=Path)
    args = parser.parse_args(argv)
    errors, warnings = validate_project(args.project_root)
    for message in warnings:
        print('WARNING: ' + message)
    for message in errors:
        print('ERROR: ' + message)
    print(f"RESULT: {'PASS' if not errors else 'FAIL'} ({len(errors)} errors, {len(warnings)} warnings)")
    return 0 if not errors else 1


if __name__ == '__main__':
    raise SystemExit(main())
