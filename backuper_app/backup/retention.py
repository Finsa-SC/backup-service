from pathlib import Path

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

    def is_beyond_keep_last(self, backups: list[Path]) -> bool:
        return len(backups) > self._keep_last

    @staticmethod
    def remove_oldest(oldest_backup: Path):
        oldest_backup.unlink()

    def do_retention(self):
        backups = self.get_backup_glob()
        if self.is_beyond_keep_last(backups):
            self.remove_oldest(backups[0])

if __name__ == "__main__":
    retention = Retention(Path("/home/silence-suzuka/backup_test"), "playground", 7)
    print(retention.get_backup_glob())
