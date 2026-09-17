#!/usr/bin/env python3
"""Verify a deployed batch, record delivery, and optionally send the authorized bot digest."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

BASE_URL = 'https://pomeloneo.github.io/ar_xiv_slider/'


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def update_history(path: Path, papers: list[dict]) -> None:
    old = [json.loads(line) for line in path.read_text().splitlines() if line.strip()] if path.exists() else []
    by_id = {row['arxiv_base_id']: row for row in old}
    for paper in papers:
        prior = by_id.get(paper['arxiv_base_id'], {})
        if (prior.get('notification_status') == 'sent'
                and paper.get('notification_status') != 'sent'):
            paper['notification_status'] = 'sent'
            paper['notification'] = prior.get('notification', {})
            paper['delivery_status'] = 'materials_ready_published_and_notified'
        # A republish must never erase a learner's actual answer or verified progress.
        progress = {key: prior[key] for key in ('learner_status', 'learner_answer', 'mastery_verified', 'pending_question') if key in prior}
        paper.update(progress)
        by_id[paper['arxiv_base_id']] = {**prior, **paper}
    with tempfile.NamedTemporaryFile(mode='w', dir=path.parent, encoding='utf-8', delete=False) as out:
        for row in by_id.values():
            out.write(json.dumps(row, ensure_ascii=False) + '\n')
        temporary = out.name
    os.replace(temporary, path)


def finalize(day: Path, site: Path, commit: str, send: bool, recipient: str | None, cli: str | None) -> None:
    if send and (not recipient or not cli):
        raise SystemExit('--send requires --recipient and an available --lark-cli executable')
    batch = json.loads((day / 'batch-prepared.json').read_text())
    papers = batch['papers']
    if len(papers) != 30:
        raise SystemExit('Expected 30 prepared papers')
    audit = day / '.source'
    audit.mkdir(exist_ok=True)
    paths = ['index.html', 'papers.json', 'assets/read-state.js', 'assets/paper-list.js', 'assets/lesson.js', 'assets/lesson.css']
    for paper in papers:
        paths.extend(paper['publication_key'] + '/' + name for name in ('index.html', 'notes.html', 'slides.html', 'answers.html', 'demo.py', 'demo-output.txt', 'map.mmd'))
    def verify(relative: str) -> dict:
        local = (site / relative).read_bytes()
        request = Request(BASE_URL + relative + '?verify=' + commit[:12], headers={'User-Agent': 'arxiv-learning-publication-verifier'})
        with urlopen(request, timeout=45) as response:
            actual = response.read()
            status = response.status
        if status != 200 or hashlib.sha256(local).digest() != hashlib.sha256(actual).digest():
            raise RuntimeError(f'Live content differs: {relative}')
        return {'path': relative, 'status': status, 'sha256': hashlib.sha256(actual).hexdigest()}
    with ThreadPoolExecutor(max_workers=6) as pool:
        verified = list(pool.map(verify, paths))
    now = datetime.now(timezone.utc).isoformat()
    write_json(audit / 'batch-live-verification.json', {'commit': commit, 'verified_at_utc': now, 'files': verified})
    for paper in papers:
        paper['delivery_status'] = 'materials_ready_published'
        paper['publication'] = {'commit': commit, 'http_verified_at_utc': now,
            'notes_url': BASE_URL + paper['publication_key'] + '/notes.html',
            'slides_url': BASE_URL + paper['publication_key'] + '/slides.html',
            'overview_url': BASE_URL + paper['publication_key'] + '/'}
    history = day.parent / 'history.jsonl'
    update_history(history, papers)
    receipt_path = audit / 'batch-lark-receipt.json'
    if send:
        receipt = json.loads(receipt_path.read_text()) if receipt_path.exists() else None
        if not receipt or receipt.get('ok') is not True:
            message = ['新增 30 篇完整论文学习包：AI 13 篇、金融 7 篇、经济 10 篇。',
                '[打开论文列表](' + BASE_URL + ')',
                '每篇均有中文完整讲解、图解课件、Mermaid、已运行的小算例和独立参考答案。任选文章版或图解版即可。',
                '列表与阅读页可手动标记已读／未读；状态仅保存在当前浏览器。']
            for direction in ('AI', '金融', '经济'):
                message.append('\n' + direction)
                for paper in papers:
                    if paper['direction'] == direction:
                        message.append('- [' + paper['title_zh'] + '](' + paper['publication']['overview_url'] + ')')
            text = '\n\n'.join(message)
            (audit / 'batch-message.md').write_text(text, encoding='utf-8')
            result = subprocess.run([cli, 'im', '+messages-send', '--as', 'bot', '--user-id', recipient,
                '--markdown', text, '--idempotency-key', 'arxiv-batch-' + day.name + '-30'], capture_output=True, text=True, timeout=90)
            if result.returncode != 0:
                (audit / 'batch-notification-error.txt').write_text(result.stderr)
                raise SystemExit('Site verified and history saved, but bot send failed; see local notification error')
            receipt = json.loads(result.stdout)
            write_json(receipt_path, receipt)
            if receipt.get('ok') is not True:
                raise SystemExit('Bot did not return ok:true; publication remains recorded without notification success')
        for paper in papers:
            paper['notification_status'] = 'sent'
            paper['delivery_status'] = 'materials_ready_published_and_notified'
            paper['notification'] = {'channel': 'lark_bot_dm', 'receipt': str(receipt_path),
                'message_id': receipt.get('data', {}).get('message_id'), 'ok': True}
        update_history(history, papers)
    write_json(day / 'batch-delivery.json', {'updated_at_utc': now, 'commit': commit, 'papers': papers})
    print(json.dumps({'published': len(papers), 'verified_files': len(verified), 'notified': all(p.get('notification_status') == 'sent' for p in papers), 'history': str(history)}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('day', type=Path)
    parser.add_argument('--site-root', type=Path, default=Path(__file__).resolve().parents[1] / 'site')
    parser.add_argument('--commit', required=True)
    parser.add_argument('--send', action='store_true', help='Send the user-authorized digest to the existing bot DM')
    parser.add_argument('--recipient', help='Previously authorized bot DM user open_id; keep it out of the public repository')
    parser.add_argument('--lark-cli', default=shutil.which('lark-cli'))
    args = parser.parse_args()
    finalize(args.day.resolve(), args.site_root.resolve(), args.commit, args.send, args.recipient, args.lark_cli)
