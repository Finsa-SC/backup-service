from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class BackupRequest:
    dry_run: bool = False

@dataclass(frozen=True)
class RestoreRequest:
    file_path: Path
    date: str
    destination: Path
    archive_path: Path
    key_path: Path

@dataclass(frozen=True)
class VerifyRequest:
    file_path: Path
    date: str
    archive_path: Path

@dataclass(frozen=True)
class InitRequest:
    config: str
    target: Path
    destination: Path
    retention: int
    compression: str
    link_mode: str
    archive_path: Path | None