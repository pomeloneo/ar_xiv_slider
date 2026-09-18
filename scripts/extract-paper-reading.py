#!/usr/bin/env python3
"""Extract a compact, citable reading view from saved arXiv HTML/PDF sources."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from bs4 import BeautifulSoup


KEEP_SECTION_TERMS = (
    "abstract", "introduction", "background", "method", "model", "framework",
    "experiment", "result", "evaluation", "discussion", "limitation",
    "conclusion", "data", "identification", "empirical", "analysis",
)


def clean(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def extract_html(path: Path) -> dict:
    soup = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")
    title = clean((soup.select_one("h1.ltx_title") or soup.title).get_text(" ", strip=True))
    abstract_node = soup.select_one(".ltx_abstract")
    abstract = clean(abstract_node.get_text(" ", strip=True)) if abstract_node else ""
    sections = []
    for section in soup.select("section.ltx_section"):
        heading = section.find(["h2", "h3"], recursive=False)
        if heading is None:
            continue
        name = clean(heading.get_text(" ", strip=True))
        lowered = name.casefold()
        if not any(term in lowered for term in KEEP_SECTION_TERMS):
            continue
        direct = []
        for child in section.find_all(["p", "figcaption", "table"], recursive=True):
            parent_section = child.find_parent("section", class_="ltx_section")
            if parent_section is not section:
                continue
            text = clean(child.get_text(" ", strip=True))
            if text and text not in direct:
                direct.append(text)
        sections.append({"heading": name, "text": "\n".join(direct)})
    figures = []
    for figure in soup.select("figure"):
        caption = figure.find("figcaption")
        if caption:
            text = clean(caption.get_text(" ", strip=True))
            if text:
                figures.append(text)
    return {
        "format": "arxiv_html",
        "title": title,
        "abstract": abstract,
        "sections": sections,
        "figure_and_table_captions": figures,
        "body_chars": len(clean(soup.get_text(" ", strip=True))),
    }


def extract_pdf(path: Path) -> dict:
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise RuntimeError(
            "PDF extraction requires pypdf on PYTHONPATH; install it in a task-local dependency directory"
        ) from exc
    reader = PdfReader(path)
    pages = [clean(page.extract_text() or "") for page in reader.pages]
    pages = [page for page in pages if page]
    text = "\n".join(pages)
    return {
        "format": "pdf_text",
        "title": pages[0][:500] if pages else "",
        "abstract": "",
        "sections": [{"heading": f"PDF page {index}", "text": page} for index, page in enumerate(pages, 1)],
        "figure_and_table_captions": [
            line for line in text.splitlines()
            if re.match(r"\s*(Figure|Fig\.|Table)\s+\d+", line)
        ],
        "body_chars": len(text),
    }


def main(source: Path, target: Path) -> None:
    result = extract_pdf(source) if source.suffix.casefold() == ".pdf" else extract_html(source)
    target.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "source": str(source),
        "target": str(target),
        "format": result["format"],
        "sections": len(result["sections"]),
        "captions": len(result["figure_and_table_captions"]),
        "body_chars": result["body_chars"],
    }, ensure_ascii=False))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("target", type=Path)
    args = parser.parse_args()
    main(args.source.resolve(), args.target.resolve())
