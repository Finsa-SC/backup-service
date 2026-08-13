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
        self.default_file = Path("/etc/backuper/")

    def _resolve_default_name(self) -> Path:
        if not self.config_path:
            file_exists = list(self.default_file.rglob(f"config*.toml"))
            file_exists = sorted(file_exists)
            file_increment = [file for file in file_exists if '-' in str(file)]

            if not Path(self.default_file / "config.toml").exists():
                return self.default_file / "config.toml"

            increment = 2
            for i, file in enumerate(file_increment, start=increment):
                if file.name != f"config-{i}.toml":
                    increment = i
                    break
                else:
                    increment += 1
            return self.default_file / f"config-{increment}.toml"

        return self.config_path

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
        config_file = self._resolve_default_name()
        with config_file.open('w+') as file:
            file.write(self._set_init())

        return config_file