import tomllib
from pathlib import Path
from dataclasses import dataclass
from enum import Enum, auto
from backuper_app.utils import get_logger

logger = get_logger(__name__)

@dataclass
class BackupConfig:
    target: Path
    destination: Path
    backup_name: str | None
    keep_last: int
    compression: str
    archive_enable: bool
    archive_path: Path
    service_mode: ServiceMode

class ServiceMode(Enum):
    Backup = auto()
    Restore = auto()

class Config:
    def __init__(self, config_path: Path, service_mode: ServiceMode):
        self._config_path: Path = config_path
        self.service_mode = service_mode

    def _get_config(self):
        logger.debug(f"Reading config from {self._config_path}")
        with self._config_path.open('rb') as file:
            return tomllib.load(file)

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

        target_backup = Path(backup["target"])
        backup_name = self._set_backup_name(backup.get("backup_name", None), target_backup)

        return BackupConfig(
            target=target_backup,
            destination=Path(backup["destination"]),
            backup_name=backup_name,
            keep_last=retention.get("keep_last", None),
            compression=backup.get("compression", None),
            archive_enable=archive.get("enabled", False),
            archive_path=Path(archive.get("path", None)),
            service_mode=self.service_mode,
        )