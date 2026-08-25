from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class VerifyRequest:
    file_path       : Path
    date            : str
    archive_path    : Path
    key_path        : Path|None
