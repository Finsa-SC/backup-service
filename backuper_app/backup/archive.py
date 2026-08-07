from pathlib import Path
from backuper_app.utils import get_logger
from datetime import datetime

logger = get_logger(__name__)

class Archive:
    def __init__(self, expired_backups: list[Path], archive_path: Path = None, archive_enabled: bool = False):
        self._archive_path = archive_path
        self._expired_backups = expired_backups
        self.archive_enabled = archive_enabled

    @staticmethod
    def _move_into_archive(old_backup: Path, archive_target: Path):
        old_backup.move_into(archive_target)

    @staticmethod
    def _delete_from_backup(old_backup: Path):
        old_backup.unlink()

    def _set_year_directory(self) -> Path:
        current_year = datetime.now().strftime("%Y")
        year_directory = self._archive_path / current_year

        #Search existing years in archive
        if not year_directory.exists():
            logger.debug(f"No archive for {current_year}, Creating one...")
            year_directory.mkdir(mode=0o700, parents=True, exist_ok=True)

        return year_directory

    @staticmethod
    def _set_month_directory(year_dir_path) -> Path:
        current_month = datetime.now().strftime("%b")
        month_directory = year_dir_path / current_month

        if not month_directory.exists():
            logger.debug(f"{current_month} archive directory not found, Creating one...")
            month_directory.mkdir(mode=0o700, parents=True, exist_ok=True)

        return month_directory

    @staticmethod
    def is_checksum_file(file: Path) -> bool:
        return ".sha256" in file.suffixes

    def do_archive(self):
        archive_target = self._set_month_directory(self._set_year_directory())

        backup_removed: int = 0
        for old in self._expired_backups:
            if self.archive_enabled:
                logger.debug(f"Moving {old.name} into {self._archive_path}...")
                self._move_into_archive(old_backup=old, archive_target=archive_target)
            else:
                logger.debug(f"Deleting {old.stem} from {self._archive_path}")
                self._delete_from_backup(old_backup=old)

            if not self.is_checksum_file(old):
                logger.info(f"Removed old backup: {old.name} (expired)")
                backup_removed += 1

        logger.info(f"Backup rotation completed: {backup_removed} backups retained.")