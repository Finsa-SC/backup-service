from backuper_app.application.restore import Restore
from backuper_app.application.verify import verify_backup
from backuper_app.domain import is_encrypted_file, Encryption
from backuper_app.exception import InvalidArgumetError
from backuper_app.infrastructure import get_file_by_path_or_date, get_logger
from backuper_app.validation import validate_master_key, is_valid_input_archive

logger = get_logger(__name__)

def run_restore(
        request,
        workspace
):
    target = request.file_path or request.date
    logger.info(f"Verifying {target}")
    file_path = request.file_path
    date = request.date
    destination = request.destination
    archive_path = request.archive_path
    key_path = request.key_path

    if is_valid_input_archive(file_path, date, archive_path=archive_path):
        # Resolve file from path or date
        archive_file = get_file_by_path_or_date(file_path, date=date, archive_path=archive_path)

        # If encrypted domain but missing key path argument
        if is_encrypted_file(archive_file) and not key_path:
            raise InvalidArgumetError("Backup is encrypted but missing --key-path argument to open domain")

        # If encrypted domain
        elif is_encrypted_file(archive_file):
            validate_master_key(key_path)

            encryption = Encryption(key_path)

            verify_backup(archive_file, key_path)

            archive_file = encryption.decrypt_file(archive_file, workspace)
            logger.info(f"Backup decrypted to {archive_file}")

        # If normal domain
        else:
            verify_backup(archive_file)

        logger.info(f"Restoring {archive_file}...")
        restore = Restore(
            file_path=archive_file,
            extract_path=destination,
            archive_path=archive_path
        )

        logger.info(f"Extracting {archive_file}...")
        extract_path = restore.do_restore()
        logger.info(f"{archive_file.name} has been extract to {extract_path}")

        logger.info("Restore completed.")

        logger.debug("Cleaning up temporary encrypted compress file")
        archive_file.unlink(missing_ok=True)