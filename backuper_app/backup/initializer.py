from pathlib import Path

DEFAULT_CONFIG_PATH: Path = Path("/etc/backuper")

class Initializer:
    def __init__(self, request):
        self.config_path = request.config
        self.target = request.target
        self.destination = request.destination
        self.retention = request.retention
        self.compression = request.compression
        self.link_mode = request.link_mode
        self.archive_path = request.archive_path
        self.key_path = request.key_path

        # Remote
        self.remote_host = request.remote_host
        self.remote_user = request.remote_user
        self.remote_port = request.remote_port
        self.remote_identity_file = request.remote_identity_file
        self.remote_path = request.remote_path
        self.remote_alias = request.remote_alias

        self.remote_enabled = False

    def _remote_is_enabled(self) -> bool:
        if self.remote_alias and not self.remote_alias.strip() and self.remote_path and self.remote_path.strip():
            return True

        if not self.remote_host or not self.remote_host.strip():
            return False
        if not self.remote_user or not self.remote_user.strip():
            return False
        if not self.remote_port or not isinstance(self.remote_port, int):
            return False
        if not self.remote_identity_file or not self.remote_identity_file.strip():
            return False
        if not self.remote_path or not self.remote_path.strip():
            return False

        return True

    def _resolve_default_name(self) -> Path:
        if not self.config_path:
            if not Path(DEFAULT_CONFIG_PATH / "config.toml").exists():
                return DEFAULT_CONFIG_PATH / "config.toml"

            file_exists = sorted(
                DEFAULT_CONFIG_PATH.rglob(f"config-*.toml"),
                key=lambda path: int(path.stem.removeprefix("config-"))
            )

            increment = 2
            for i, file in enumerate(file_exists, start=increment):
                if file.name != f"config-{i}.toml":
                    increment = i
                    break
                else:
                    increment += 1
            return DEFAULT_CONFIG_PATH / f"config-{increment}.toml"

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
        return \
f"""[backup]
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
    "**/*.key",
]

[retention]
{self._optional_key("keep_last", hint=7, value=self.retention)}

[archive]
enabled = {'true' if self.archive_path else 'false'}
{self._optional_key("path", hint='', value=self.archive_path)}

[encryption]
enabled = {'true' if self.key_path else 'false'}
{self._optional_key("key_path", hint='', value=self.key_path)}

[remote]
enabled = {'true' if self._remote_is_enabled() else 'false'}
{self._optional_key("host", hint='', value=self.remote_host)}
{self._optional_key("user", hint='', value=self.remote_user)}
{self._optional_key("port", hint='22', value=self.remote_port)}
{self._optional_key("identity_file", hint='', value=self.remote_identity_file)}
{self._optional_key("remote_path", hint='', value=self.remote_path)}
{self._optional_key("alias", hint='', value=self.remote_alias)}
"""

    def make_init(self) -> Path:
        config_file = self._resolve_default_name()
        with config_file.open('w+') as file:
            file.write(self._set_init())

        return config_file