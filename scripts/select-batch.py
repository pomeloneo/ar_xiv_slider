#!/usr/bin/env python3
"""Validate a planned candidate pool and draw a heat-weighted batch without replacement."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import secrets
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from html import unescape
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from bs4 import BeautifulSoup

ARXIV_ABS = "https://arxiv.org/abs/"
ARXIV_HTML = "https://arxiv.org/html/"
HF_PAPER = "https://huggingface.co/api/papers/"
USER_AGENT = "arxiv-guided-reading/1.0 (candidate validation)"


def fetch(url: str, timeout: int = 45) -> bytes:
    request = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(request, timeout=timeout) as response:
        return response.read()


def heat_for(base_id: str) -> dict:
    try:
        value = json.loads(fetch(HF_PAPER + base_id))
    except HTTPError as exc:
        if exc.code == 404:
            return {"status": "unknown", "source": HF_PAPER + base_id, "weight": 1}
        raise
    upvotes = value.get("upvotes")
    comments = value.get("numComments")
    stars = value.get("githubStars")
    signals = [number for number in (upvotes, comments, stars) if isinstance(number, int)]
    score = max(signals, default=0)
    weight = 1 if score <= 0 else min(4, 1 + int(math.log2(score + 1)))
    return {
        "status": "observed",
        "source": HF_PAPER + base_id,
        "upvotes": upvotes,
        "comments": comments,
        "github_stars": stars,
        "weight": weight,
    }


def validate_candidate(candidate: dict) -> dict:
    base_id = candidate["base_id"]
    abs_url = ARXIV_ABS + base_id
    soup = BeautifulSoup(fetch(abs_url), "html.parser")
    meta = {}
    for node in soup.select("meta[name]"):
        meta.setdefault(node.get("name"), []).append(unescape(node.get("content", "")).strip())
    canonical = (meta.get("citation_arxiv_id") or [None])[0]
    if canonical != base_id:
        raise RuntimeError(f"{base_id}: canonical arXiv ID mismatch: {canonical}")
    title = (meta.get("citation_title") or [""])[0]
    abstract = (meta.get("citation_abstract") or [""])[0]
    authors = meta.get("citation_author", [])
    publication_date = (meta.get("citation_date") or [""])[0].replace("/", "-")
    version_match = re.search(rf"{re.escape(base_id)}v([1-9]\d*)", str(soup))
    if not title or len(abstract) < 200 or not authors or not version_match:
        raise RuntimeError(f"{base_id}: incomplete title, abstract, authors, or version")
    arxiv_id = f"{base_id}v{version_match.group(1)}"
    html_url = ARXIV_HTML + arxiv_id
    body_chars = 0
    try:
        body = fetch(html_url)
        body_chars = len(BeautifulSoup(body, "html.parser").get_text(" ", strip=True))
        if body_chars < 3000:
            raise RuntimeError(f"{base_id}: HTML body is unexpectedly short")
        body_format = "arxiv_html"
        body_url = html_url
    except HTTPError as exc:
        if exc.code != 404:
            raise
        pdf_url = (meta.get("citation_pdf_url") or [f"https://arxiv.org/pdf/{base_id}"])[0]
        pdf = fetch(pdf_url)
        if len(pdf) < 10_000 or not pdf.startswith(b"%PDF"):
            raise RuntimeError(f"{base_id}: PDF is unavailable or invalid")
        body_format = "pdf"
        body_url = pdf_url
        body_chars = None
    return {
        **candidate,
        "arxiv_id": arxiv_id,
        "title": title,
        "authors": authors,
        "publication_date": publication_date,
        "abstract": abstract,
        "abs_url": abs_url + "v" + version_match.group(1),
        "body_url": body_url,
        "body_format": body_format,
        "body_chars": body_chars,
        "heat": heat_for(base_id),
        "qualified": True,
    }


def random_threshold(total: int) -> tuple[int, dict]:
    ceiling = 1 << 64
    accepted_below = ceiling - (ceiling % total)
    attempts = 0
    while True:
        raw = secrets.token_bytes(8)
        attempts += 1
        number = int.from_bytes(raw, "big")
        if number < accepted_below:
            return number % total, {
                "algorithm": "64-bit rejection sampling",
                "raw_bytes_sha256": hashlib.sha256(raw).hexdigest(),
                "accepted_below": accepted_below,
                "threshold": number % total,
                "attempts": attempts,
            }


def draw(pool: list[dict], count: int) -> tuple[list[dict], list[dict]]:
    remaining = list(pool)
    selected = []
    trace = []
    for draw_number in range(1, count + 1):
        total = sum(item["heat"]["weight"] for item in remaining)
        threshold, random_record = random_threshold(total)
        cursor = 0
        chosen_index = None
        for index, item in enumerate(remaining):
            cursor += item["heat"]["weight"]
            if threshold < cursor:
                chosen_index = index
                break
        assert chosen_index is not None
        chosen = remaining.pop(chosen_index)
        selected.append(chosen)
        trace.append({
            "draw": draw_number,
            "total_weight": total,
            "ordered_ids": [item["base_id"] for item in [*remaining[:chosen_index], chosen, *remaining[chosen_index:]]],
            "chosen_id": chosen["base_id"],
            **random_record,
        })
    return selected, trace


def select(plan_path: Path, output_dir: Path) -> None:
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    record_name = plan.get("record_name", "batch-selection.json")
    if Path(record_name).name != record_name or not record_name.endswith(".json"):
        raise SystemExit("record_name must be a plain JSON filename")
    record_path = output_dir / record_name
    directions = plan["directions"]
    expected_pool = plan["candidates_per_direction"]
    draw_count = plan["draws_per_direction"]
    candidates = []
    seen = set()
    for direction, entries in directions.items():
        if len(entries) != expected_pool:
            raise SystemExit(f"{direction}: expected {expected_pool} candidates, found {len(entries)}")
        for entry in entries:
            if entry["base_id"] in seen:
                raise SystemExit(f"Duplicate candidate ID: {entry['base_id']}")
            seen.add(entry["base_id"])
            candidates.append({"direction": direction, **entry})
    history_path = Path(plan["history_path"])
    history_ids = {
        json.loads(line)["arxiv_base_id"]
        for line in history_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    } if history_path.exists() else set()
    additional_excluded_ids = set(plan.get("additional_excluded_ids", []))
    excluded_ids = history_ids | additional_excluded_ids
    overlap = seen & excluded_ids
    if overlap:
        raise SystemExit(f"Candidates overlap excluded papers: {sorted(overlap)}")
    with ThreadPoolExecutor(max_workers=6) as pool:
        qualified = list(pool.map(validate_candidate, candidates))
    selected = []
    direction_records = {}
    for direction in directions:
        pool = [item for item in qualified if item["direction"] == direction]
        winners, trace = draw(pool, draw_count)
        selected.extend(winners)
        direction_records[direction] = {
            "pool": pool,
            "draw_trace": trace,
            "selected_ids": [item["base_id"] for item in winners],
        }
    now = datetime.now(timezone.utc).isoformat()
    output_dir.mkdir(parents=True, exist_ok=True)
    record = {
        "selected_at_utc": now,
        "selection_date": plan["selection_date"],
        "timezone": "Asia/Shanghai",
        "window": plan["window"],
        "rule_fixed_before_draw": plan["rule"],
        "heat_weight_rule": "unknown/zero=1; max(upvotes, comments, GitHub stars): 1-3=>2, 4-7=>3, >=8=>4",
        "heat_weight_cap_ratio": 4,
        "history_path": str(history_path),
        "history_ids_excluded": sorted(history_ids),
        "additional_ids_excluded": sorted(additional_excluded_ids),
        "all_ids_excluded": sorted(excluded_ids),
        "directions": direction_records,
        "selected": selected,
    }
    record_path.write_text(
        json.dumps(record, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    for item in selected:
        target = output_dir.parent / f"batch-{item['direction']}" / item["base_id"]
        target.mkdir(parents=True, exist_ok=True)
        (target / "selection.json").write_text(
            json.dumps({
                "batch_record": str(record_path),
                "selected_at_utc": now,
                "paper": item,
                "selection_status": "selected_content_pending",
                "mastery_status": "pending_user_response",
            }, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    print(json.dumps({
        "qualified": len(qualified),
        "selected": len(selected),
        "by_direction": {
            direction: direction_records[direction]["selected_ids"]
            for direction in directions
        },
        "record": str(record_path),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plan", type=Path)
    parser.add_argument("output_dir", type=Path)
    args = parser.parse_args()
    select(args.plan.resolve(), args.output_dir.resolve())
