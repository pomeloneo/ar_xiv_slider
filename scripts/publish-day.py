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
    <p><a class="primary" href="{quote(entry["slides"], safe="/")}">打开 HTML 幻灯片</a></p>
    <h2>学习包文件</h2>
    <ul>
      {links_markup}
    </ul>
  </article>
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
