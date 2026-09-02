from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class SystemdRequest:
    jobs: list[str]
    destination: Path
