#!/usr/bin/env python3
"""Publish one daily arXiv learning package into the static site tree."""

from __future__ import annotations

import argparse
import html
import json
import shutil
import tempfile
from datetime import date
from pathlib import Path, PurePosixPath
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
    parser.add_argument("--arxiv-id", required=True, help="arXiv ID, optionally with version")
    parser.add_argument(
        "--direction",
        required=True,
        choices=("AI", "金融", "经济"),
        help="Primary learning direction",
    )
    parser.add_argument("--summary", required=True, help="One-sentence learning value")
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


def is_public_artifact(path: Path) -> bool:
    return (
        path.suffix.lower() in PUBLIC_EXTENSIONS
        and not any(part.startswith(".") for part in path.parts)
        and not any(Path(part).stem.lower() in PRIVATE_NAMES for part in path.parts)
    )


def validate(args: argparse.Namespace) -> list[Path]:
    validate_date(args.date)
    validate_slide_path(args.slides)

    if args.source.is_symlink() or not args.source.is_dir():
        raise SystemExit(f"Source directory does not exist: {args.source}")

    source = args.source.resolve()
    destination = (args.site_root / args.date).resolve()
    if source.is_relative_to(destination) or destination.is_relative_to(source):
        raise SystemExit("Source and publication destination must not overlap")
    for path in (args.site_root, args.site_root / args.date, args.site_root / "papers.json"):
        if path.is_symlink():
            raise SystemExit(f"Publication paths must not be symbolic links: {path}")
    if (args.site_root / args.date).exists() and not (args.site_root / args.date).is_dir():
        raise SystemExit("The existing day path must be a directory")

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


def load_manifest(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        raise SystemExit(f"Cannot read existing manifest {path}: {exc}") from exc
    if not isinstance(value, list):
        raise SystemExit(f"Existing manifest must contain a JSON array: {path}")
    required = {"date", "title", "arxiv_id", "direction", "summary", "path", "slides"}
    seen_dates = set()
    for item in value:
        if not isinstance(item, dict) or any(not isinstance(item.get(key), str) for key in required):
            raise SystemExit(f"Existing manifest contains an invalid paper entry: {path}")
        validate_date(item["date"])
        validate_slide_path(item["slides"])
        if (
            item["path"] != f'{item["date"]}/'
            or item["direction"] not in {"AI", "金融", "经济"}
            or item["date"] in seen_dates
        ):
            raise SystemExit(f"Existing manifest contains an invalid or duplicate paper entry: {path}")
        seen_dates.add(item["date"])
    return value


def render_day_page(entry: dict[str, str], artifact_names: list[str]) -> str:
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
    destination = site_root / args.date
    manifest_path = site_root / "papers.json"
    entries = [item for item in load_manifest(manifest_path) if item["date"] != args.date]

    entry = {
        "date": args.date,
        "title": args.title,
        "arxiv_id": args.arxiv_id,
        "direction": args.direction,
        "summary": args.summary,
        "path": f"{args.date}/",
        "slides": args.slides,
    }

    entries.append(entry)
    entries.sort(key=lambda item: item["date"], reverse=True)
    site_root.mkdir(parents=True, exist_ok=True)

    # Build everything outside the upload tree before touching the previous publication.
    with tempfile.TemporaryDirectory(prefix=".publish-stage-", dir=site_root.parent) as temporary:
        stage = Path(temporary)
        staged_day = stage / args.date
        staged_manifest = stage / "papers.json"
        copy_artifacts(args.source.resolve(), staged_day, artifacts)
        (staged_day / "index.html").write_text(
            render_day_page(entry, [path.as_posix() for path in artifacts]), encoding="utf-8"
        )
        staged_manifest.write_text(
            json.dumps(entries, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )

        # Previous files remain recoverable outside site/, including after a successful rerun.
        backup = Path(tempfile.mkdtemp(prefix=".publish-backup-", dir=site_root.parent))
        moved_day = moved_manifest = installed_day = installed_manifest = False
        try:
            if destination.exists():
                destination.rename(backup / args.date)
                moved_day = True
            if manifest_path.exists():
                manifest_path.rename(backup / "papers.json")
                moved_manifest = True
            staged_day.rename(destination)
            installed_day = True
            staged_manifest.rename(manifest_path)
            installed_manifest = True
        except BaseException:
            if installed_manifest:
                manifest_path.rename(stage / "failed-papers.json")
            if installed_day:
                destination.rename(stage / "failed-day")
            if moved_day:
                (backup / args.date).rename(destination)
            if moved_manifest:
                (backup / "papers.json").rename(manifest_path)
            raise
        if moved_day or moved_manifest:
            print(f"Previous publication backup: {backup}")
        else:
            backup.rmdir()

    print(f"Published {args.date} to {destination}")
    print(f'Slides URL path: /ar_xiv_slider/{args.date}/{quote(args.slides, safe="/")}')


def main() -> None:
    publish(parse_args())


if __name__ == "__main__":
    main()
