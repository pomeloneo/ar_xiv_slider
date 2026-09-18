#!/usr/bin/env python3
"""Render reviewed, authored content.json into a complete static learning package."""
from __future__ import annotations

import argparse
import html
import json
import re
import shutil
from pathlib import Path

MERMAID_PRE = re.compile(r'''<pre\b[^>]*\bclass=["'][^"']*\bmermaid\b[^"']*["'][^>]*>(.*?)</pre>''', re.I | re.S)
MERMAID_DIV = re.compile(r'''<div\b[^>]*\bclass=["'][^"']*\bmermaid\b[^"']*["'][^>]*>(.*?)</div>''', re.I | re.S)
EXECUTABLE_HTML = re.compile(
    r'''<script\b|<[^>]*\s+on[a-z0-9_-]+\s*=|javascript:''',
    re.I,
)


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def diagram(source: str) -> str:
    return f'''<figure data-mermaid>
<div data-mermaid-output></div><p data-mermaid-status>正在绘制关系图…</p>
<figcaption>沿着研究问题、方法、验证和局限，复述这篇论文的主线。宽图可左右滑动。</figcaption>
<details><summary>查看可编辑的 Mermaid 源码</summary><pre data-mermaid-source>{esc(source)}</pre></details>
</figure>'''


def render_fragment(fragment: str) -> str:
    rendered = MERMAID_PRE.sub(lambda match: diagram(html.unescape(match.group(1))), fragment)
    return MERMAID_DIV.sub(lambda match: diagram(html.unescape(match.group(1))), rendered)


def validate_authored_html(fragment: str, source: Path, location: str) -> None:
    if EXECUTABLE_HTML.search(fragment):
        raise ValueError(f'{source}: executable code in authored HTML at {location}')


def shell(meta: dict, title: str, body: str, deck: bool = False) -> str:
    return f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="{esc(meta['summary'])}">
<title>{esc(title)} · {esc(meta['title_zh'])}</title>
<link rel="stylesheet" href="../assets/lesson.css">
<script defer src="../assets/read-state.js"></script>
<script defer src="../assets/mermaid/renderer.js"></script>
{'<script defer src="../assets/lesson.js"></script>' if deck else ''}
</head><body>
<header class="topbar"><a href="../">每日 arXiv 论文带读</a>
<nav aria-label="阅读方式"><a href="./">本篇总览</a><a href="slides.html">图解全文</a><a href="notes.html">详细讲解</a></nav>
<button data-read-toggle="{esc(meta['arxiv_id'])}" disabled>标为已读</button></header>
<p class="storage-notice" data-storage-notice role="status" hidden></p>
<main>{body}</main>
<footer>材料已准备 · 理解程度待你回答后验证。阅读标记仅保存在当前浏览器。</footer>
</body></html>'''


def render(source: Path, target: Path) -> None:
    content = json.loads((source / 'content.json').read_text(encoding='utf-8'))
    meta = content['metadata']
    for field in ('title', 'title_zh', 'arxiv_id', 'direction', 'summary', 'question', 'original_url', 'publication_date'):
        if not isinstance(meta.get(field), str) or not meta[field].strip():
            raise ValueError(f'{source}: missing metadata.{field}')
    if not re.fullmatch(r'\d{4}\.\d{4,5}v\d+', meta['arxiv_id']):
        raise ValueError(f'{source}: expected a versioned modern arXiv ID')
    if not isinstance(meta.get('authors'), list) or not meta['authors']:
        raise ValueError(f'{source}: missing author list')
    if len(content['slides']) < 10 or len(content['sections']) < 5:
        raise ValueError(f'{source}: incomplete lesson structure')
    if len(content.get('answers_html', '').strip()) < 50:
        raise ValueError(f'{source}: missing separate reference answers')
    validate_authored_html(content['answers_html'], source, 'answers_html')
    if not content.get('mermaid', '').strip():
        raise ValueError(f'{source}: missing Mermaid overview')
    for filename in ('demo.py', 'demo-output.txt'):
        if not (source / filename).is_file():
            raise ValueError(f'{source}: missing verified practice artifact {filename}')
    for group_name, group in (('sections', content['sections']), ('slides', content['slides'])):
        for index, section in enumerate(group):
            if not section.get('title') or not section.get('html'):
                raise ValueError(f'{source}: empty learning section')
            validate_authored_html(section['html'], source, f'{group_name}[{index}].html')
    target.mkdir(parents=True, exist_ok=True)
    for filename in ('content.json', 'demo.py', 'demo-output.txt', 'selection.json', 'selection.md', 'test_demo.py', 'notes.md'):
        if (source / filename).is_file():
            shutil.copy2(source / filename, target / filename)
    (target / 'map.mmd').write_text(content['mermaid'] + '\n', encoding='utf-8')
    (target / 'metadata.json').write_text(json.dumps(meta, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    source_info = f'''<details class="sources"><summary>论文信息与原文</summary>
<p lang="en">{esc(meta['title'])}</p><p>{esc('、'.join(meta['authors']))}</p>
<p>arXiv:{esc(meta['arxiv_id'])} · 发布日期：{esc(meta['publication_date'])} · {esc(meta['direction'])}</p>
<p><a href="{esc(meta['original_url'])}">arXiv 论文信息</a> · <a href="{esc(meta.get('html_url') or 'https://arxiv.org/html/' + meta['arxiv_id'])}">论文正文</a></p></details>'''
    intro = f'''<p class="eyebrow">{esc(meta['direction'])} · arXiv:{esc(meta['arxiv_id'])}</p>
<h1>{esc(meta['title_zh'])}</h1><p class="original" lang="en">{esc(meta['title'])}</p>
<p class="lead">{esc(meta['summary'])}</p>'''
    toc = '<nav class="toc" aria-label="文章目录">' + ''.join(
        f'<a href="#section-{i}">{esc(s["title"])}</a>' for i, s in enumerate(content['sections'])
    ) + '</nav>'
    sections = []
    has_article_diagram = any(
        MERMAID_PRE.search(section['html']) or MERMAID_DIV.search(section['html'])
        for section in content['sections']
    )
    for i, section in enumerate(content['sections']):
        sections.append(f'<section id="section-{i}"><h2>{esc(section["title"])}</h2>{render_fragment(section["html"])}</section>')
        if i == 0 and not has_article_diagram:
            sections.append('<section><h2>先看整篇的关系图</h2>' + diagram(content['mermaid']) + '</section>')
    practice = '<section><h2>运行与核对最小实践</h2><p>在安装 Python 3 的环境运行 <code>python3 demo.py</code>。以下是本学习包实际运行的输出，使用教学设定；并非论文实验复现。</p><pre>' + esc((source / 'demo-output.txt').read_text()) + '</pre><p><a href="demo.py">算例源码</a> · <a href="demo-output.txt">运行输出</a> · <a href="map.mmd">图源码</a></p></section>'
    if any('demo.py' in section['html'] for section in content['sections']):
        practice = ''  # The authored practice section already contains the run instructions and output.
    article = '<article>' + intro + toc + ''.join(sections) + practice + '<p><a href="answers.html">完成自测后，再看参考答案</a></p>' + source_info + '</article>'
    (target / 'notes.html').write_text(shell(meta, '详细讲解', article), encoding='utf-8')
    # Both routes must teach the full mechanism. A short slide outline uses the
    # corresponding complete concept explanation instead of becoming a teaser.
    section_by_title = {section['title']: section['html'] for section in content['sections']}
    complete_slides = []
    for slide in content['slides']:
        explanation = section_by_title.get(slide['title'], '')
        body = explanation if len(explanation) > len(slide['html']) else slide['html']
        complete_slides.append({'title': slide['title'], 'html': render_fragment(body)})
    slides = [{'title': meta['title_zh'], 'html': '<p class="lead">' + esc(meta['summary']) + '</p><p>用具体例子读懂整篇论文：问题、机制、证据、局限和自测。方向键或下方按钮翻页。</p>'}, *complete_slides]
    if not any('data-mermaid-source' in slide['html'] for slide in complete_slides):
        slides.insert(2, {'title': '把整篇串起来', 'html': diagram(content['mermaid'])})
    slide_body = ''.join(f'<section class="slide" id="slide-{i+1}" aria-label="第 {i+1} 页"><p class="eyebrow">{i+1:02d} / {len(slides):02d} · {esc(meta["direction"])}</p><h1 tabindex="-1">{esc(s["title"])}</h1>{s["html"]}</section>' for i, s in enumerate(slides))
    choices = ''.join(f'<option value="{i+1}">{i+1}. {esc(s["title"])}</option>' for i, s in enumerate(slides))
    controls = f'<nav class="slide-controls" aria-label="翻页" hidden><button id="previous">上一页</button><label>跳转 <select id="page-select">{choices}</select></label><button id="next">下一页</button></nav>'
    reading_sources = ''.join(section['html'] for section in content['sections'] if section.get('id') == 'sources')
    (target / 'slides.html').write_text(shell(meta, '图解全文', slide_body + controls + source_info + reading_sources, True), encoding='utf-8')
    (target / 'answers.html').write_text(shell(meta, '参考答案', '<article><h1>参考答案</h1><p>先尝试自行解释，再用这里核对理由。答案不是对你掌握程度的判定。</p>' + content['answers_html'] + '<p><a href="notes.html">返回详细讲解</a></p></article>'), encoding='utf-8')
    print(f'Rendered {meta["arxiv_id"]}: {target}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('target', type=Path)
    args = parser.parse_args()
    render(args.source.resolve(), args.target.resolve())
