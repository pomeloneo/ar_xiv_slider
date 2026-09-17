#!/usr/bin/env python3
"""Publish one daily arXiv learning package into the static site tree."""

from __future__ import annotations

import argparse
import html
import json
import shutil
from datetime import date
from pathlib import Path
from urllib.parse import quote


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


def validate(args: argparse.Namespace) -> None:
    try:
        parsed_date = date.fromisoformat(args.date)
    except ValueError as exc:
        raise SystemExit(f"Invalid --date value {args.date!r}; expected YYYY-MM-DD") from exc
    if parsed_date.isoformat() != args.date:
        raise SystemExit(f"Invalid --date value {args.date!r}; expected YYYY-MM-DD")

    if not args.source.is_dir():
        raise SystemExit(f"Source directory does not exist: {args.source}")

    if args.slides == "index.html":
        raise SystemExit("--slides cannot be index.html because that path is reserved for the day page")

    slides_path = args.source / args.slides
    if not slides_path.is_file():
        raise SystemExit(f"Slides file does not exist: {slides_path}")


def copy_artifacts(source: Path, destination: Path) -> None:
    if destination.exists():
        shutil.rmtree(destination)
    destination.mkdir(parents=True, exist_ok=True)
    for source_path in source.rglob("*"):
        relative_path = source_path.relative_to(source)
        destination_path = destination / relative_path
        if source_path.is_symlink():
            raise SystemExit(f"Symbolic links are not supported in learning packages: {source_path}")
        if source_path.is_dir():
            destination_path.mkdir(parents=True, exist_ok=True)
        elif source_path.is_file():
            destination_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source_path, destination_path)


def load_manifest(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        raise SystemExit(f"Cannot read existing manifest {path}: {exc}") from exc
    if not isinstance(value, list):
        raise SystemExit(f"Existing manifest must contain a JSON array: {path}")
    return value


def render_day_page(entry: dict[str, str], artifact_names: list[str]) -> str:
    artifact_links = []
    for name in artifact_names:
        if name == "index.html":
            continue
        escaped_name = html.escape(name)
        artifact_links.append(f'<li><a href="{quote(name)}">{escaped_name}</a></li>')

    links_markup = "\n".join(artifact_links)
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="color-scheme" content="light dark">
  <title>{html.escape(entry["title"])}</title>
  <style>
    :root {{
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      color: #18212f;
      background: #f3f6fb;
    }}
    body {{ max-width: 880px; margin: 0 auto; padding: 64px 24px; line-height: 1.7; }}
    a {{ color: #2563eb; }}
    .card {{
      padding: 30px;
      border: 1px solid #dbe3ee;
      border-radius: 18px;
      background: #fff;
      box-shadow: 0 14px 38px rgb(40 61 89 / 8%);
    }}
    .meta {{ color: #607086; }}
    .primary {{
      display: inline-block;
      margin: 16px 0 8px;
      padding: 10px 16px;
      border-radius: 10px;
      color: #fff;
      background: #2563eb;
      text-decoration: none;
      font-weight: 650;
    }}
    @media (prefers-color-scheme: dark) {{
      :root {{ color: #eef4ff; background: #0e1420; }}
      .card {{ border-color: #263247; background: #141c2a; }}
      .meta {{ color: #a9b7ca; }}
      a {{ color: #8ab4ff; }}
      .primary {{ color: #fff; }}
    }}
  </style>
</head>
<body>
  <p><a href="../">← 返回论文列表</a></p>
  <article class="card">
    <p class="meta">{html.escape(entry["date"])} · {html.escape(entry["direction"])} · arXiv:{html.escape(entry["arxiv_id"])}</p>
    <h1>{html.escape(entry["title"])}</h1>
    <p>{html.escape(entry["summary"])}</p>
    <p><a class="primary" href="{html.escape(entry["slides"])}">打开 HTML 幻灯片</a></p>
    <h2>学习包文件</h2>
    <ul>
      {links_markup}
    </ul>
  </article>
</body>
</html>
"""


def main() -> None:
    args = parse_args()
    validate(args)

    site_root = args.site_root.resolve()
    destination = site_root / args.date
    site_root.mkdir(parents=True, exist_ok=True)
    copy_artifacts(args.source.resolve(), destination)

    entry = {
        "date": args.date,
        "title": args.title,
        "arxiv_id": args.arxiv_id,
        "direction": args.direction,
        "summary": args.summary,
        "path": f"{args.date}/",
        "slides": args.slides,
    }

    manifest_path = site_root / "papers.json"
    entries = [
        item
        for item in load_manifest(manifest_path)
        if item.get("date") != args.date
    ]
    entries.append(entry)
    entries.sort(key=lambda item: item.get("date", ""), reverse=True)
    manifest_path.write_text(
        json.dumps(entries, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    artifact_names = sorted(
        str(path.relative_to(destination))
        for path in destination.rglob("*")
        if path.is_file()
    )
    (destination / "index.html").write_text(
        render_day_page(entry, artifact_names),
        encoding="utf-8",
    )

    print(f"Published {args.date} to {destination}")
    print(f"Slides URL path: /ar_xiv_slider/{args.date}/{args.slides}")


if __name__ == "__main__":
    main()
