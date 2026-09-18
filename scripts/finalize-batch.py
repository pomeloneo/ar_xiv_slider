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
PRIMARY_DIRECTIONS = ('AI', '金融', '经济', '社会研究', '科技与产业')


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


PROGRESS_FIELDS = ('learner_status', 'learner_answer', 'mastery_verified', 'pending_question')


def notification_idempotency_key(day: Path, commit: str) -> str:
    return f'arxiv-batch-{day.name}-{commit[:12]}'


def successful_receipt_for_commit(receipt: dict | None, commit: str) -> bool:
    return bool(receipt and receipt.get('ok') is True and receipt.get('publication_commit') == commit)


def history_key(row: dict) -> str:
    # Each publication is its own event; a later re-selection of the same paper on
    # another day keeps a distinct record instead of overwriting past deliveries.
    return row.get('publication_key') or row['arxiv_base_id']


def update_history(path: Path, papers: list[dict]) -> None:
    old = [json.loads(line) for line in path.read_text().splitlines() if line.strip()] if path.exists() else []
    by_key = {history_key(row): row for row in old}
    # A learner's mastery status belongs to the paper, so the newest record of the
    # same base ID seeds progress even across separate publication events.
    progress_by_base: dict[str, dict] = {}
    for row in old:
        progress_by_base[row['arxiv_base_id']] = {key: row[key] for key in PROGRESS_FIELDS if key in row}
    for paper in papers:
        key = history_key(paper)
        prior = by_key.get(key, {})
        # Notification continuity is per publication event: only a prior send of this
        # same event may mark it already delivered.
        if (prior.get('notification_status') == 'sent'
                and paper.get('notification_status') != 'sent'):
            paper['notification_status'] = 'sent'
            paper['notification'] = prior.get('notification', {})
            paper['delivery_status'] = 'materials_ready_published_and_notified'
        # A republish must never erase a learner's actual answer or verified progress.
        progress = {**progress_by_base.get(paper['arxiv_base_id'], {}),
                    **{field: prior[field] for field in PROGRESS_FIELDS if field in prior}}
        paper.update(progress)
        by_key[key] = {**prior, **paper}
    with tempfile.NamedTemporaryFile(mode='w', dir=path.parent, encoding='utf-8', delete=False) as out:
        for row in by_key.values():
            out.write(json.dumps(row, ensure_ascii=False) + '\n')
        temporary = out.name
    os.replace(temporary, path)


def build_digest(papers: list[dict]) -> str:
    counts = {}
    for paper in papers:
        direction = paper['direction']
        counts[direction] = counts.get(direction, 0) + 1
    ordered = [direction for direction in PRIMARY_DIRECTIONS if direction in counts]
    ordered.extend(sorted(set(counts) - set(ordered)))
    breakdown = '、'.join(f'{direction} {counts[direction]} 篇' for direction in ordered)
    message = [f'新增 {len(papers)} 篇完整论文学习包：{breakdown}。',
        '[打开论文列表](' + BASE_URL + ')',
        '每篇均有中文完整讲解、图解课件、Mermaid、已运行的小算例和独立参考答案。任选文章版或图解版即可。',
        '列表与阅读页可手动标记已读／未读；状态仅保存在当前浏览器。']
    for direction in ordered:
        message.append('\n' + direction)
        for paper in papers:
            if paper['direction'] == direction:
                message.append('- [' + paper['title_zh'] + '](' + paper['publication']['overview_url'] + ')')
    return '\n\n'.join(message)


def finalize(day: Path, site: Path, commit: str, send: bool, recipient: str | None, cli: str | None) -> None:
    if send and (not recipient or not cli):
        raise SystemExit('--send requires --recipient and an available --lark-cli executable')
    batch = json.loads((day / 'batch-prepared.json').read_text())
    papers = batch['papers']
    if len(papers) != batch.get('count') or not papers:
        raise SystemExit('Prepared paper count does not match the batch manifest')
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
        if not successful_receipt_for_commit(receipt, commit):
            text = build_digest(papers)
            (audit / 'batch-message.md').write_text(text, encoding='utf-8')
            result = subprocess.run([cli, 'im', '+messages-send', '--as', 'bot', '--user-id', recipient,
                '--markdown', text, '--idempotency-key', notification_idempotency_key(day, commit)],
                capture_output=True, text=True, timeout=90)
            if result.returncode != 0:
                (audit / 'batch-notification-error.txt').write_text(result.stderr)
                raise SystemExit('Site verified and history saved, but bot send failed; see local notification error')
            receipt = json.loads(result.stdout)
            if receipt.get('ok') is not True:
                write_json(receipt_path, receipt)
                raise SystemExit('Bot did not return ok:true; publication remains recorded without notification success')
            receipt['publication_commit'] = commit
            write_json(receipt_path, receipt)
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
