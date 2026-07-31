from pathlib import Path
from backuper_app.utils import get_logger

logger = get_logger(__name__)

class Retention:
    def __init__(self, destination: Path, backup_name: str, keep_last: int):
        self._destination: Path = destination
        self._backup_name = backup_name
        self._keep_last = keep_last

    def get_backup_glob(self) -> list[Path]:
        backups_list = list(
            self._destination.glob(f"{self._backup_name}*")
        )
        backups_list.sort(key=lambda backup: backup.name)
        return backups_list

    def should_delete_backup(self, backups: list[Path]) -> bool:
        return len(backups) > self._keep_last

    @staticmethod
    def remove_oldest(oldest_backup: Path):
        oldest_backup.unlink()

    def do_retention(self):
        backups = self.get_backup_glob()
        while self.should_delete_backup(backups):
            oldest_backup = backups[0]
            backups.pop(0)
            self.remove_oldest(oldest_backup)
            logger.info(f"{oldest_backup.name} has been removed from {self._destination.name}")

if __name__ == "__main__":
    retention = Retention(Path("/home/silence-suzuka/backup_test"), "playground", 7)
    print(retention.get_backup_glob())
