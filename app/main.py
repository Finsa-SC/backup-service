import tomllib, logging, sys
from pathlib import Path
from backuper import Backuper

logging.basicConfig(
    format="[%(levelname)s] %(asctime)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    stream=sys.stdout,
    level=logging.DEBUG,
)
logger = logging.getLogger(__name__)

current_directory = Path(__file__).resolve().parents[1]
with open(current_directory / "config.toml", "rb") as file:
    config = tomllib.load(file)

class BackupService:
    def __init__(self):
        ...

    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            logger.info(exc_val)
        return True

    def backup_target(self, item):
        target_backup = item.get("target", None)
        destination = item.get("destination", None)
        backup_name = item.get("backup_name", None)

        backuper = Backuper(target_path=target_backup, destination_path=destination, backup_name=backup_name)
        backuper.do_backup()

    def run(self):
        for item in config["backup"]:
            self.backup_target(item)

if __name__ == "__main__":
    try:
        logger.info("Starting backup service...")
        backup = BackupService()
        backup.run()
        logger.info("All target has been backup!")
    except Exception as e:
        logger.error(e)
