from paramiko import SSHClient, SSHConfig, SFTPClient
from pathlib import Path
from backuper_app.exception import ConfigurationError

class RemoteBackup:
    def __init__(
            self,
            remote_path:str,
            backup_list: list[Path],
            hostname:str|None=None,
            username:str|None=None,
            port:int|None=None,
            identity_file:str|None=None,
            alias:str|None=None
        ):
        self.hostname = hostname
        self.username = username
        self.port = port
        self.identity_file = identity_file
        self.alias = alias
        self.remote_path = remote_path
        self.backup_list = backup_list

    @staticmethod
    def validate_ssh_config(
        hostname: str|None,
        username: str|None,
        port: int|None,
        identity_file: str | None,
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

    @staticmethod
    def load_ssh_config(alias):
        config_path = Path("~/.ssh/config").expanduser()
        config = SSHConfig.from_path(config_path)
        host_config = config.lookup(alias)
        return host_config

    @staticmethod
    def create_sftp_connection(hostname: str, username: str, port: int, identity_file: str|None) -> tuple[SSHClient, SFTPClient]:
        ssh = SSHClient()
        ssh.connect(
            hostname,
            username=username,
            port=port,
            key_filename=identity_file,
        )
        return ssh, ssh.open_sftp()

    @staticmethod
    def transfer_backup(sftp: SFTPClient, local_backup: list[Path], remote_path: str) -> None:
        for backup in local_backup:
            sftp.put(backup, remote_path)

    def do_remote(self):
        if self.alias and self.alias.strip():
            host_config = self.load_ssh_config(self.alias)
            self.hostname = host_config.get("hostname", None)
            self.username = host_config.get("user", None)
            self.port = host_config.get("port", None)
            self.identity_file = host_config.get("identityfile", None)
        else:
            self.identity_file = self.identity_file if self.identity_file and self.identity_file.strip() else None

        self.validate_ssh_config(
            self.hostname,
            username=self.username,
            port=self.port,
            identity_file=self.identity_file,
            remote_path=self.remote_path
        )

        # Init sftp connection
        ssh, sftp = self.create_sftp_connection(
            self.hostname,
            username=self.username,
            port=self.port,
            identity_file=self.identity_file,
        )

        try:
            self.transfer_backup(sftp, local_backup=self.backup_list, remote_path=self.remote_path)
        finally:
            sftp.close()
            ssh.close()

if __name__ == "__main__":
    remote = RemoteBackup("agus", "ahmad", 22, "ambatukan/")
    remote.do_remote()