#!/usr/bin/env python3
"""Publish one daily arXiv learning package into the static site tree."""

from __future__ import annotations

import argparse
import html
import json
import re
import shutil
import tempfile
from datetime import date
from pathlib import Path, PurePosixPath
from typing import Any
from urllib.parse import quote


PUBLIC_EXTENSIONS = {
    ".html", ".htm", ".css", ".js", ".mjs", ".md", ".txt", ".mmd",
    ".py", ".csv", ".svg", ".png", ".jpg", ".jpeg", ".gif", ".webp",
    ".pdf", ".woff", ".woff2", ".ttf",
}
PRIVATE_NAMES = {
    "config", "configuration", "credentials", "secrets", "tokens", "history",
    "private", "logs", "auth", "agents", "skill",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Copy one learning package into site/YYYY-MM-DD and update the site index."
    )
    parser.add_argument("--source", required=True, type=Path, help="Daily artifact directory")
    parser.add_argument("--date", required=True, help="Publication date in YYYY-MM-DD")
    parser.add_argument("--title", required=True, help="Paper title")
    parser.add_argument("--title-zh", required=True, help="Accurate Chinese translation of the paper title")
    parser.add_argument("--arxiv-id", required=True, help="arXiv ID, optionally with version")
    parser.add_argument(
        "--direction",
        required=True,
        choices=("AI", "金融", "经济"),
        help="Primary learning direction",
    )
    parser.add_argument("--summary", required=True, help="One-sentence learning value")
    parser.add_argument(
        "--tag",
        action="append",
        dest="tags",
        default=[],
        help="Reader-facing Chinese topic tag; repeat for multiple tags",
    )
    parser.add_argument(
        "--publication-key",
        help="Unique single-directory site key; defaults to the publication date",
    )
    parser.add_argument(
        "--slides",
        default="slides.html",
        help="Slides filename relative to the source directory",
    )
    parser.add_argument(
        "--site-root",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "site",
        help="Static site root (defaults to this repository's site directory)",
    )
    return parser.parse_args()


def validate_date(value: str) -> None:
    try:
        parsed_date = date.fromisoformat(value)
    except ValueError as exc:
        raise SystemExit(f"Invalid date {value!r}; expected YYYY-MM-DD") from exc
    if parsed_date.isoformat() != value:
        raise SystemExit(f"Invalid date {value!r}; expected YYYY-MM-DD")


def validate_slide_path(value: str) -> None:
    path = PurePosixPath(value)
    if (
        not value
        or path.is_absolute()
        or path.as_posix() != value
        or ".." in path.parts
        or "\\" in value
        or ":" in path.parts[0]
        or path.suffix.lower() not in {".html", ".htm"}
        or value == "index.html"
    ):
        raise SystemExit("--slides must be a normalized relative HTML path other than index.html")


def validate_publication_key(value: str) -> None:
    if value in {"assets", "index.html", "papers.json"} or not re.fullmatch(
        r"[0-9A-Za-z][0-9A-Za-z._-]{0,79}", value
    ):
        raise SystemExit(
            "--publication-key must be one safe directory segment using letters, digits, dot, underscore, or hyphen"
        )


def base_arxiv_id(value: str) -> str:
    modern = re.fullmatch(r"(?P<base>\d{4}\.\d{4,5})(?:v[1-9]\d*)?", value)
    legacy = re.fullmatch(
        r"(?P<base>[A-Za-z][A-Za-z.-]*/\d{7})(?:v[1-9]\d*)?",
        value,
    )
    match = modern or legacy
    if not match:
        raise SystemExit(
            "--arxiv-id must be a canonical arXiv ID, optionally followed by a lowercase version such as v2"
        )
    return match.group("base").casefold()


def normalize_tags(direction: str, tags: list[str]) -> list[str]:
    normalized = []
    for raw in [direction, *tags]:
        value = raw.strip()
        if not value or len(value) > 30 or any(character in value for character in "<>\n\r\t"):
            raise SystemExit("Each tag must contain 1-30 readable characters without markup or newlines")
        if value not in normalized:
            normalized.append(value)
    if len(normalized) > 8:
        raise SystemExit("A paper may have at most 8 unique tags including its direction")
    return normalized


def is_public_artifact(path: Path) -> bool:
    return (
        path.suffix.lower() in PUBLIC_EXTENSIONS
        and not any(part.startswith(".") for part in path.parts)
        and not any(Path(part).stem.lower() in PRIVATE_NAMES for part in path.parts)
    )


def publication_key_for(args: argparse.Namespace) -> str:
    return getattr(args, "publication_key", None) or args.date


def validate(args: argparse.Namespace) -> list[Path]:
    validate_date(args.date)
    validate_slide_path(args.slides)
    publication_key = publication_key_for(args)
    validate_publication_key(publication_key)
    if not args.title.strip() or not args.title_zh.strip():
        raise SystemExit("English and Chinese titles must both be non-empty")
    if len(args.title) > 500 or len(args.title_zh) > 200:
        raise SystemExit("Paper title is unreasonably long")
    base_arxiv_id(args.arxiv_id)
    normalize_tags(args.direction, args.tags)

    if args.source.is_symlink() or not args.source.is_dir():
        raise SystemExit(f"Source directory does not exist: {args.source}")

    source = args.source.resolve()
    destination = (args.site_root / publication_key).resolve()
    if source.is_relative_to(destination) or destination.is_relative_to(source):
        raise SystemExit("Source and publication destination must not overlap")
    for path in (
        args.site_root,
        args.site_root / publication_key,
        args.site_root / "papers.json",
        args.site_root / "index.html",
    ):
        if path.is_symlink():
            raise SystemExit(f"Publication paths must not be symbolic links: {path}")
    if (args.site_root / publication_key).exists() and not (
        args.site_root / publication_key
    ).is_dir():
        raise SystemExit("The existing publication path must be a directory")

    artifacts = []
    for path in sorted(source.rglob("*")):
        if path.is_symlink():
            raise SystemExit(f"Symbolic links are not supported in learning packages: {path}")
        if not path.is_dir() and not path.is_file():
            raise SystemExit(f"Unsupported learning package file: {path}")
        relative = path.relative_to(source)
        if path.is_file() and relative.as_posix() != "index.html" and is_public_artifact(relative):
            artifacts.append(relative)
    if Path(args.slides) not in artifacts:
        raise SystemExit(f"Slides file is missing or excluded from public artifacts: {args.slides}")
    return artifacts


def copy_artifacts(source: Path, destination: Path, artifacts: list[Path]) -> None:
    destination.mkdir()
    for relative in artifacts:
        destination_path = destination / relative
        destination_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source / relative, destination_path)


def load_manifest(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        raise SystemExit(f"Cannot read existing manifest {path}: {exc}") from exc
    if not isinstance(value, list):
        raise SystemExit(f"Existing manifest must contain a JSON array: {path}")
    required = {"date", "title", "arxiv_id", "direction", "summary", "path", "slides"}
    seen_paths = set()
    seen_arxiv_ids = set()
    for item in value:
        if not isinstance(item, dict) or any(not isinstance(item.get(key), str) for key in required):
            raise SystemExit(f"Existing manifest contains an invalid paper entry: {path}")
        validate_date(item["date"])
        validate_slide_path(item["slides"])
        base_arxiv_id(item["arxiv_id"])
        publication_key = item["path"].removesuffix("/")
        validate_publication_key(publication_key)
        if "title_zh" in item and (
            not isinstance(item["title_zh"], str) or not item["title_zh"].strip()
        ):
            raise SystemExit(f"Existing manifest contains an invalid Chinese title: {path}")
        if "tags" in item and (
            not isinstance(item["tags"], list)
            or any(not isinstance(tag, str) for tag in item["tags"])
            or normalize_tags(item["direction"], item["tags"]) != item["tags"]
        ):
            raise SystemExit(f"Existing manifest contains invalid tags: {path}")
        if (
            item["path"] != f"{publication_key}/"
            or item["direction"] not in {"AI", "金融", "经济"}
            or item["path"] in seen_paths
            or item["arxiv_id"] in seen_arxiv_ids
        ):
            raise SystemExit(f"Existing manifest contains an invalid or duplicate paper entry: {path}")
        seen_paths.add(item["path"])
        seen_arxiv_ids.add(item["arxiv_id"])
    return value


def render_home_page(entries: list[dict[str, Any]]) -> str:
    all_tags = sorted(
        {tag for entry in entries for tag in entry.get("tags", [entry["direction"]])},
        key=lambda tag: (tag not in {"AI", "金融", "经济"}, tag),
    )
    filters = ['<a class="filter is-active" href="./" data-tag="" aria-current="true">全部</a>']
    for tag in all_tags:
        filters.append(
            f'<a class="filter" href="?tag={quote(tag)}" '
            f'data-tag="{html.escape(tag, quote=True)}">{html.escape(tag)}</a>'
        )
    cards = []
    for entry in entries:
        tags = entry.get("tags", [entry["direction"]])
        encoded_tags = html.escape(json.dumps(tags, ensure_ascii=False), quote=True)
        title_zh = entry.get("title_zh") or entry["title"]
        tag_markup = "".join(f"<li>{html.escape(tag)}</li>" for tag in tags)
        cards.append(
            f"""      <li class="paper" data-tags="{encoded_tags}">
        <p class="meta">{html.escape(entry["date"])} · arXiv:{html.escape(entry["arxiv_id"])}</p>
        <h2><a href="{quote(entry["path"], safe="/")}">{html.escape(title_zh)}</a></h2>
        <p class="original-title" lang="en">{html.escape(entry["title"])}</p>
        <ul class="tags" aria-label="论文标签">{tag_markup}</ul>
        <p class="summary">{html.escape(entry["summary"])}</p>
      </li>"""
        )
    paper_markup = "\n".join(cards)
    empty_markup = (
        """    <section class="empty">
      <h2>站点已经就绪</h2>
      <p>学习包发布后，这里会按日期列出中英文标题、主题标签和阅读入口。</p>
    </section>"""
        if not entries
        else f"""    <div class="filters" aria-label="按标签筛选">
      {"".join(filters)}
    </div>
    <p class="result-count" id="result-count" role="status" aria-live="polite">共 {len(entries)} 篇</p>
    <ol class="papers">
{paper_markup}
    </ol>
    <p class="no-results" id="no-results" hidden>没有符合该标签的论文。</p>"""
    )
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="color-scheme" content="light dark">
  <title>每日 arXiv 论文带读</title>
  <style>
    * {{ box-sizing: border-box; }}
    :root {{
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      color: #18212f;
      background: #f3f6fb;
    }}
    body {{ max-width: 960px; margin: 0 auto; padding: 72px 24px; }}
    header {{ margin-bottom: 34px; }}
    h1 {{ margin: 0 0 12px; font-size: clamp(2rem, 5vw, 3.6rem); letter-spacing: -.045em; }}
    p {{ color: #526071; font-size: 1.05rem; line-height: 1.75; }}
    a:focus-visible {{ outline: 3px solid #1d7a70; outline-offset: 4px; }}
    .filters {{ display: flex; flex-wrap: wrap; gap: 10px; margin: 0 0 14px; }}
    .filter {{
      padding: 8px 15px; border: 1px solid #b9c8d8; border-radius: 999px; color: #334155;
      background: #fff; text-decoration: none; font-weight: 650;
    }}
    .filter:hover {{ border-color: #1d7a70; }}
    .filter.is-active {{ color: #fff; border-color: #1d7a70; background: #1d7a70; }}
    .result-count {{ margin: 0 0 18px; font-size: .95rem; }}
    .empty, .no-results {{
      padding: 28px; border: 1px solid #dbe3ee; border-radius: 18px; background: #fff;
      box-shadow: 0 14px 38px rgb(40 61 89 / 8%);
    }}
    .papers {{ display: grid; gap: 18px; padding: 0; list-style: none; }}
    .paper {{
      padding: 26px; border: 1px solid #dbe3ee; border-radius: 18px; background: #fff;
      box-shadow: 0 14px 38px rgb(40 61 89 / 8%);
    }}
    .paper[hidden] {{ display: none; }}
    .paper h2 {{ margin: 9px 0 5px; font-size: clamp(1.35rem, 3vw, 1.8rem); line-height: 1.4; }}
    .paper h2 a {{ color: inherit; text-decoration-thickness: .08em; text-underline-offset: .15em; }}
    .meta {{ margin: 0; font-size: .9rem; }}
    .original-title {{ margin: 0 0 14px; font-size: .96rem; line-height: 1.55; }}
    .summary {{ margin-bottom: 0; }}
    .tags {{ display: flex; flex-wrap: wrap; gap: 7px; padding: 0; margin: 0; list-style: none; }}
    .tags li {{ padding: 4px 10px; border-radius: 999px; color: #245c55; background: #e5f2ef; font-size: .83rem; }}
    @media (max-width: 600px) {{ body {{ padding: 42px 18px; }} .paper {{ padding: 21px; }} }}
    @media (prefers-color-scheme: dark) {{
      :root {{ color: #eef4ff; background: #0e1420; }}
      p {{ color: #a9b7ca; }}
      .empty, .no-results, .paper {{ border-color: #263247; background: #141c2a; }}
      .filter {{ color: #dbe8f5; border-color: #42526a; background: #141c2a; }}
      .filter.is-active {{ color: #081514; border-color: #7bd6c8; background: #7bd6c8; }}
      .tags li {{ color: #a8e5da; background: #213d3a; }}
    }}
  </style>
</head>
<body>
  <header>
    <h1>每日 arXiv 论文带读</h1>
    <p>每天一篇 AI、金融或经济论文，用中文从基础讲清整篇主线。可按标签筛选，打开本篇总览后选择图解全文或详细讲解即可。</p>
  </header>
  <main>
{empty_markup}
  </main>
  <script>
    const controls = [...document.querySelectorAll("[data-tag]")];
    const papers = [...document.querySelectorAll(".paper")];
    const resultCount = document.querySelector("#result-count");
    const noResults = document.querySelector("#no-results");

    function applyTag(requestedTag, updateUrl = false) {{
      const availableTags = new Set(controls.map((control) => control.dataset.tag));
      const tag = availableTags.has(requestedTag) ? requestedTag : "";
      let visible = 0;
      for (const paper of papers) {{
        const tags = JSON.parse(paper.dataset.tags);
        paper.hidden = Boolean(tag) && !tags.includes(tag);
        if (!paper.hidden) visible += 1;
      }}
      for (const control of controls) {{
        const active = control.dataset.tag === tag;
        control.classList.toggle("is-active", active);
        if (active) control.setAttribute("aria-current", "true");
        else control.removeAttribute("aria-current");
      }}
      if (resultCount) resultCount.textContent = tag ? `${{tag}} · ${{visible}} 篇` : `共 ${{visible}} 篇`;
      if (noResults) noResults.hidden = visible !== 0;
      if (updateUrl) {{
        const url = new URL(location.href);
        if (tag) url.searchParams.set("tag", tag);
        else url.searchParams.delete("tag");
        history.pushState({{ tag }}, "", url);
      }}
    }}

    for (const control of controls) {{
      control.addEventListener("click", (event) => {{
        event.preventDefault();
        applyTag(control.dataset.tag, true);
      }});
    }}
    window.addEventListener("popstate", () => {{
      applyTag(new URLSearchParams(location.search).get("tag") || "");
    }});
    applyTag(new URLSearchParams(location.search).get("tag") || "");
  </script>
</body>
</html>
"""


def render_day_page(entry: dict[str, Any], artifact_names: list[str]) -> str:
    labels = {
        "notes.html": "详细讲解（文章版）",
        "answers.html": "自测参考答案（先尝试再看）",
        "demo.py": "Python 算例源码（可选）",
        "test_demo.py": "算例核对测试（可选）",
        "demo-output.txt": "算例的实际运行输出",
        "map.mmd": "Mermaid 关系图源码",
        "map.md": "关系图 Markdown 源文档",
        "selection.md": "选题与抽签记录",
    }
    links = []
    for name in artifact_names:
        if name == "index.html":
            continue
        label = "图解全文（课件）" if name == entry["slides"] else labels.get(name, name)
        links.append(f'<li><a href="{quote(name)}">{html.escape(label)}</a></li>')
    links_markup = "\n".join(links)
    notes_route = ""
    if "notes.html" in artifact_names:
        notes_route = """
        <section class="route">
          <h2>喜欢读文章？</h2>
          <p>详细讲解沿着同一条主线，把背景、每一步的原因、实验与局限展开；技术公式放在选读区域。</p>
          <a class="secondary" href="notes.html">读详细讲解</a>
        </section>"""
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="color-scheme" content="light dark">
  <title>本篇总览 · {html.escape(entry["title"])}</title>
  <style>
    * {{ box-sizing: border-box; }}
    :root {{ font-family: system-ui, -apple-system, "Segoe UI", sans-serif; color: #20343d; background: #f7f7f2; }}
    body {{ max-width: 1000px; margin: 0 auto; padding: 44px 26px 72px; line-height: 1.85; font-size: 18px; }}
    a {{ color: #006f65; text-underline-offset: .18em; }}
    a:focus-visible, summary:focus-visible {{ outline: 3px solid #b76800; outline-offset: 4px; }}
    h1 {{ font-size: clamp(2rem, 5vw, 3.2rem); line-height: 1.3; letter-spacing: -.03em; }}
    h2 {{ font-size: 1.25rem; line-height: 1.45; }}
    .meta {{ color: #586e76; font-size: 15px; }}
    .value {{ font-size: 1.15rem; max-width: 46em; }}
    .guide {{ border-left: 4px solid #006f65; background: #eaf3ee; padding: 16px 22px; margin: 28px 0; }}
    .routes {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 280px), 1fr)); gap: 22px; }}
    .route {{ padding: 26px; border: 1px solid #d7e1dd; border-radius: 14px; background: #fff; }}
    .route h2 {{ margin-top: 0; }}
    .primary, .secondary {{ display: inline-block; padding: 10px 18px; border-radius: 9px; text-decoration: none; font-weight: 650; }}
    .primary {{ color: #fff; background: #006f65; }}
    .secondary {{ border: 1px solid #006f65; }}
    details {{ margin: 28px 0; padding: 18px 22px; border: 1px solid #d7e1dd; border-radius: 12px; }}
    summary {{ cursor: pointer; font-weight: 600; }}
    details p, details li {{ font-size: 16px; overflow-wrap: anywhere; }}
    li {{ margin: 9px 0; }}
    @media(max-width: 600px) {{ body {{ padding: 28px 18px 48px; font-size: 17px; }} .route {{ padding: 20px; }} }}
    @media(prefers-color-scheme: dark) {{
      :root {{ color: #e9f2ee; background: #152320; }}
      a {{ color: #91d7c9; }} .meta {{ color: #afc3bc; }}
      .route {{ background: #20312c; border-color: #435d53; }}
      details {{ border-color: #435d53; }} .guide {{ background: #244038; }}
      .primary {{ color: white; }} .secondary {{ border-color: #91d7c9; }}
    }}
  </style>
</head>
<body>
  <nav aria-label="站点导航"><a href="../">← 返回论文列表</a></nav>
  <main>
    <p class="meta">{html.escape(entry["date"])} · {html.escape(entry["direction"])} · arXiv:{html.escape(entry["arxiv_id"])}</p>
    <h1>从这里开始读这一篇</h1>
    <p class="value">{html.escape(entry["summary"])}</p>
    <div class="guide">
      <strong>这只是总入口，不是第三份必读材料。</strong><br>
      图解全文和详细讲解是同一篇论文的两种阅读方式，不需要重复读两遍。
      整篇内容一次提供，不按天拆讲，也不需要先回答问题才能继续。
    </div>
    <div class="routes">
      <section class="route">
        <h2>第一次读，推荐从这里开始</h2>
        <p>按页看图，从具体问题一路读到完整方法、实验结果和局限。遇到想深究的地方，再查详细讲解。</p>
        <a class="primary" href="{quote(entry["slides"], safe="/")}">开始图解全文</a>
      </section>
{notes_route}
    </div>
    <h2>读懂之后，再动手和自测</h2>
    <p>先用课件里的小实验改变条件、观察结果，再尝试用自己的话解释。代码和公式都是选读，不是进入这篇论文的门槛。</p>
    <details>
      <summary>论文信息</summary>
      <p>{html.escape(entry["title"])}</p>
      <p><a href="https://arxiv.org/abs/{quote(entry["arxiv_id"], safe="")}">查看 arXiv 原文信息</a></p>
    </details>
    <details>
      <summary>可选资料与文件</summary>
      <p>这是资料归档，不是阅读清单；关系图会在正文和课件中直接显示，源码只用于修改或复用。</p>
      <ul>{links_markup}</ul>
    </details>
  </main>
</body>
</html>
"""


def publish(args: argparse.Namespace) -> None:
    artifacts = validate(args)
    site_root = args.site_root.resolve()
    publication_key = publication_key_for(args)
    destination = site_root / publication_key
    manifest_path = site_root / "papers.json"
    index_path = site_root / "index.html"
    entries = [item for item in load_manifest(manifest_path) if item["path"] != f"{publication_key}/"]
    base_id = base_arxiv_id(args.arxiv_id)
    if any(base_arxiv_id(item["arxiv_id"]) == base_id for item in entries):
        raise SystemExit("This paper already exists under another publication key; update that key instead")

    entry = {
        "date": args.date,
        "title": args.title,
        "title_zh": args.title_zh.strip(),
        "arxiv_id": args.arxiv_id,
        "direction": args.direction,
        "tags": normalize_tags(args.direction, args.tags),
        "summary": args.summary,
        "path": f"{publication_key}/",
        "slides": args.slides,
    }

    entries.append(entry)
    entries.sort(key=lambda item: item["date"], reverse=True)
    site_root.mkdir(parents=True, exist_ok=True)

    # Build everything outside the upload tree before touching the previous publication.
    with tempfile.TemporaryDirectory(prefix=".publish-stage-", dir=site_root.parent) as temporary:
        stage = Path(temporary)
        staged_day = stage / publication_key
        staged_manifest = stage / "papers.json"
        staged_index = stage / "index.html"
        copy_artifacts(args.source.resolve(), staged_day, artifacts)
        (staged_day / "index.html").write_text(
            render_day_page(entry, [path.as_posix() for path in artifacts]), encoding="utf-8"
        )
        staged_manifest.write_text(
            json.dumps(entries, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        staged_index.write_text(render_home_page(entries), encoding="utf-8")

        # Previous files remain recoverable outside site/, including after a successful rerun.
        backup = Path(tempfile.mkdtemp(prefix=".publish-backup-", dir=site_root.parent))
        moved_day = moved_manifest = moved_index = False
        installed_day = installed_manifest = installed_index = False
        try:
            if destination.exists():
                destination.rename(backup / publication_key)
                moved_day = True
            if manifest_path.exists():
                manifest_path.rename(backup / "papers.json")
                moved_manifest = True
            if index_path.exists():
                index_path.rename(backup / "index.html")
                moved_index = True
            staged_day.rename(destination)
            installed_day = True
            staged_manifest.rename(manifest_path)
            installed_manifest = True
            staged_index.rename(index_path)
            installed_index = True
        except BaseException:
            if installed_index:
                index_path.rename(stage / "failed-index.html")
            if installed_manifest:
                manifest_path.rename(stage / "failed-papers.json")
            if installed_day:
                destination.rename(stage / "failed-day")
            if moved_day:
                (backup / publication_key).rename(destination)
            if moved_manifest:
                (backup / "papers.json").rename(manifest_path)
            if moved_index:
                (backup / "index.html").rename(index_path)
            raise
        if moved_day or moved_manifest or moved_index:
            print(f"Previous publication backup: {backup}")
        else:
            backup.rmdir()

    print(f"Published {args.date} to {destination}")
    print(f'Slides URL path: /ar_xiv_slider/{publication_key}/{quote(args.slides, safe="/")}')


def main() -> None:
    publish(parse_args())


if __name__ == "__main__":
    main()
