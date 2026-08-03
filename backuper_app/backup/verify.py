from pathlib import Path
from backuper_app.utils import get_archive_by_date, get_archive_by_path, validate_checksum, is_checksum_file


class Verify:
    def __init__(self, file_path: Path | None = None, archive_path: Path | None = None, date: str | None = None):
        self.file_path = file_path
        self.archive_path = archive_path
        self.date = date

    def do_verify(self) -> bool:
        if self.file_path:
            archive_file = get_archive_by_path(self.file_path)
        elif self.date and self.archive_path:
            #Find path that not hash file
            match_archives = get_archive_by_date(self.archive_path, date=self.date)
            backup_files = [file for file in match_archives if is_checksum_file(file)]
            archive_file = backup_files[-1]
        else:
            raise ValueError("Missing argument for Verify command")

        #Validate checksum and raise error if any problem occured
        validate_checksum(archive_file)

        return True

if __name__ == "__main__":
    verify = Verify(date="2026-08-02", archive_path=Path("/home/silence-suzuka/backup_archive"))
    verify.do_verify()