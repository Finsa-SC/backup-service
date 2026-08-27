from backuper_app.exception import InvalidArgumetError, ConfigurationError
from pathlib import Path

def is_valid_input_archive(file: Path | None, date: str | None, archive_path: Path | None) -> bool:
    if file and date:
        raise InvalidArgumetError("Unexpected argument, choose one format(file/date)")

    if date and not archive_path:
        raise InvalidArgumetError("Missing --archive-path flag to use --date")

    return True

def validate_archive(archive_path: Path | None, archive_enable: bool, keep_last: int | None) -> None:
    if keep_last and not archive_enable:
        raise ConfigurationError(f"Keep last active but archive is {archive_enable}")
    if archive_enable and not archive_path:
        raise ConfigurationError(f"Archive is enabled but archive path is not set")
    if not keep_last and archive_enable:
        raise ConfigurationError(f"Archive is enabled but keep last is not set")