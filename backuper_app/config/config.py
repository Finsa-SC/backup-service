import tomllib
from pathlib import Path
from dataclasses import dataclass
from backuper_app.utils import get_logger
from backuper_app.exception import BackuperError, ConfigurationError
from backuper_app.validation import get_validate_file_mode, get_validate_config_path

logger = get_logger(__name__)

@dataclass
class BackupConfig:
    target          : Path
    destination     : Path
    backup_name     : str
    compression     : str
    file_mode       : int|None

    include         : list[str] | None
    exclude         : list[str] | None

    keep_last       : int
    archive_enabled : bool
    archive_path    : Path

    encryption_enabled: bool
    key_path        : Path

    remote_enabled  : bool
    remote_host     : str|None
    remote_user     : str|None
    remote_backup   : str # Use str because paramiko sftp put needed str for destination remote path
    remote_path     : Path
    identity_file   : str|None
    alias           : str|None
    remote_port     : int = 22

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
        except FileNotFoundError:
            raise BackuperError(f"{self._config_path} not found")
        except PermissionError:
            raise BackuperError(f"You don't have permission to read {self._config_path}")

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
        remote = config['remote']


        target_backup = backup.get('target', '')
        target_backup = get_validate_config_path('target', target_backup)

        destination_backup = backup.get('destination', '')
        destination_backup = get_validate_config_path("destination", destination_backup)

        archive_backup = archive.get('path', '')
        archive_enabled = archive.get("enabled", False)
        if archive_enabled:
            archive_backup = get_validate_config_path("Archive", archive_backup)

        encryption_enabled = encryption.get('enabled', False)
        key_path = encryption.get('key_path', '')
        if encryption_enabled:
            key_path = get_validate_config_path("Master Key", key_path)

        backup_name = self._set_backup_name(backup.get("backup_name", None), target_backup)

        return BackupConfig(
            target=target_backup,
            destination=destination_backup,
            backup_name=backup_name,
            compression=backup.get("compression", None),
            file_mode=get_validate_file_mode(backup.get('file_mode', None)),

            include=config_filter.get("include", None),
            exclude=config_filter.get("exclude", None),

            keep_last=retention.get("keep_last", None),
            archive_enabled=archive_enabled,
            archive_path=archive_backup,

            encryption_enabled=encryption_enabled,
            key_path=key_path,

            # Remote
            remote_enabled=remote.get("enabled", False),
            remote_host=remote.get("host", None),
            remote_user=remote.get("user", None),
            identity_file=remote.get("identity_file", None),
            remote_backup=remote.get("remote_path", None),
            remote_port=remote.get("remote_port", 22),
            remote_path=remote.get("remote_path"),
            alias=remote.get("alias"),

            link_mode=backup["link_mode"],
        )