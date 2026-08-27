from backuper_app.exception import ConfigurationError

def validate_ssh_config(
        hostname: str | None,
        username: str | None,
        port: int,
        remote_path: str
):
    if not hostname or not hostname.strip():
        raise ConfigurationError("Hostname unfilled")

    if not username or not username.strip():
        raise ConfigurationError("Username is not set")

    if not isinstance(port, int):
        raise ConfigurationError("Port is not set")
    elif not (1 <= port <= 65535):
        raise ConfigurationError("Invalid port configuration")

    if not remote_path.strip():
        raise ConfigurationError("Remote path is not set")
