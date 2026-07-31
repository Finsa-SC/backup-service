from pathlib import Path
from backuper_app.utils import get_logger

logger = get_logger(__name__)

class Archive:
    def __init__(self, oldest_backup: list[Path], archive_path: Path = None, archive_enable: bool = False):
        self._archive_path = archive_path
        self._oldest_backup = oldest_backup
        self.archive_enable = archive_enable

    def _move_into_archive(self, old_backup: Path):
        old_backup.move_into(self._archive_path)

    @staticmethod
    def _delete_from_backup(old_backup: Path):
        old_backup.unlink()

    def do_archive(self):
        for old in self._oldest_backup:
            if self.archive_enable:
                logger.debug(f"Moving {old.name} into {self._archive_path}...")
                self._move_into_archive(old)
                logger.info(f"{old.name} has been moved to {self._archive_path.name}")
            else:
                logger.debug(f"Deleting {old.name} from {self._archive_path}")
                self._delete_from_backup(old)
                logger.info(f"{old.name} has beed removed from {self._archive_path.name}")

