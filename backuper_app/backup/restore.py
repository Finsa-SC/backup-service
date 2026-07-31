from pathlib import Path
from utils import get_logger
import subprocess
from .compression import COMPRESSION

logger = get_logger(__name__)

class Restore:
    def __init__(self, user_input: str, extract_path: Path = Path("/tmp/backup_restore"), is_file: bool = False, archive_path: Path = None):
        self.user_input = user_input
        self.is_file = is_file
        self.extract_path = extract_path
        self.archive_path = Path(archive_path) if archive_path else None

    def _get_archive_by_date(self) -> list[Path]:
        date = self.user_input.replace("-", "")
        found_archive = list(
            self.archive_path.rglob(f"*{date}*")
        )
        found_archive.sort(key=lambda arch_name: arch_name.name, reverse=True)

        return found_archive

    def _get_archive_by_name(self) -> Path | None:
        archive_file = Path(self.user_input)
        if archive_file.exists():
            return archive_file

        return None

    def _make_extarct_dir(self) -> None:
        self.extract_path.mkdir(mode=0o700, parents=True, exist_ok=True)

    def _resolve_archive_compress_type(self, archive_path: Path):


    def _extract_archive(self, archive_path: Path):
        extract_command = [
            "tar",
            ""
        ]
        subprocess.run()

    def do_restore(self):
        if self.is_file:
            archive_file = self._get_archive_by_name()
        else:
            archive_stack = self._get_archive_by_date()
            if archive_stack:
                archive_file = archive_stack[0]
            else:
                logger.info(f"No archive found for {self.user_input}")
                exit(0)

            self._make_extarct_dir()
        logger.debug(archive_file)


if __name__ == "__main__":
    restore = Restore("2026-07-31", archive_path=Path("/home/silence-suzuka/backup_archive"))
    restore.do_restore()