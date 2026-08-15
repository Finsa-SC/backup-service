from pathlib import Path
from backuper_app.utils import get_logger, validate_checksum
import subprocess
from backuper_app.backup.compression import resolve_compression_from_suffix

logger = get_logger(__name__)

class Restore:
    def __init__(self, file_path: Path, extract_path: Path = Path("/tmp/backup_restore"), archive_path: Path | None = None):
        self.file_path = file_path
        self.extract_path = extract_path
        self.archive_path = Path(archive_path) if archive_path else None

    def _make_extract_dir(self) -> None:
        self.extract_path.mkdir(
            mode=0o700,
            parents=True,
            exist_ok=True
        )

    def _extract_archive(self, archive_file: Path) -> None:
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

    def do_restore(self) -> Path:
        validate_checksum(self.file_path)

        self._make_extract_dir()

        self._extract_archive(archive_file=self.file_path)
        return self.extract_path

if __name__ == "__main__":
    ...
    # restore = Restore(date="2026-07-31", archive_path=Path("/home/silence-suzuka/backup_archive"))
    # restore.do_restore()