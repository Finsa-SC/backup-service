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

    @staticmethod
    def _optional_key(key: str | None, hint: str, value) -> str:
        if value is not None:
            return f"{key} = {value}"
        return f"# {key} = {hint if hint.strip() else '""'}"

    def _set_init(self):
        return f"""
[backup]
{self._optional_key("target", hint='', value=self.target)}
{self._optional_key("destination", hint='', value=self.destination)}
#backup_name = ""
compression = "{self.compression}"

link_mode = "{self.link_mode}" # follow/preserve/ignore

[filter]
include = []
exclude = [
    ".venv",
    "dist/",
    "**.__pycache__/",
    "**/*.pyc",
]

[retention]
{self._optional_key("keep_last", hint="7", value=self.retention)}

[archive]
#enabled = false
#path = ""
"""

    def make_init(self) -> Path:
        with self.config_path.open('w+') as file:
            file.write(self._set_init())

        if self.config_path.is_file(follow_symlinks=True):
            return self.config_path
        else:
            raise FileNotFoundError(f"File {self.config_path} not found")