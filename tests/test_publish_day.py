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
            arxiv_id="2608.12345v1", direction="AI", summary="Learn a mechanism",
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
                     "session.log", "key.pem", "raw.json"):
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
