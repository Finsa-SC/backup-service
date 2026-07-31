from pathlib import Path
from backuper_app.utils import get_logger
from datetime import datetime

logger = get_logger(__name__)

class Archive:
    def __init__(self, expired_backups: list[Path], archive_path: Path = None, archive_enabled: bool = False):
        self._archive_path = archive_path
        self._expired_backups = expired_backups
        self.archive_enabled = archive_enabled

    def _move_into_archive(self, old_backup: Path):
        old_backup.move_into(self._archive_path)

    @staticmethod
    def _delete_from_backup(old_backup: Path):
        old_backup.unlink()

    def _set_year_directory(self) -> Path:
        current_year = datetime.now().strftime("%Y")
        year_directory = self._archive_path / Path(current_year)

        #Search existing years in archive
        if not year_directory.exists():
            year_directory.mkdir(mode=0o700)

        return year_directory

    def do_archive(self):
        for old in self._expired_backups:
            if self.archive_enabled:
                logger.debug(f"Moving {old.name} into {self._archive_path}...")
                self._move_into_archive(old)
                logger.info(f"{old.name} has been moved to {self._archive_path.name}")
            else:
                logger.debug(f"Deleting {old.name} from {self._archive_path}")
                self._delete_from_backup(old)
                logger.info(f"{old.name} has beed removed")