from pathlib import Path
from backuper_app.utils import get_logger, get_archive_glob

logger = get_logger(__name__)

class Retention:
    def __init__(self, destination: Path, backup_name: str, keep_last: int):
        self._destination: Path = destination
        self._backup_name = backup_name
        self._keep_last = keep_last

    def should_delete_backup(self, backups: list[Path]) -> bool:
        return len(backups) > self._keep_last

    def get_should_delete(self, oldest_backups: list[Path]):
        expired_backups = []
        oldest_backups = [backup for backup in oldest_backups if backup.suffix != ".sha256"]
        while self.should_delete_backup(oldest_backups):
            oldest_backup = oldest_backups.pop(0)
            expired_backups.append(oldest_backup)

            backup_checksum = oldest_backup.with_suffix(oldest_backup.suffix + ".sha256")
            if backup_checksum.is_file():
                expired_backups.append(backup_checksum)

        return expired_backups

    def do_retention(self):
        expired_backups = get_archive_glob(self._destination, self._backup_name)
        should_delete = self.get_should_delete(expired_backups)

        return should_delete


if __name__ == "__main__":
    retention = Retention(Path("/home/silence-suzuka/backup_test"), "playground", 7)
    # print(get_archive_glob())
