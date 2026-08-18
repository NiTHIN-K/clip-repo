import contextlib
import io
import tempfile
import unittest
from pathlib import Path

from crepo.main import build_clipboard_payload, main, normalize_extensions


class ClipboardPayloadTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.directory = Path(self.temporary_directory.name)

    def tearDown(self):
        self.temporary_directory.cleanup()

    def write(self, path, contents):
        target = self.directory / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(contents, encoding="utf-8")

    def test_payload_uses_relative_paths_and_stable_order(self):
        self.write("zeta.py", "print('zeta')")
        self.write("alpha.md", "# Alpha")

        payload, count = build_clipboard_payload(self.directory)

        self.assertEqual(count, 2)
        self.assertLess(payload.index("alpha.md"), payload.index("zeta.py"))
        self.assertNotIn(str(self.directory), payload)

    def test_generated_and_sensitive_files_are_skipped(self):
        self.write("src/app.py", "print('included')")
        self.write("node_modules/package.js", "ignored")
        self.write("credentials.json", '{"token": "ignored"}')
        self.write("binary.json", "before\x00after")

        payload, count = build_clipboard_payload(self.directory)

        self.assertEqual(count, 1)
        self.assertIn("src/app.py", payload)
        self.assertNotIn("node_modules", payload)
        self.assertNotIn("credentials", payload)
        self.assertNotIn("binary", payload)

    def test_large_files_are_skipped(self):
        self.write("small.py", "print('included')")
        self.write("large.py", "x" * 100)

        payload, count = build_clipboard_payload(self.directory, max_file_size=20)

        self.assertEqual(count, 1)
        self.assertIn("small.py", payload)
        self.assertNotIn("large.py", payload)

    def test_extensions_are_normalized(self):
        self.assertEqual(normalize_extensions(["PY, md", ".JSON"]), {".py", ".md", ".json"})

    def test_stdout_mode_returns_success(self):
        self.write("readme.md", "# Example")

        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            exit_code = main([str(self.directory), "--include", "md", "--stdout"])

        self.assertEqual(exit_code, 0)
        self.assertIn("--- readme.md ---", output.getvalue())


if __name__ == "__main__":
    unittest.main()
