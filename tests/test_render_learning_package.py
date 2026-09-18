"""Mermaid authoring blocks become one rendered, reader-facing diagram."""
import importlib.util
import unittest
from pathlib import Path


SPEC = importlib.util.spec_from_file_location(
    "renderer",
    Path(__file__).resolve().parents[1] / "scripts/render-learning-package.py",
)
renderer = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(renderer)


class MermaidFragmentTests(unittest.TestCase):
    def test_div_mermaid_block_is_converted_to_rendering_contract(self):
        result = renderer.render_fragment(
            '<div class="mermaid">flowchart TD\nA --&gt; B</div><p>图意说明</p>'
        )

        self.assertIn("<figure data-mermaid>", result)
        self.assertIn("<pre data-mermaid-source>flowchart TD\nA --&gt; B</pre>", result)
        self.assertNotIn('<div class="mermaid">', result)
        self.assertEqual(result.count("<figure data-mermaid>"), 1)

    def test_pre_mermaid_block_remains_supported(self):
        result = renderer.render_fragment(
            '<pre class="diagram mermaid wide">flowchart LR\nA --&gt; B</pre>'
        )

        self.assertIn("<figure data-mermaid>", result)
        self.assertNotIn('class="diagram mermaid wide"', result)


class AuthoredHtmlSafetyTests(unittest.TestCase):
    SOURCE = Path("2026-09-18-2609.00000")

    def test_script_tag_in_answers_is_rejected(self):
        with self.assertRaises(ValueError):
            renderer.validate_authored_html(
                "<p>正常讲解</p><script>steal()</script>",
                self.SOURCE,
                "answers_html",
            )

    def test_inline_event_handler_is_rejected(self):
        with self.assertRaises(ValueError):
            renderer.validate_authored_html(
                '<img src="x" onload="fetch(\'/steal\')">',
                self.SOURCE,
                "sections[0].html",
            )

    def test_javascript_uri_is_rejected(self):
        with self.assertRaises(ValueError):
            renderer.validate_authored_html(
                '<a href="javascript:alert(1)">点我</a>',
                self.SOURCE,
                "slides[3].html",
            )

    def test_ordinary_teaching_html_is_allowed(self):
        # A clean fragment with code, links and inline markup must not be flagged.
        renderer.validate_authored_html(
            '<p>输入是价格序列，输出是<code>alpha</code>。</p>'
            '<a href="https://arxiv.org/abs/2609.00000">原文</a>',
            self.SOURCE,
            "sections[1].html",
        )


if __name__ == "__main__":
    unittest.main()
