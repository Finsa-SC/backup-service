from pathlib import Path
from backuper_app.utils import get_logger

logger = get_logger(__name__)

class Archive:
    def __init__(self, archive_path: Path, oldest_backup: Path):
        self._archive_path = archive_path
        self._oldest_backup = oldest_backup

    def _move_into_archive(self):
        self._oldest_backup.move_into(self._archive_path)

    def do_archive(self):
        logger.debug(f"Moving {self._oldest_backup.name} into {self._archive_path}...")
        self._move_into_archive()
        logger.debug(f"{self._oldest_backup} has been moved to {self._archive_path}")