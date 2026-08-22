from datetime import datetime
from backuper_app.utils import get_logger, configure_logging
from backuper_app.exception import BackuperError, InvalidArgumetError
from backuper_app.cli import run_backup, run_restore, run_verify, get_config, run_init
from backuper_app.dto import RestoreRequest, VerifyRequest, InitRequest

logger = get_logger(__name__)

def main():
    # Init logging format and policy
    configure_logging()

    try:
        start_time = datetime.now()
        argv = get_config()

        match argv.command:
            case "backup":
                run_backup(argv.dry_run)

            case "restore":
                request = RestoreRequest(
                    file_path=argv.file,
                    date=argv.date,
                    destination=argv.destination,
                    archive_path=argv.archive_path,
                    key_path=argv.key_path,
                )
                run_restore(request)

            case "verify":
                request = VerifyRequest(
                    file_path=argv.file,
                    date=argv.date,
                    archive_path=argv.archive_path,
                    key_path=argv.key_path,
                )
                run_verify(request)

            case "init":
                request = InitRequest(
                    config=argv.config,
                    target=argv.target_path,
                    destination=argv.destination,
                    retention=argv.retention,
                    compression=argv.compression,
                    link_mode=argv.link_mode,
                    archive_path=argv.archive_path,
                    key_path=argv.key_path,
                    remote_host=argv.remote_host,
                    remote_user=argv.remote_user,
                    remote_port=argv.remote_port,
                    remote_identity_file=argv.remote_identity_file,
                    remote_path=argv.remote_path,
                    remote_alias=argv.remote_alias,
                )
                run_init(request)
            case _:
                raise InvalidArgumetError(f"Invalid command {argv.command}")

        backup_time = datetime.now() - start_time
        logger.info(f"Backuper completed successfully in {backup_time.total_seconds():.2f} seconds.")

    except BackuperError as e:
        logger.error(e)
        raise SystemExit(1)
    except Exception as e:
        logger.exception(e)
        raise SystemExit(1)

if __name__ == "__main__":
    main()
