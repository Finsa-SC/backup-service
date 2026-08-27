from dataclasses import dataclass
from pathlib import Path

from .remote import RemoteConfig

@dataclass(frozen=True)
class BackupPlan:
    target_path         : Path
    destination_path    : Path
    parent_path         : Path
    backup_name         : str
    compression_type    : str

    link_mode           : str

    retention           : int | None
    archive_enabled     : bool
    archive_path        : Path | None

    include             : list[str] | None
    exclude             : list[str] | None

    encryption_enabled  : bool

    remote_config       : RemoteConfig | None
    dry_run             : bool = False