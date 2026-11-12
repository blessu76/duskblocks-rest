import os
import subprocess
import sys
import unittest

SCRIPT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts", "check_release.py")


def run(*args):
    return subprocess.run([sys.executable, SCRIPT, *args], capture_output=True, text=True).returncode


class CheckReleaseTest(unittest.TestCase):
    def test_existing_build_passes(self):
        self.assertEqual(run("--build", "4"), 0)
        self.assertEqual(run("--build", "4", "--latest"), 0)

    def test_missing_build_fails(self):
        self.assertNotEqual(run("--build", "999"), 0)

    def test_bad_build_fails(self):
        self.assertNotEqual(run("--build", "x"), 0)


if __name__ == "__main__":
    unittest.main()
