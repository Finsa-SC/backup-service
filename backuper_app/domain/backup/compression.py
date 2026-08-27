from dataclasses import dataclass
from pathlib import Path
from backuper_app.validation import validate_compression

@dataclass(frozen=True)
class CompressionType:
    compress_flag: str
    extract_flag: str
    suffix: str

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