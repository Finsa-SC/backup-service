from pathlib import Path
from backuper_app.utils import get_archive_by_date, get_archive_by_path, is_valid_checksum

class Verify:
    def __init__(self, file_path: Path = None, archive_path: Path = None, date: str = None):
        self.file_path = file_path
        self.archive_path = archive_path
        self.date = date

    def do_verify(self):
        if self.file_path:
            archive_file = get_archive_by_path(self.file_path)
        elif self.date and self.archive_path:
            archive_file = get_archive_by_date(self.archive_path, date=self.date)[0]
        else:
            raise ValueError("Missing argument for Verify command")

        return is_valid_checksum(archive_file)

if __name__ == "__main__":
    verify = Verify(Path("/home/silence-suzuka/backup_archive/2026/Aug/playground_20260731_182432.tar.zst"))
    verify.do_verify()