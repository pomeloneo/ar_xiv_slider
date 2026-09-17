#!/usr/bin/env python3
"""Render and locally publish a reviewed batch; does not push or send notifications."""
from __future__ import annotations

import argparse
import importlib.util
import json
import re
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path


def module(filename: str):
    spec = importlib.util.spec_from_file_location(filename.replace('-', '_'), Path(__file__).with_name(filename))
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def prepare(day: Path, site: Path, expected: int) -> None:
    publisher = module('publish-day.py')
    renderer = module('render-learning-package.py')
    paths = sorted(day.glob('batch-*/*/content.json'))
    if len(paths) != expected:
        raise SystemExit(f'Expected {expected} completed content files, found {len(paths)}; no publication performed')
    seen = set()
    contents = []
    for path in paths:
        content = json.loads(path.read_text())
        base = re.sub(r'v\d+$', '', content['metadata']['arxiv_id'])
        if base in seen:
            raise SystemExit(f'Duplicate paper: {base}')
        seen.add(base)
        if not (path.parent / 'selection.json').exists() and not (path.parent.parent / 'selection.json').exists():
            raise SystemExit(f'Missing selection audit for {path}')
        output = subprocess.run(['python3', 'demo.py'], cwd=path.parent, capture_output=True, text=True, timeout=60, check=True)
        recorded = (path.parent / 'demo-output.txt').read_text()
        if output.stdout.strip() != recorded.strip():
            raise SystemExit(f'Demo output changed: {base}; review before publishing')
        contents.append((path, content, base))
    rendered = day / 'rendered'
    rendered.mkdir(exist_ok=True)
    shutil.copytree(site / 'assets', rendered / 'assets', dirs_exist_ok=True)
    for path, content, base in contents:
        renderer.render(path.parent, rendered / base)
        if not (rendered / base / 'selection.json').exists():
            shutil.copy2(path.parent.parent / 'selection.json', rendered / base / 'selection.json')
    report = []
    for path, content, base in contents:
        meta = content['metadata']
        key = day.name + '-' + base
        publisher.publish(argparse.Namespace(source=rendered / base, site_root=site, date=day.name,
            title=meta['title'], title_zh=meta['title_zh'], arxiv_id=meta['arxiv_id'], direction=meta['direction'],
            tags=meta.get('tags', []), summary=meta['summary'], slides='slides.html', publication_key=key))
        report.append({'arxiv_base_id': base, 'version': meta['arxiv_id'][len(base):], 'title': meta['title'],
            'title_zh': meta['title_zh'], 'authors': meta['authors'], 'original_url': meta['original_url'],
            'selection_date': day.name, 'timezone': 'Asia/Shanghai', 'direction': meta['direction'],
            'artifact_path': str(rendered / base), 'source_content': str(path),
            'delivery_status': 'materials_ready_publication_pending', 'learner_status': 'awaiting_response',
            'mastery_verified': False, 'pending_question': meta['question'], 'learner_answer': None,
            'publication_key': key, 'notification_status': 'not_sent'})
    result = {'prepared_at_utc': datetime.now(timezone.utc).isoformat(), 'count': len(report), 'papers': report}
    (day / 'batch-prepared.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(f'Prepared {len(report)} packages; deployment and notification remain pending')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('day', type=Path)
    parser.add_argument('--site-root', type=Path, default=Path(__file__).resolve().parents[1] / 'site')
    parser.add_argument('--expect-count', type=int, default=30)
    args = parser.parse_args()
    prepare(args.day.resolve(), args.site_root.resolve(), args.expect_count)
