from pathlib import Path
from backuper_app.backup.encryption import Encryption, is_encrypted_file
from backuper_app.utils import get_archive_by_date, get_archive_by_path, validate_checksum, is_checksum_file, resolve_checksum_path
from backuper_app.exception import InvalidArgumetError, BackuperError

class Verify:
    def __init__(self, file_path: Path, key_path: Path|None = None):
        self.file_path = file_path
        self.key_path = key_path

    def do_verify(self) -> bool:
        # Decrypt file if file is encrypted)
        if is_encrypted_file(self.file_path) and not self.key_path:
            raise InvalidArgumetError("Backup is encrypted but missing --key-path argument to open backup")

        parent_path = self.file_path.parent
        try:
            if is_encrypted_file(self.file_path):
                checksum_path = resolve_checksum_path(self.file_path, parent_path)
                validate_checksum(file_path=self.file_path)
            else:
                validate_checksum(file_path=self.file_path)
        except BackuperError as e:
            if self.file_path:
                self.file_path.unlink(missing_ok=True)
            raise BackuperError(e)

        return True