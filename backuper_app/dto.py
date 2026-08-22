from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class BackupPlan:
    target_path         : Path
    destination_path    : Path
    parent_path         : Path
    backup_name         : str
    compression_type    : str
    link_mode           : str
    archive_enabled     : bool
    archive_path        : Path | None
    include             : list[str] | None
    exclude             : list[str] | None
    retention           : int | None
    encryption_enabled  : bool
    remote_path         : Path | None
    remote_enabled      : bool = False
    dry_run             : bool = False

@dataclass(frozen=True)
class RestoreRequest:
    file_path       : Path
    date            : str
    destination     : Path
    archive_path    : Path
    key_path        : Path|None

@dataclass(frozen=True)
class VerifyRequest:
    file_path       : Path
    date            : str
    archive_path    : Path
    key_path        : Path|None

@dataclass(frozen=True)
class InitRequest:
    config_path             : str
    target_path             : Path
    destination_path        : Path
    retention               : int
    compression             : str
    link_mode               : str
    archive_path            : Path | None
    key_path                : Path | None
    remote_host             : str|None
    remote_user             : str|None
    remote_port             : int
    remote_identity_file    : str|None
    remote_path             : str|None
    remote_alias            : str|None