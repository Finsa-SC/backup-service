import tomllib
from pathlib import Path
from dataclasses import dataclass
from backuper_app.utils import get_logger
from backuper_app.exception import BackuperError, ConfigurationError

logger = get_logger(__name__)

@dataclass
class BackupConfig:
    target: Path
    destination: Path
    backup_name: str | None
    include: list[str] | None
    exclude: list[str] | None
    keep_last: int
    compression: str
    archive_enable: bool
    archive_path: Path
    encryption_enabled: bool
    key_path: Path
    link_mode: str = "follow"

class Config:
    def __init__(self, config_path: Path):
        self._config_path: Path = config_path

    def _get_config(self):
        logger.debug(f"Reading config from {self._config_path}")
        try:
            with self._config_path.open('rb') as file:
                return tomllib.load(file)
        except tomllib.TOMLDecodeError as e:
            raise ConfigurationError (
                f"Invalid TOML configuration in {self._config_path}: {e}"
            )

    @staticmethod
    def _set_backup_name(backup_name: str | None, target_backup: Path):
        if backup_name:
            return backup_name
        else:
            return target_backup.name

    def set_config(self) -> BackupConfig:
        config = self._get_config()
        backup = config["backup"]
        retention = config["retention"]
        archive = config["archive"]
        config_filter = config["filter"]
        encryption = config['encryption']

        def _validate_path(key: str, path) -> Path:
            if not path.strip():
                raise ConfigurationError(f"{key} path is not set, make sure the target path is configured in your config")

            path = Path(path)
            if not path.exists():
                raise BackuperError(f"{key} path not found: {path}")

            return path

        target_backup = backup.get('target', '')
        target_backup = _validate_path('target', target_backup)

        destination_backup = backup.get('destination', '')
        destination_backup = _validate_path("destination", destination_backup)

        archive_backup = archive.get('path', '')
        archive_enabled = archive.get("enabled", False)
        if archive_enabled:
            archive_backup = _validate_path("Archive", archive_backup)

        encryption_enabled =  encryption.get('enabled', False)
        key_path = encryption.get('key_path', '')
        if encryption_enabled:
            key_path = _validate_path("Master Key", key_path)

        backup_name = self._set_backup_name(backup.get("backup_name", None), target_backup)

        return BackupConfig(
            target=target_backup,
            destination=destination_backup,
            backup_name=backup_name,
            include=config_filter.get("include", None),
            exclude=config_filter.get("exclude", None),
            keep_last=retention.get("keep_last", None),
            compression=backup.get("compression", None),
            archive_enable=archive_enabled,
            archive_path=archive_backup,
            encryption_enabled=encryption_enabled,
            key_path=key_path,
            link_mode=backup["link_mode"],
        )