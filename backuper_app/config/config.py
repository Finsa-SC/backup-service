import tomllib
from pathlib import Path
from dataclasses import dataclass
from backuper_app.utils import get_logger
from backuper_app.exception import BackuperError, ConfigurationError

logger = get_logger(__name__)

PERMISSION_MODE = [
    "0", "1", "2", "3",
    "4", "5", "6", "7",
]

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

    @staticmethod
    def _get_validate_file_mode(mode) -> int|None:
        if not mode:
            return None

        if not isinstance(mode, str):
            raise ConfigurationError(f"Invalid file mode type: got {type(mode)}, expected 'str'")

        len_mode = len(mode)
        if not len_mode == 3:
            raise ConfigurationError(f"Invalid len of file mode: got {len_mode} len, expected 3 len")

        for perm in mode:
            if perm not in  PERMISSION_MODE:
                raise ConfigurationError("Invalid permission got")

        try:
            return int(mode, 8)
        except Exception:
            raise ConfigurationError(f"Invalid permission, got {mode}. Expected like 640")

    def set_config(self) -> BackupConfig:
        config = self._get_config()
        backup = config["backup"]
        retention = config["retention"]
        archive = config["archive"]
        config_filter = config["filter"]
        encryption = config['encryption']
        remote = config['remote']

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

        encryption_enabled = encryption.get('enabled', False)
        key_path = encryption.get('key_path', '')
        if encryption_enabled:
            key_path = _validate_path("Master Key", key_path)

        backup_name = self._set_backup_name(backup.get("backup_name", None), target_backup)

        return BackupConfig(
            target=target_backup,
            destination=destination_backup,
            backup_name=backup_name,
            compression=backup.get("compression", None),
            file_mode=self._get_validate_file_mode(backup.get('file_mode', None)),

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