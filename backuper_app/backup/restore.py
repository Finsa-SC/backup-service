from pathlib import Path
from backuper_app.utils import get_logger
import subprocess
from backuper_app.backup.compression import resolve_compression_from_suffix

logger = get_logger(__name__)

class Restore:
    def __init__(self, file_path: Path = None, date: str = None , extract_path: Path = Path("/tmp/backup_restore"), archive_path: Path = None):
        self.file_path = file_path
        self.date = date
        self.extract_path = extract_path
        self.archive_path = Path(archive_path) if archive_path else None

    def _get_archive_by_date(self) -> list[Path]:
        date = self.date.replace("-", "")
        found_archive = list(
            self.archive_path.rglob(f"*{date}*")
        )
        found_archive.sort(key=lambda arch_name: arch_name.name, reverse=True)

        return found_archive

    def _get_archive_by_name(self) -> Path | None:
        archive_file = Path(self.file_path)
        if archive_file.exists():
            return archive_file

        return None

    def _make_extract_dir(self) -> None:
        self.extract_path.mkdir(
            mode=0o700,
            parents=True,
            exist_ok=True
        )

    def _extract_archive(self, archive_file: Path):
        compression = resolve_compression_from_suffix(archive_file)
        extract_command = [
            "tar",
            compression.extract_flag,
            "-xf",
            str(archive_file),
            "-C",
            str(self.extract_path)
        ]
        subprocess.run(
            extract_command,
            text=True,
            check=True,
        )

    def do_restore(self):
        if self.file_path:
            archive_file = self._get_archive_by_name()
        else:
            archive_stack = self._get_archive_by_date()
            if archive_stack:
                archive_file = archive_stack[0]
            else:
                logger.info(f"No archive found for {self.date}")
                exit(0)

        self._make_extract_dir()

        logger.info(f"Extracting {archive_file}...")
        self._extract_archive(archive_file=archive_file)
        logger.info(f"{archive_file.name} has been extract to {self.extract_path}")

if __name__ == "__main__":
    restore = Restore(date="2026-07-31", archive_path=Path("/home/silence-suzuka/backup_archive"))
    restore.do_restore()