from pathlib import Path

from backuper_app.exception import ConfigurationError, BackuperError

PERMISSION_MODE = [
    "0", "1", "2", "3",
    "4", "5", "6", "7",
]

def get_validate_file_mode(mode) -> int | None:
    if not mode:
        return None

    if not isinstance(mode, str):
        raise ConfigurationError(f"Invalid file mode type: got {type(mode)}, expected 'str'")

    len_mode = len(mode)
    if not len_mode == 3:
        raise ConfigurationError(f"Invalid len of file mode: got {len_mode} len, expected 3 len")

    for perm in mode:
        if perm not in PERMISSION_MODE:
            raise ConfigurationError("Invalid permission got")

    try:
        return int(mode, 8)
    except Exception:
        raise ConfigurationError(f"Invalid permission, got {mode}. Expected like 640")


def get_validate_config_path(hint: str, path) -> Path:
    if not path.strip():
        raise ConfigurationError(f"{hint} path is not set, make sure the target path is configured in your config")

    path = Path(path)
    if not path.exists():
        raise BackuperError(f"{hint} path not found: {path}")

    return path