from pathlib import Path
from backuper_app.utils import get_logger

logger = get_logger(__name__)

class Retention:
    def __init__(self, destination: Path, backup_name: str, keep_last: int):
        self._destination: Path = destination
        self._backup_name = backup_name
        self._keep_last = keep_last

    def get_backup_glob(self) -> list[Path]:
        path_list = list(
            self._destination.glob(f"{self._backup_name}*")
        )
        backups_list = [backup for backup in path_list if not str(backup).endswith(".sha256")]

        backups_list.sort(key=lambda backup: backup.name)
        return backups_list

    def should_delete_backup(self, backups: list[Path]) -> bool:
        return len(backups) > self._keep_last

    def get_should_delete(self, oldest_backups: list[Path]):
        expired_backups = []
        while self.should_delete_backup(oldest_backups):
            oldest_backup = oldest_backups.pop(0)
            expired_backups.append(oldest_backup)

            backup_checksum = oldest_backup.with_name(oldest_backup.name + ".sha256")
            if backup_checksum.is_file():
                expired_backups.append(backup_checksum)

        return expired_backups

    def do_retention(self):
        expired_backups = self.get_backup_glob()
        should_delete = self.get_should_delete(expired_backups)

        return should_delete


if __name__ == "__main__":
    retention = Retention(Path("/home/silence-suzuka/backup_test"), "playground", 7)
    print(retention.get_backup_glob())
