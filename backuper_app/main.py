import argparse
from pathlib import Path
from backuper_app.backup.backuper import Backuper
from backuper_app.config.config import Config
from backuper_app.utils import get_logger

logger = get_logger(__name__)

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

    def load_config(self, argsv):
        config_path = Path(argsv.config)
        backup_config = Config(config_path)
        self.config = backup_config.set_config()

    def run(self):
        backuper = Backuper(
            target_path=self.config.target,
            destination_path=self.config.destination,
            backup_name=self.config.backup_name
        )
        backuper.do_backup()

def main():
    try:
        logger.info("Starting backup service...")

        backup_service = BackupService()
        args =  backup_service.get_config()
        backup_service.load_config(args)
        backup_service.run()

        logger.info("Target has been backup!")
    except Exception as e:
        logger.error(e)

if __name__ == "__main__":
    main()