"""Overwrite protection (output_guard.py). Uses temporary directories only."""

import os
import tempfile
import unittest

import testutil  # noqa: F401
from output_guard import ensure_writable, environment_versions


class OutputGuardTests(unittest.TestCase):

    def test_refuses_non_empty_directory_without_flag(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "results.csv")
            with open(path, "w") as f:
                f.write("keep me")
            with self.assertRaises(SystemExit) as raised:
                ensure_writable(d, overwrite=False)
            self.assertEqual(raised.exception.code, 2)
            with open(path) as f:
                self.assertEqual(f.read(), "keep me")

    def test_allows_with_flag(self):
        with tempfile.TemporaryDirectory() as d:
            open(os.path.join(d, "results.csv"), "w").close()
            ensure_writable(d, overwrite=True)  # no exception

    def test_allows_new_or_desktop_ini_only_directory(self):
        with tempfile.TemporaryDirectory() as d:
            ensure_writable(os.path.join(d, "new"), overwrite=False)
            self.assertTrue(os.path.isdir(os.path.join(d, "new")))
        with tempfile.TemporaryDirectory() as d:
            open(os.path.join(d, "desktop.ini"), "w").close()
            ensure_writable(d, overwrite=False)  # Google Drive file ignored

    def test_versions_recorded(self):
        versions = environment_versions()
        for key in ("python", "pandas", "matplotlib"):
            self.assertIn(key, versions)


if __name__ == "__main__":
    unittest.main()
