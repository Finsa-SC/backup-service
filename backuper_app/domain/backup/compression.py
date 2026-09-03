import subprocess
from dataclasses import dataclass
from pathlib import Path
from backuper_app.validation import validate_compression
from backuper_app.validation.path import get_relative_path_list

@dataclass(frozen=True)
class CompressionType:
    compress_flag: str
    extract_flag: str
    suffix: str

COMPRESSION = {
    "zstd": CompressionType(
        compress_flag="--zstd",
        extract_flag="--zstd",
        suffix="zst"
    ),
    "gzip": CompressionType(
        compress_flag="-z",
        extract_flag="-z",
        suffix="gz"
    ),
}

def resolve_compression_from_config(compression_type: str):
    compression = COMPRESSION.get(compression_type, None)

    validate_compression(compression, compression_type)

    return compression

def _get_compression_type(suffix: str) -> str:
    suffix = suffix.replace(".", "")
    match suffix:
        case "zst":
            return "zstd"
        case "gz":
            return "gzip"
        case _:
            raise SystemExit(f"No compression format found for {suffix}")

def resolve_compression_from_suffix(compressed_file: Path) -> CompressionType:
    suffix = compressed_file.suffix
    return COMPRESSION[_get_compression_type(suffix)]

def compress(
        compression,
        backup_path: Path,
        backup_list: list[Path],
        workspace_path: Path,
        parent_path: Path,
        manifest_relative_path: Path,
) -> Path:
    str_command = [
        "tar",
        compression.compress_flag,
        "--no-recursion",
        "-cf",
        str(backup_path),
        "-C",
        str(parent_path),
    ]

    relative_backup = get_relative_path_list(parent_path, backup_list)
    str_command.extend(relative_backup)

    # Insert manifest into compression command
    manifest_command = [
        "-C",
        str(workspace_path),
        str(manifest_relative_path),
    ]
    str_command.extend(manifest_command)

    result = subprocess.run(
        str_command,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        backup_path.unlink(missing_ok=True)
        raise ChildProcessError(result.stderr)
    else:
        return backup_path
