import logging, sys, subprocess, datetime
from pathlib import Path

logging.basicConfig(
    format="[%(levelname)s] %(asctime)s: %(message)s",
    level=logging.DEBUG,
    stream=sys.stdout,
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

class Backuper:
    def __init__(self, target_path, destination_path, backup_name=None):
        self.target_path = Path(target_path)
        self.destination_path = Path(destination_path)

        if not backup_name:
            self.backup_name = self.target_path.name
        else:
            self.backup_name = backup_name

    @staticmethod
    def path_exists(path: Path) -> bool:
        return path.exists()

    @staticmethod
    def set_backup_name(backup_name: str) -> str:
        return f"{backup_name}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"

    def do_backup(self):
        logger.info("Creating archive...")
        backup_name = self.set_backup_name(self.backup_name)
        archive_path = self.destination_path / f"{backup_name}.tar.zst"
        str_command = [
            "tar",
            "--zstd",
            "-cf",
            str(archive_path),
            f"{self.target_path}"
        ]
        result = subprocess.run(
            str_command,
            shell=False,
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            raise Exception(result.stderr)
        else:
            logger.info(result.stdout)

    def start_backup(self):
        logger.info("Starting backup service...")

        #Validate path
        if not self.path_exists(self.target_path):
            raise FileNotFoundError(f"Target path not found for {self.target_path}")

        if not self.path_exists(self.destination_path):
            raise FileNotFoundError(f"Destination path not found for {self.destination_path}")

        self.do_backup()

        logger.info(f"Backup for {self.target_path.name} success with no error found.")

if __name__ == "__main__":
    try:
        backuper = Backuper(target_path="/home/silence-suzuka/Project/File_Backuper", destination_path="/home/silence-suzuka/Project/")
        backuper.start_backup()
    except Exception as e:
        logger.error(e)
