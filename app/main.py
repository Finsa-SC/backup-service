import tomllib, logging, sys, argparse
from pathlib import Path
from backuper import Backuper

# Set logging
logging.basicConfig(
    format="[%(levelname)s] %(asctime)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    stream=sys.stdout,
    level=logging.DEBUG,
)
logger = logging.getLogger(__name__)


class BackupService:
    def __init__(self):
        self.config = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            logger.info(exc_val)
        return False

    @staticmethod
    def get_config():
        parser = argparse.ArgumentParser(description="Backup Service")
        parser.add_argument(
            "--config",
            required=True,
            help="Path to Configuration target",
        )
        return parser.parse_args()

    def load_config(self):
        args = self.get_config()
        config_path = Path(args.config)
        try:
            with open(config_path, "rb") as file:
                self.config = tomllib.load(file)
        except FileNotFoundError as er:
            raise FileNotFoundError(f"Configuration file not found: {args.config}") from er

    def run(self):
        self.get_config()
        self.load_config()
        backup = self.config.get("backup")
        target_backup = backup.get("target", None)
        destination = backup.get("destination", None)
        backup_name = backup.get("backup_name", None)

        backuper = Backuper(target_path=target_backup, destination_path=destination, backup_name=backup_name)
        backuper.do_backup()

if __name__ == "__main__":
    try:
        logger.info("Starting backup service...")
        backup_service = BackupService()
        backup_service.run()
        logger.info("Target has been backup!")
    except Exception as e:
        logger.error(e)
