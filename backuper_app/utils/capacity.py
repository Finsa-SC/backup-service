import shutil
from pathlib import Path

def format_size(size: float) -> str:
    units = [
        "B",
        "KiB",
        "MiB",
        "GiB",
        "TiB",
    ]

    byte = 1024
    unit_index = 0
    while size >= byte:
        size /= byte
        unit_index += 1

    return f"{size} {units[unit_index]}"

def get_space_info(path: Path) -> dict[str, int]:
    space_info = shutil.disk_usage(path)
    return dict(
        space_available=space_info.free,
        space_used=space_info.used,
        space_total=space_info.total,
    )

def analyze_estimate_size(files: list[Path]) -> float:
    size = 0
    for file in files:
        if not file.is_dir():
            size += file.lstat().st_size

    return size

def is_enough_space(required: float, space_available: float) -> bool:
    return required >= space_available