from dataclasses import dataclass
from pathlib import Path

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