from pathlib import Path
import hashlib

def make_file_checksum(path_file: Path, hashed_file: str) -> Path:
    checksum_path =  path_file.with_name(path_file.name + ".sha256")

    checksum_path.touch(mode=0o664, exist_ok=False)

    with checksum_path.open('w') as file:
        file.write(hashed_file)

    return checksum_path

def get_hash(file_path) -> str:
    with file_path.open('rb') as file:
        sha = hashlib.sha256()
        while True:
            byte = file.read(8096)

            if byte:
                sha.update(byte)
            else:
                break
        return sha.hexdigest()

def make_hash(file_path: Path):
    if file_path.is_file():
            hashed_file = get_hash(file_path)

            return make_file_checksum(file_path, hashed_file)
    else:
        raise FileNotFoundError(f"{file_path} not exist or it's not a file")

def is_valid_checksum(file_path: Path, checksum_path: Path) -> bool:
    expected = get_hash(checksum_path)
    actual = get_hash(file_path)
    if expected == actual:
        return True
    else:
        raise ValueError(f"Checksum mismatch for {file_path.name}: expected {expected}, got {actual}")

if __name__ == "__main__":
    make_hash(Path("/home/silence-suzuka/backup_test/playground_20260731_182432.tar.zst"))