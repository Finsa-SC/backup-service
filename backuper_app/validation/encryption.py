from pathlib import Path
from backuper_app.exception import BackuperError, EncryptionError

def validate_master_key(key_path) -> None:
    if not Path(key_path).exists():
        raise BackuperError("Master key path is invalid")

def validate_encryption_version(version: int) -> None:
    version_list = (1, )
    if version not in version_list:
        raise EncryptionError("Unsupported encryption version")

def validate_encrypted_file_not_malformed(enc_file_path) -> None:
    min_encrypted_size = 12 + 16

    if enc_file_path.stat().st_size < min_encrypted_size:
        raise EncryptionError("Malformed encryption domain")
