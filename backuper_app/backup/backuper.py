import subprocess, datetime
from pathlib import Path
from backuper_app.utils import get_logger

logger = get_logger(__name__)

class Backuper:
    def __init__(self, target_path, destination_path, backup_name=None):
        self.target_path = Path(target_path)
        self.destination_path = Path(destination_path)
        self.backup_name = backup_name or self.target_path.name

    @staticmethod
    def path_exists(path: Path) -> bool:
        return path.exists()

    @staticmethod
    def set_backup_name(backup_name: str) -> str:
        return f"{backup_name}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"

    def compress(self):
        logger.info(f"Creating archive for {self.target_path.name}...")
        backup_name = self.set_backup_name(self.backup_name)
        archive_path = self.destination_path / f"{backup_name}.tar.zst"
        parent_path = self.target_path.parent
        str_command = [
            "tar",
            "--zstd",
            "-C",
            str(parent_path),
            "-cf",
            str(archive_path),
            f"{self.target_path.name}"
        ]
        result = subprocess.run(
            str_command,
            shell=False,
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            raise RuntimeError(result.stderr)
        else:
            logger.info(f"Archive created: {archive_path}")

    def do_backup(self):
        #Validate path
        logger.debug(f"Validate path for {self.target_path}")
        if not self.path_exists(self.target_path):
            raise FileNotFoundError(f"Target path not found for {self.target_path}")

        logger.debug(f"Validate path for {self.destination_path}")
        if not self.path_exists(self.destination_path):
            raise FileNotFoundError(f"Destination path not found for {self.destination_path}")

        self.compress()

        logger.info(f"Backup for {self.target_path.name} success with no error found.")

if __name__ == "__main__":
    try:
        backuper = Backuper(target_path="/", destination_path="/home/silence-suzuka/backup_test", backup_name="My_Backup")
        backuper.do_backup()
    except Exception as e:
        logger.error(e)
