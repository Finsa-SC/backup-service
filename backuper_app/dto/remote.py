from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class RemoteConfig:
    enabled: bool
    host: str | None
    user: str | None
    port: int
    identity_file: Path | None
    remote_path: str | None
    alias: str | None