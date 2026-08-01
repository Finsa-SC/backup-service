import argparse
from pathlib import Path
from backup import Backuper, Retention, Archive
from config import Config
from utils import get_logger

logger = get_logger(__name__)

class BackupService:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            logger.info(exc_val)
        return False

    @staticmethod
    def get_config():
        parser = argparse.ArgumentParser(
            prog="backuper",
            description="Backup Service",
        )

        subparser = parser.add_subparsers(
            dest="command",
            required=True,
        )

        #Backup Mode
        backup_mode = subparser.add_parser(
            name="backup",
            description="Create new backup",
        )

        backup_mode.add_argument(
            "--config",
            required=True,
            help="Path to Configuration target",
        )

        #Restore Mode
        restore_mode = subparser.add_parser(
            name="restore",
            description="Extract archive backup",
        )

        restore_mode.add_argument(
            "--extract",
            required=True,
            help="Archive file path you want to extract or date format to find latest archive on a day(require --archive)",
        )

        restore_mode.add_argument(
            "--destination",
            type=Path,
            default=Path("/tmp/backup_restore"),
            help="Path to extract directory destination you want, default is /tmp/backup_restore"
        )

        restore_mode.add_argument(
            "--archive",
            help="Path to your archive directory to find file to be extract"
        )

        return parser.parse_args()

    @staticmethod
    def load_config(argsv):
        config_path = Path(argsv.config)
        backup_config = Config(config_path, )
        return backup_config.set_config()

    @staticmethod
    def run_backup(config):
        backuper = Backuper(
            target_path=config.target,
            destination_path=config.destination,
            backup_name=config.backup_name,
            compression_type=config.compression,
        )

        backuper.do_backup()

        if config.keep_last:
            backup_retention = Retention(
                destination=config.destination,
                backup_name=config.backup_name,
                keep_last=config.keep_last
            )
            should_delete = backup_retention.do_retention()

            backup_archive = Archive(
                expired_backups=should_delete,
                archive_path=config.archive_path,
                archive_enabled=config.archive_enable,
            )
            backup_archive.do_archive()

def main():
    try:
        backup_service = BackupService()
        logger.info("Starting backup service...")

        args =  backup_service.get_config()
        config = backup_service.load_config(args)
        backup_service.run_backup(config)

        logger.info("Target has been backup!")
    except Exception as e:
        logger.error(e)

if __name__ == "__main__":
    main()