import logging, sys
from pathlib import Path

logging.basicConfig(
    format="[%(levelname)s] %(asctime)s: %(message)s",
    level=logging.DEBUG,
    stream=sys.stdout,
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

class Backuper:
    def __init__(self, target_path, destination_path):
        self.target_path = Path(target_path)
        self.destination_path = Path(destination_path)

    @staticmethod
    def path_exists(path: Path) -> bool:
        return path.exists()

    def start_backup(self):
        logger.info("Starting backup service...")

        #Validate path
        if not self.path_exists(self.target_path):
            raise FileNotFoundError(f"Target path not found for {self.target_path}")

        if not self.path_exists(self.destination_path):
            raise FileNotFoundError(f"Destination path not found for {self.destination_path}")

        logger.info("All path exists.")

if __name__ == "__main__":
    try:

        backuper = Backuper(target_path="/home/silence-suzuka/Project/File_Backuper", destination_path="/home/silence-suzuka/Project/")
        backuper.start_backup()
    except Exception as e:
        logger.error(e)
