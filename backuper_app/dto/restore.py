from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class RestoreRequest:
    file_path       : Path
    date            : str
    destination     : Path
    archive_path    : Path
    key_path        : Path|None
