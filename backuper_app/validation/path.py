from backuper_app.exception import BackuperError, ConfigurationError
from pathlib import Path

def validate_path(*args: Path|None) -> None:
    if not args:
        raise BackuperError("validate_path required minimal one path")

    for path in args:
        path = string_to_path(path)
        if not path.exists():
            raise BackuperError(f"Path not found for {path}")

def string_to_path(obj_path) -> Path:
    if isinstance(obj_path, str):
        return Path(obj_path)
    elif isinstance(obj_path, Path):
        return obj_path
    raise BackuperError(f"Invalid type for path: {obj_path}, got type {type(obj_path)}")

def get_validate_config_path(hint: str, path) -> Path:
    if not path.strip():
        raise ConfigurationError(f"{hint} path is not set, make sure the target path is configured in your config")

    path = Path(path).expanduser()
    if not path.exists():
        raise BackuperError(f"{hint} path not found: {path}")

    return path