import argparse
from datetime import datetime
from pathlib import Path
from backuper_app.backup import Backuper, Retention, Archive, Verify
from backuper_app.backup.restore import Restore
from backuper_app.config import Config
from backuper_app.utils import get_logger, format_size
from backuper_app.exception import BackuperError

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
            type=Path,
            default=None,
            help="Path to Configuration target",
        )
        backup_mode.add_argument(
            "--dry-run",
            action="store_true",
            help="Trial without actually taking action"
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
            help="Path to extract directory destination you want, default is /tmp/backup_restore",
        )
        restore_mode.add_argument(
            "--archive-path",
            help="Path to your archive directory to find file to be extract",
        )

        verify_mode = subparser.add_parser(
            name="verify",
            help="verify backup data with checksum",
            description="verify backup data with checksum",
        )
        verify_mode.add_argument(
            "--file",
            type=Path,
            default=None,
            help="File path you want to verify",
        )
        verify_mode.add_argument(
            "--date",
            type=str,
            default=None,
            help="Date archive you want to verify(require --archive-path)",
        )
        verify_mode.add_argument(
            "--archive-path",
            type=Path,
            default=None,
            help="Path to your archive directory to find file to be verify",
        )

        return parser.parse_args()

    @staticmethod
    def load_config(argsv):
        config_path = Path(argsv.config)
        backup_config = Config(config_path)
        return backup_config.set_config()

    @staticmethod
    def run_backup(config, dry_run: bool):
        logger.info(f"Starting backup for {config.target.name}...")
        from backuper_app.utils.checksum import make_hash

        parent_path = config.target.parent

        backuper = Backuper(
            target_path=config.target,
            destination_path=config.destination,
            parent_path=parent_path,
            include=config.include,
            exclude=config.exclude,
            backup_name=config.backup_name,
            compression_type=config.compression,
            link_mode=config.link_mode,
            dry_run=dry_run,
            archive_enabled=config.archive_enable,
            archive_path=config.archive_path,
            retention=config.keep_last
        )

        backup_path = backuper.do_backup()
        logger.info(f"Backup created: {backup_path.name} {format_size(backup_path.lstat().st_size)}")

        checksum_path = make_hash(backup_path)
        logger.info(f"Checksum generated: {checksum_path.name}")

        #Check retention enabled
        if config.keep_last:
            logger.info(f"Rotating old backups (keeping last {config.keep_last})...")
            backup_retention = Retention(
                destination=config.destination,
                backup_name=config.backup_name,
                keep_last=config.keep_last,
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
        from backuper_app.utils.checksum import validate_checksum

        file_path = kwargs['file_path']

        validate_checksum(file_path)

        restore = Restore(
            file_path=file_path,
            date=kwargs['date'],
            extract_path=kwargs['extract_path'],
            archive_path=kwargs["archive_path"],
        )
        restore.do_restore()

def _valid_input_archive(file: Path | None, date: str | None, archive_path: Path | None):
    if file and date:
        raise ValueError("Unexpected argument, choose one format(file/date)")

    if date and not archive_path:
        raise ValueError("Missing --archive-path flag to use --date")

    return True

def main():
    try:
        start_time = datetime.now()
        backup_service = BackupService()

        args =  backup_service.get_config()

        match args.command:
            case "backup":
                config = backup_service.load_config(args)
                logger.info(f"Starting backup service for {config.backup_name}")
                logger.info(f"Source: {config.target}")
                logger.info(f"Destination: {config.destination}")
                logger.info(f"Compression: {config.compression}")
                backup_service.run_backup(config, args.dry_run)

            case "restore":
                if _valid_input_archive(file=args.file, date=args.date, archive_path=args.archive_path):
                    logger.info(f"Restoring {args.file or args.date}...")
                    backup_service.run_restore(
                        file_path=args.file,
                        date=args.date,
                        extract_path=args.destination,
                        archive_path=args.archive_path,
                    )
                    logger.info("Restore completed.")

            case "verify":
                if _valid_input_archive(file=args.file, date=args.date, archive_path=args.archive_path):
                    target = args.file or args.date
                    logger.info(f"Verifying {target}")
                    verify = Verify(
                        file_path=args.file,
                        date=args.date,
                        archive_path=args.archive_path,
                    )
                    is_valid = verify.do_verify()
                    if is_valid:
                        logger.info(f"Archive verification passed for {target}")
            case _:
                raise ValueError(f"Invalid command {args.command}")

        backup_time = datetime.now() - start_time
        logger.info(f"Backup completed successfully in {backup_time.total_seconds():.2f} seconds.")

    except BackuperError as e:
        logger.warning(e)
    except Exception as e:
        logger.error(e)

if __name__ == "__main__":
    main()