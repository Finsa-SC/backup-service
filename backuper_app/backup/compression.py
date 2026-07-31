from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class CompressionType:
    compress_flag: str
    extract_flag: str
    suffix: str

def resolve_compression_from_config(commpression_type: str):
    return COMPRESSION[commpression_type]

def _get_compression_type(suffix: str) -> str:
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