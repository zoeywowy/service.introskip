"""Regression tests for reproducible Kodi packages."""
import hashlib
import os
from pathlib import Path
import subprocess
import sys
import unittest
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]


class BuildZipTests(unittest.TestCase):
    def test_source_file_timestamps_do_not_change_package(self):
        source_file = ROOT / "main.py"
        original = source_file.stat()
        addon = ET.parse(ROOT / "addon.xml").getroot()
        output = ROOT / "dist" / "service.introskip-{}.zip".format(addon.get("version"))

        def build_hash():
            subprocess.run(
                [sys.executable, str(ROOT / "build_zip.py")],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            )
            return hashlib.sha256(output.read_bytes()).hexdigest()

        try:
            first_hash = build_hash()
            os.utime(
                source_file,
                ns=(original.st_atime_ns, original.st_mtime_ns + 2_000_000_000),
            )
            second_hash = build_hash()
        finally:
            os.utime(source_file, ns=(original.st_atime_ns, original.st_mtime_ns))

        self.assertEqual(first_hash, second_hash)


if __name__ == "__main__":
    unittest.main()
