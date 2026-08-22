from pathlib import Path
from backuper_app.backup.encryption import is_encrypted_file
from backuper_app.utils import validate_checksum
from backuper_app.exception import InvalidArgumetError, BackuperError

def verify_backup(file_path: Path, key_path: Path|None = None) -> bool:
    if is_encrypted_file(file_path) and not key_path:
        raise InvalidArgumetError("Backup is encrypted but missing --key-path argument to open backup")

    validate_checksum(file_path=file_path)

    return True