from pathlib import Path

class Initializer:
    def __init__(
            self,
            config_path: Path,
            target: Path,
            destination: Path,
            retention: int|None,
            compression: str,
            link_mode: str,
    ):
        self.config_path = config_path
        self.target = target
        self.destination = destination
        self.retention = retention
        self.compression = compression
        self.link_mode = link_mode

    def _set_init(self):
        return f"""
[backup]
target = {self.target}
destination = {self.destination}
backup_name = \"\"
compression = {self.compression}

link_mode = {self.link_mode} #follow/preserve/ignore

[filter]
include = []
exclude = [
    ".venv",
    "dist/",
    "**.__pycache__/",
    "**/*.pyc",
]

[retention]
keep_last = 

[archive]
enabled = false
path =
"""

    def make_init(self):
        with self.config_path.open('w+') as file:
            file.write(self._set_init())