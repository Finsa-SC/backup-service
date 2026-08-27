from dataclasses import dataclass
from pathlib import Path

from .remote import RemoteConfig

@dataclass(frozen=True)
class ValidateRequest:
    target_path     : Path
    destination_path: Path
    compression_type: str

    archive_enabled : bool
    archive_path    : Path|None

    encryption_enabled: bool
    key_path        : Path|None

    remote_config   : RemoteConfig