"""Exercise publication boundaries with real temporary source/site trees."""

import argparse
import contextlib
import importlib.util
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "publish-day.py"
SPEC = importlib.util.spec_from_file_location("publish_day", SCRIPT)
publisher = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(publisher)


class PublishDayTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.source = self.root / "source"
        self.source.mkdir()
        (self.source / "slides.html").write_text("<h1>First edition</h1>")
        self.site = self.root / "site"
        self.day = self.site / "2026-09-17"
        self.args = argparse.Namespace(
            source=self.source, site_root=self.site, date="2026-09-17", title="Paper",
            title_zh="论文中文标题",
            arxiv_id="2608.12345v1", direction="AI", summary="Learn a mechanism",
            tags=["机器学习", "可靠性"],
            publication_key=None,
            slides="slides.html",
        )

    def publish(self):
        with contextlib.redirect_stdout(io.StringIO()):
            publisher.publish(self.args)

    def snapshot(self):
        return {p.relative_to(self.site): p.read_bytes() for p in self.site.rglob("*") if p.is_file()}

    def test_rerun_replaces_day_without_duplicates_and_keeps_backup(self):
        (self.source / "old.md").write_text("old notes")
        self.publish()
        (self.source / "old.md").unlink()
        (self.source / "slides.html").write_text("<h1>Second edition</h1>")
        self.publish()
        self.assertEqual((self.day / "slides.html").read_text(), "<h1>Second edition</h1>")
        self.assertFalse((self.day / "old.md").exists())
        self.assertEqual(len(json.loads((self.site / "papers.json").read_text())), 1)
        backups = list(self.root.glob(".publish-backup-*/2026-09-17/old.md"))
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0].read_text(), "old notes")

    def test_manifest_contains_bilingual_titles_and_normalized_tags(self):
        self.args.tags = ["机器学习", "AI", "机器学习", "  可靠性  "]
        self.publish()
        entry = json.loads((self.site / "papers.json").read_text())[0]
        self.assertEqual(entry["title"], "Paper")
        self.assertEqual(entry["title_zh"], "论文中文标题")
        self.assertEqual(entry["tags"], ["AI", "机器学习", "可靠性"])

    def test_home_page_shows_bilingual_titles_and_filter_controls(self):
        self.publish()
        page = (self.site / "index.html").read_text()
        self.assertIn(">论文中文标题</a>", page)
        self.assertIn('class="original-title" lang="en">Paper</p>', page)
        self.assertIn('href="?tag=AI" data-tag="AI"', page)
        self.assertIn(
            'href="?tag=%E6%9C%BA%E5%99%A8%E5%AD%A6%E4%B9%A0" data-tag="机器学习"',
            page,
        )
        self.assertIn('data-tags="[&quot;AI&quot;, &quot;机器学习&quot;, &quot;可靠性&quot;]"', page)
        self.assertIn('src="assets/paper-list.js"', page)
        self.assertIn('src="assets/read-state.js"', page)
        self.assertTrue(all(line == line.rstrip() for line in page.splitlines()))

    def test_home_page_escapes_bilingual_metadata_and_tags(self):
        self.args.title = '<img src=x onerror=alert(1)>'
        self.args.title_zh = '<script>alert("标题")</script>'
        self.args.tags = ['" data-bad="true']
        self.publish()
        page = (self.site / "index.html").read_text()
        self.assertNotIn('<script>alert("标题")</script>', page)
        self.assertNotIn("<img src=x", page)
        self.assertNotIn('data-bad="true"', page)
        self.assertIn("&lt;script&gt;", page)
        self.assertIn("&lt;img", page)
        self.assertIn("&quot; data-bad=&quot;true", page)

    def test_same_date_supports_multiple_unique_publications(self):
        self.publish()
        self.args.publication_key = "2026-09-17-2608.54321"
        self.args.arxiv_id = "2608.54321v1"
        self.args.title = "Second Paper"
        self.args.title_zh = "第二篇论文"
        self.args.direction = "经济"
        self.args.tags = ["因果推断"]
        self.publish()

        second = self.site / "2026-09-17-2608.54321"
        entries = json.loads((self.site / "papers.json").read_text())
        self.assertTrue((self.day / "slides.html").is_file())
        self.assertTrue((second / "slides.html").is_file())
        self.assertEqual(len(entries), 2)
        self.assertEqual({entry["path"] for entry in entries},
                         {"2026-09-17/", "2026-09-17-2608.54321/"})
        page = (self.site / "index.html").read_text()
        self.assertIn("论文中文标题", page)
        self.assertIn("第二篇论文", page)
        self.assertIn('data-tag="经济"', page)
        self.assertIn('data-tag="因果推断"', page)

    def test_rejects_invalid_bilingual_metadata_without_touching_site(self):
        self.publish()
        before = self.snapshot()
        for title_zh, tags in (
            ("", ["机器学习"]),
            ("   ", ["机器学习"]),
            ("论文中文标题", [""]),
            ("论文中文标题", ["x" * 31]),
            ("论文中文标题", list(map(str, range(9)))),
        ):
            with self.subTest(title_zh=title_zh, tags=tags):
                self.args.title_zh = title_zh
                self.args.tags = tags
                with self.assertRaises(SystemExit):
                    self.publish()
                self.assertEqual(self.snapshot(), before)

    def test_rejects_overlap_without_touching_source_or_existing_day(self):
        self.publish()
        original = self.snapshot()
        for source in (self.day, self.site, self.day / "nested"):
            with self.subTest(source=source):
                if source.name == "nested":
                    source.mkdir()
                    (source / "slides.html").write_text("nested")
                self.args.source = source
                before = self.snapshot()
                with self.assertRaises(SystemExit):
                    self.publish()
                self.assertEqual(self.snapshot(), before)
        self.assertEqual((self.day / "slides.html").read_bytes(), original[Path("2026-09-17/slides.html")])

    def test_invalid_manifest_preserves_existing_page(self):
        self.publish()
        for invalid in ("{broken", "{}", "[42]", '[{"date":"2026-09-17"}]'):
            with self.subTest(invalid=invalid):
                (self.site / "papers.json").write_text(invalid)
                before = self.snapshot()
                with self.assertRaises(SystemExit):
                    self.publish()
                self.assertEqual(self.snapshot(), before)

    def test_symlink_preserves_existing_page(self):
        self.publish()
        before = self.snapshot()
        (self.source / "leak.md").symlink_to(self.site / "papers.json")
        with self.assertRaises(SystemExit):
            self.publish()
        self.assertEqual(self.snapshot(), before)

    def test_rejects_unsafe_slide_paths_and_noncanonical_dates(self):
        for value in ("../slides.html", "/slides.html", "https://example.com/x.html",
                      "a/../slides.html", "./slides.html", "a//slides.html",
                      "a\\slides.html", "slides.md", "index.html"):
            with self.subTest(slides=value):
                self.args.slides = value
                with self.assertRaises(SystemExit):
                    self.publish()
                self.assertFalse(self.site.exists())
        self.args.slides = "slides.html"
        for value in ("20260917", "2026-W38-4", "2026-02-30"):
            with self.subTest(date=value):
                self.args.date = value
                with self.assertRaises(SystemExit):
                    self.publish()
                self.assertFalse(self.site.exists())

    def test_nested_slide_and_artifact_urls_are_encoded(self):
        slides = self.source / "lesson one" / "图 #?%.html"
        slides.parent.mkdir()
        slides.write_text("<h1>Slides</h1>")
        self.args.slides = "lesson one/图 #?%.html"
        self.publish()
        expected = "lesson%20one/%E5%9B%BE%20%23%3F%25.html"
        manifest = json.loads((self.site / "papers.json").read_text())
        self.assertEqual(manifest[0]["slides"], self.args.slides)
        self.assertEqual((self.day / "index.html").read_text().count(f'href="{expected}"'), 2)
        self.assertTrue((self.day / self.args.slides).is_file())
        self.publish()  # Filenames with URL-significant characters remain valid on rerun.

    def test_only_public_artifacts_are_copied(self):
        for name in (".env", ".cache/notes.md", "config.py", "credentials.txt",
                     "history.jsonl", "private/notes.md", "auth/token.txt", "AGENTS.md",
                     "session.log", "key.pem", "raw.json", "batch-ai/raw.html", "sources/paper.html"):
            path = self.source / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("private control file")
        for name in ("notes.md", "demo.py", "diagram.mmd", "assets/figure.svg", "assets/style.css"):
            path = self.source / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("public learning artifact")
        self.publish()
        names = {p.relative_to(self.day).as_posix() for p in self.day.rglob("*") if p.is_file()}
        self.assertEqual(names, {"index.html", "slides.html", "notes.md", "demo.py", "diagram.mmd",
                                 "assets/figure.svg", "assets/style.css"})

    def test_day_page_explains_alternative_complete_reading_routes(self):
        (self.source / "notes.html").write_text("<h1>Full article</h1>")
        self.publish()
        page = (self.day / "index.html").read_text()
        self.assertIn("图解全文", page)
        self.assertIn("详细讲解", page)
        self.assertIn("不需要重复读两遍", page)
        self.assertIn('href="notes.html"', page)
        self.assertIn("可选资料与文件", page)
        self.assertTrue(all(line == line.rstrip() for line in page.splitlines()))

    def test_day_page_does_not_link_missing_optional_notes(self):
        self.publish()
        page = (self.day / "index.html").read_text()
        self.assertNotIn('href="notes.html"', page)
        self.assertTrue(all(line == line.rstrip() for line in page.splitlines()))

    def test_day_page_escapes_metadata_for_reading_guide(self):
        self.args.title = '<img src=x onerror=alert(1)>'
        self.args.summary = '<script>alert(1)</script>'
        self.publish()
        page = (self.day / "index.html").read_text()
        self.assertNotIn('<script>alert(1)</script>', page)
        self.assertIn('&lt;script&gt;', page)
        self.assertIn('&lt;img', page)

    def test_copy_failure_preserves_existing_publication(self):
        self.publish()
        before = self.snapshot()
        with patch.object(publisher.shutil, "copy2", side_effect=OSError("Disk full")):
            with self.assertRaises(OSError):
                self.publish()
        self.assertEqual(self.snapshot(), before)
        self.assertFalse(list(self.root.glob(".publish-stage-*")))

    def test_install_failure_restores_page_and_manifest(self):
        self.publish()
        before = self.snapshot()
        original_rename = Path.rename

        def fail_manifest_install(path, target):
            if path.name == "papers.json" and path.parent.name.startswith(".publish-stage-"):
                raise OSError("Install failed")
            return original_rename(path, target)

        with patch.object(Path, "rename", fail_manifest_install):
            with self.assertRaises(OSError):
                self.publish()
        self.assertEqual(self.snapshot(), before)
        self.assertTrue((self.source / "slides.html").is_file())


if __name__ == "__main__":
    unittest.main()
