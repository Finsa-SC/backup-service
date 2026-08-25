from backuper_app.exception import BackuperError
from pathlib import Path

def validate_path(*args: Path) -> None:
    if not args:
        raise BackuperError("validate_path required minimal one path")

    for path in args:
        if not path.exists():
            raise BackuperError(f"Path not found for {path}")