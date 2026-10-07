import os
import unittest
from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory

from app import delete_file, rename_file, replace_file, save_file


class FileOperationsTest(unittest.TestCase):
    def test_save_rename_replace_and_delete(self):
        with TemporaryDirectory(dir=Path.cwd()) as directory:
            storage = Path(directory)
            saved = save_file(BytesIO(b"first"), "report.pdf", storage)
            self.assertEqual(saved.read_bytes(), b"first")

            renamed = rename_file("report.pdf", "medical-report.pdf", storage)
            replace_file("medical-report.pdf", BytesIO(b"second"), "new-version.pdf", storage)
            replacement = storage / "new-version.pdf"
            self.assertFalse(renamed.exists())
            self.assertEqual(replacement.read_bytes(), b"second")

            delete_file("new-version.pdf", storage)
            self.assertFalse(replacement.exists())

    def test_replaces_with_different_extension_and_updates_metadata(self):
        with TemporaryDirectory(dir=Path.cwd()) as directory:
            storage = Path(directory)
            original = save_file(BytesIO(b"old"), "load.xlsx", storage)
            os.utime(original, (1_000_000, 1_000_000))

            replacement = replace_file("load.xlsx", BytesIO(b"new content"), "report.pdf", storage)

            self.assertFalse(original.exists())
            self.assertEqual(replacement.name, "report.pdf")
            self.assertEqual(replacement.suffix, ".pdf")
            self.assertEqual(replacement.read_bytes(), b"new content")
            self.assertEqual(replacement.stat().st_size, 11)
            self.assertGreater(replacement.stat().st_mtime, 1_000_000)

    def test_collision_and_unsafe_name_leave_files_intact(self):
        with TemporaryDirectory(dir=Path.cwd()) as directory:
            storage = Path(directory)
            original = save_file(BytesIO(b"original"), "original.txt", storage)
            other = save_file(BytesIO(b"other"), "existing.pdf", storage)

            with self.assertRaises(FileExistsError):
                replace_file("original.txt", BytesIO(b"replacement"), "existing.pdf", storage)
            self.assertEqual(original.read_bytes(), b"original")
            self.assertEqual(other.read_bytes(), b"other")

            with self.assertRaises(ValueError):
                save_file(BytesIO(b"private"), "../private.pdf", storage)


if __name__ == "__main__":
    unittest.main()
