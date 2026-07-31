from dataclasses import dataclass

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