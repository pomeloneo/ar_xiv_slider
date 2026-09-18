from pathlib import Path
import subprocess
import sys
import unittest


class DemoTests(unittest.TestCase):
    def test_output_matches_reviewed_record(self):
        root = Path(__file__).parent
        result = subprocess.run(
            [sys.executable, str(root / "demo.py")],
            capture_output=True,
            text=True,
            check=True,
        )
        self.assertEqual(result.stderr, "")
        self.assertEqual(result.stdout, (root / "demo-output.txt").read_text())
        self.assertIn("边界：", result.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
