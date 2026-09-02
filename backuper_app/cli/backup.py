from backuper_app.application.backup import Backuper
from backuper_app.application.verify import verify_backup
from .parser import load_config, get_arg_parse
from backuper_app.domain import Encryption, RemoteBackup, Archive, Retention
from backuper_app.dto import BackupPlan, RemoteConfig
from backuper_app.infrastructure import TemporaryWorkspace, get_logger, format_size
from backuper_app.validation import validate_archive

logger = get_logger(__name__)

def run_backup(dry_run: bool, workspace: TemporaryWorkspace):
    from backuper_app.infrastructure import make_hash

    config_path = get_arg_parse()
    config = load_config(config_path.config)

    validate_archive(config.archive_path, config.archive_enabled, keep_last=config.keep_last)

    if not dry_run:
        logger.info(f"Starting backup service for {config.backup_name}")
        logger.info(f"Source: {config.target}")
        logger.info(f"Destination: {config.destination}")
        logger.info(f"Compression: {config.compression}")

    parent_path = config.target.parent

    # Set remote config
    remote_config = RemoteConfig(
        enabled=config.remote_enabled,
        host=config.remote_host,
        user=config.remote_user,
        port=config.remote_port,
        identity_file=config.identity_file,
        alias=config.alias,
        remote_path=config.remote_path
    )

    backup_plan = BackupPlan(
        target_path=config.target,
        destination_path=config.destination,
        parent_path=parent_path,
        backup_name=config.backup_name,
        compression_type=config.compression,

        include=config.include,
        exclude=config.exclude,

        link_mode=config.link_mode,
        dry_run=dry_run,

        retention=config.keep_last,
        archive_enabled=config.archive_enabled,
        archive_path=config.archive_path,

        encryption_enabled=config.encryption_enabled,

        remote_config=remote_config
    )

    backuper = Backuper(
        backup_plan,
        workspace
    )

    # Init encryption here to validate key path before backuping
    encryption = None
    if config.encryption_enabled:
        encryption = Encryption(config.key_path)

    backup_path = backuper.do_backup()
    logger.info(f"Backup created: {backup_path.name} {format_size(backup_path.lstat().st_size)}")

    # Encrypt domain except checksum file
    if encryption:
        encrypted_file_path = encryption.encrypt_file(backup_path)
        logger.info(f"Backup has been encrypted to {encrypted_file_path.name}")
        backup_path = encrypted_file_path

    checksum_path = make_hash(backup_path)
    logger.info(f"Checksum generated: {checksum_path.name}")

    if config.file_mode:
        backup_path.chmod(mode=config.file_mode)
        logger.info(f"Backup mode has been changed to {oct(config.file_mode)}")

    # Validating checksum
    logger.info(f"Validating checksum...")
    verify_backup(backup_path, config.key_path)
    logger.info(f"Checkum is valid.")

    # Do remote domain if enabled
    if config.remote_enabled:
        will_send_remote = [checksum_path, backup_path]

        remote = RemoteBackup(
            backup_list=will_send_remote,
            remote_config=remote_config
        )
        remote.do_remote()

    # Do retention if enabled
    if config.keep_last:
        backup_retention = Retention(
            destination=config.destination,
            backup_name=config.backup_name,
            keep_last=config.keep_last,
        )
        should_delete = backup_retention.do_retention()

        if should_delete:
            logger.info(f"Rotating old backups (keeping last {config.keep_last})...")

            backup_archive = Archive(
                expired_backups=should_delete,
                archive_path=config.archive_path,
                archive_enabled=config.archive_enabled,
            )
            backup_archive.do_archive()