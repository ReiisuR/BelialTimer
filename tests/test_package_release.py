import os
import tempfile
import unittest
import zipfile
from pathlib import Path

from package_release import create_archive


class PackageReleaseTests(unittest.TestCase):

    def test_archive_contains_app_folder_and_executable(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            source = root / "BelialTimer"
            source.mkdir()
            (source / "BelialTimer.exe").write_bytes(b"test executable")
            (source / "LEIA-ME.txt").write_text(
                "Extraia o pacote.",
                encoding="utf-8"
            )
            archive_path = root / "BelialTimer-windows-x64.zip"

            create_archive(source, archive_path)

            with zipfile.ZipFile(archive_path) as archive:
                self.assertEqual(
                    set(archive.namelist()),
                    {
                        "BelialTimer/BelialTimer.exe",
                        "BelialTimer/LEIA-ME.txt"
                    }
                )
                self.assertIsNone(archive.testzip())

    def test_archive_requires_the_application_executable(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            source = root / "BelialTimer"
            source.mkdir()

            with self.assertRaises(FileNotFoundError):
                create_archive(source, root / "application.zip")


if __name__ == "__main__":
    unittest.main()
