import argparse
from pathlib import Path
from backuper_app.backup import Backuper, Retention, Archive
from backuper_app.backup.restore import Restore
from backuper_app.config import Config
from backuper_app.utils import get_logger

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
            help="Create new backup",
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
            help="Extract archive backup",
            description="Extract archive backup",
        )

        restore_mode.add_argument(
            "--file",
            type=Path,
            default=None,
            help="File path you want to restore",
        )

        restore_mode.add_argument(
            "--date",
            type=str,
            default=None,
            help="Date archive you want to restore(require --archive-path)",
        )

        restore_mode.add_argument(
            "--destination",
            type=Path,
            default=Path("/tmp/backup_restore"),
            help="Path to extract directory destination you want, default is /tmp/backup_restore"
        )

        restore_mode.add_argument(
            "--archive-path",
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

        backup_path = backuper.do_backup()

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

    @staticmethod
    def run_restore(**kwargs):
        restore = Restore(
            file_path=kwargs['file_path'],
            date=kwargs['date'],
            extract_path=kwargs['extract_path'],
            archive_path=kwargs["archive_path"],
        )
        restore.do_restore()

def main():
    try:
        backup_service = BackupService()

        args =  backup_service.get_config()

        match args.command:
            case "backup":
                logger.info("Starting backup service...")

                config = backup_service.load_config(args)
                backup_service.run_backup(config)

                logger.info("Target has been backup!")
            case "restore":
                if args.file and args.date:
                    raise ValueError("Unexpected argument, choose one format(file/date)")

                if args.date and not args.archive_path:
                    raise ValueError("Missing --archive-path flag to use --date")

                logger.info(f"Restoring {args.file or args.date}...")
                backup_service.run_restore(
                    file_path=args.file,
                    date=args.date,
                    extract_path=args.destination,
                    archive_path=args.archive_path,
                )
                logger.info("Restore completed.")

    except Exception as e:
        logger.error(e)

if __name__ == "__main__":
    main()