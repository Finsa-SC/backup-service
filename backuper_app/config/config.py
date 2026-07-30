import tomllib
from pathlib import Path
from dataclasses import dataclass
from backuper_app.utils import get_logger

logger = get_logger(__name__)

@dataclass
class BackupConfig:
    target: Path
    destination: Path
    backup_name: str | None

class Config:
    def __init__(self, config_path: Path):
        self._config_path: Path = config_path

    def _get_config(self):
        logger.debug(f"Reading config from {self._config_path}")
        with self._config_path.open('rb') as file:
            return tomllib.load(file)

    def set_config(self) -> BackupConfig:
        config = self._get_config()
        backup = config["backup"]

        return BackupConfig(
            target=Path(backup["target"]),
            destination=Path(backup["destination"]),
            backup_name=backup.get("backup_name", None),
        )