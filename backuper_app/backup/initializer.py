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
    def _toml_value(value) -> str:
        if isinstance(value, str|Path):
            return f'"{value}"'
        if isinstance(value, bool):
            return str(value)
        if isinstance(value, int):
            return str(value)
        return '""'

    def _optional_key(
            self,
            key: str | None,
            hint,
            value,
            required: bool = False
    ) -> str:
        if value is None:
            value = "" if required else hint
            prefix = "" if required else "# "
        else:
            prefix = ""

        return f"{prefix}{key} = {self._toml_value(value)}"

    def _set_init(self):
        return f"""
[backup]
{self._optional_key("target",      hint='',         value=self.target,         required=True)}
{self._optional_key("destination", hint='',         value=self.destination,    required=True)}
{self._optional_key("backup_name", hint='',         value="")}
{self._optional_key("compression", hint="zstd",     value=self.compression)}
{self._optional_key("link_mode",   hint="preserve", value=self.link_mode)} # follow/preserve/ignore

[filter]
include = []
exclude = [
    ".venv",
    "dist/",
    "**.__pycache__/",
    "**/*.pyc",
]

[retention]
{self._optional_key("keep_last", hint=7, value=self.retention)}

[archive]
enabled = false
# path = ""
"""

    def make_init(self) -> Path:
        with self.config_path.open('w+') as file:
            file.write(self._set_init())

        if self.config_path.is_file(follow_symlinks=True):
            return self.config_path
        else:
            raise FileNotFoundError(f"File {self.config_path} not found")