from os import name

from backuper_app.exception import ChecksumNotFoundError, ChecksumMismatchError, BackuperError
from pathlib import Path
import hashlib

def make_file_checksum(path_file: Path, hashed_file: str) -> Path:
    checksum_path =  path_file.with_suffix(path_file.suffix + ".sha256")

    checksum_path.touch(mode=0o664, exist_ok=False)

    with checksum_path.open('w') as file:
        file.write(hashed_file)

    return checksum_path

def calculate_hash(file_path) -> str:
    with file_path.open('rb') as file:
        sha = hashlib.sha256()
        while True:
            byte = file.read(8096)

            if byte:
                sha.update(byte)
            else:
                break
        return sha.hexdigest()

def read_hash_from_checksum(checksum_path: Path):
    with checksum_path.open('r') as file:
        return file.read()

def make_hash(file_path: Path):
    if file_path.is_file():
            hashed_file = calculate_hash(file_path)

            return make_file_checksum(file_path, hashed_file)
    else:
        raise BackuperError(f"{file_path} not exist or it's not a file")

def is_checksum_file(path: Path) -> bool:
    return ".sha256" in path.suffixes

def resolve_checksum_path(file_path: Path, backup_path: Path|None=None) -> Path:
    if backup_path:
        checksum_name = file_path.name + ".sha256"
        checksum = backup_path / checksum_name
        return checksum
    return file_path.with_suffix(file_path.suffix + ".sha256")

#Return bool, expected and actual hash
def validate_checksum(file_path: Path, checksum_path: Path|None=None) -> None:
    if not checksum_path:
        checksum_path = file_path.with_suffix(file_path.suffix + ".sha256")

    #Validate checksum file
    if checksum_path and checksum_path.is_file():
        expected = read_hash_from_checksum(checksum_path)
    else:
        raise ChecksumNotFoundError(f"Checksum file not found for {checksum_path}")

    actual = calculate_hash(file_path)
    if expected != actual:
        raise ChecksumMismatchError(f"Checksum mismatch for {file_path.name}: expected {expected}, got {actual}")

if __name__ == "__main__":
    make_hash(Path("/home/silence-suzuka/backup_test/playground_20260731_182432.tar.zst"))