import tomllib, logging, sys, argparse
from pathlib import Path
from backuper import Backuper
from config import Config

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

    def load_config(self, args):
        config_path = Path(args.config)
        backup_config = Config(config_path)
        self.config = backup_config.set_config()

    def run(self):

        backuper = Backuper(
            target_path=self.config.target,
            destination_path=self.config.destination,
            backup_name=self.config.backup_name
        )
        backuper.do_backup()

if __name__ == "__main__":
    try:
        logger.info("Starting backup service...")

        backup_service = BackupService()
        args =  backup_service.get_config()
        backup_service.load_config(args)
        backup_service.run()

        logger.info("Target has been backup!")
    except Exception as e:
        logger.error(e)
