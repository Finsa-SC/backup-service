from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class SystemdRequest:
    job: list[str]
    destination: Path
