import argparse
from importlib.metadata import version
from pathlib import Path
from backuper_app.utils import get_logger, format_size
from backuper_app.config import Config
from backuper_app.backup import Retention, Archive, Backuper, Restore, Verify, Initializer

logger = get_logger(__name__)
VERSION = version("file-backuper")

def get_config():
    parser = argparse.ArgumentParser(
        prog="backuper",
        description="Backup Service",
    )

    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"%(prog)s {VERSION}"
    )

    subparser = parser.add_subparsers(
        dest="command",
        required=True,
    )

    ### Backup Mode
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

    ### Restore Mode
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

    ### Verify
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

    ### Init
    init_mode = subparser.add_parser(
        name="init",
        help="Create an initial configuration file",
        description="Create an initial configuration file from the default template.",
    )
    init_mode.add_argument(
        "config",
        type=Path,
        nargs="?",
        default=None,
        help="Path to the configuration file (default: /etc/backuper/config.toml).",
    )
    init_mode.add_argument(
        "-t",
        "--target",
        type=Path,
        default=None,
        help="Path to the backup target directory.",
    )
    init_mode.add_argument(
        "-d",
        "--destination",
        type=Path,
        default=None,
        help="Path to the backup destination directory.",
    )
    init_mode.add_argument(
        "-r",
        "--retention",
        type=int,
        default=None,
        help="Number of backups to retain.",
    )
    init_mode.add_argument(
        "-c",
        "--compression",
        choices=["gzip", "zstd"],
        default="zstd",
        help="Compression method.",
    )

    init_mode.add_argument(
        "-l",
        "--link-mode",
        choices=["ignore", "follow", "preserve"],
        default="preserve",
        help="How symbolic links are handled.",
    )

    return parser.parse_args()

def load_config(argsv):
    config_path = Path(argsv.config)
    backup_config = Config(config_path)
    return backup_config.set_config()


def _valid_input_archive(file: Path | None, date: str | None, archive_path: Path | None):
    if file and date:
        raise ValueError("Unexpected argument, choose one format(file/date)")

    if date and not archive_path:
        raise ValueError("Missing --archive-path flag to use --date")

    return True

def run_backup(request):
    from backuper_app.utils.checksum import make_hash

    config = load_config(get_config())

    if not request.dry_run:
        logger.info(f"Starting backup service for {config.backup_name}")
        logger.info(f"Source: {config.target}")
        logger.info(f"Destination: {config.destination}")
        logger.info(f"Compression: {config.compression}")

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
        dry_run=request.dry_run,
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

def run_restore(request):
    from backuper_app.utils.checksum import validate_checksum

    target = request.file_path or request.date
    logger.info(f"Verifying {target}")
    file_path = request.file_path
    date = request.date
    destination = request.destination
    archive_path = request.archive_path

    if _valid_input_archive(file_path, date, archive_path=archive_path):
        logger.info(f"Restoring {file_path or date}...")

        validate_checksum(file_path)

        restore = Restore(
            file_path=file_path,
            date=request.date,
            extract_path=destination,
            archive_path=archive_path,
        )
        restore.do_restore()

        logger.info("Restore completed.")


def run_verify(request):
    if _valid_input_archive(file=request.file_path, date=request.date, archive_path=request.archive_path):
        target = request.file_path or request.date
        verify = Verify(
            file_path=request.file_path,
            date=request.date,
            archive_path=request.archive_path,
        )
        is_valid = verify.do_verify()
        if is_valid:
            logger.info(f"Archive verification passed for {target}")

def run_init(request):
    init = Initializer(
        request.config,
        request.target,
        request.destination,
        request.retention,
        request.compression,
        request.link_mode,
    )

    config_path = init.make_init()
    logger.info(f"Initial config has been created: {config_path}")
    logger.info("Edit the file before running `backuper backup`.")