from paramiko import SSHClient, SSHConfig, SFTPClient, RejectPolicy, SSHException
from pathlib import Path

from backuper_app.dto import RemoteConfig
from backuper_app.exception import BackuperError
from backuper_app.validation import validate_ssh_config

CONFIG_PATH = Path("~/.ssh/config").expanduser()
KNOWN_HOST_PATH = Path("~/.ssh/known_hosts").expanduser()

class RemoteBackup:
    def __init__(
            self,
            backup_list: list[Path],
            remote_config: RemoteConfig
        ):
        self.hostname = remote_config.host
        self.username = remote_config.user
        self.port = remote_config.port
        self.alias = remote_config.alias
        self.remote_path = remote_config.remote_path
        self.backup_list = backup_list

        identity_file = None
        if remote_config.identity_file:
            identity_file = Path(remote_config.identity_file).expanduser()
            identity_file = str(identity_file)
        self.identity_file = identity_file

    @staticmethod
    def load_ssh_config(alias):
        config = SSHConfig.from_path(CONFIG_PATH)
        host_config = config.lookup(alias)
        return host_config

    @staticmethod
    def create_sftp_connection(
            hostname: str,
            username: str,
            port: int,
            identity_file: list[str] | None,
    ) -> tuple[SSHClient, SFTPClient]:

        ssh = SSHClient()

        # Load known host from disk and reject host not registered in know host
        ssh.load_host_keys(KNOWN_HOST_PATH)
        ssh.set_missing_host_key_policy(
            RejectPolicy()
        )

        ssh.connect(
            hostname,
            username=username,
            port=port,
            key_filename=identity_file[0] if identity_file else None,
        )
        return ssh, ssh.open_sftp()

    def is_success_send_backup(self, sftp: SFTPClient) -> bool:
        try:
            for path in self.backup_list:
                remote_backup = f"{self.remote_path}/{path.name}"
                sftp.stat(remote_backup)
        except FileNotFoundError:
            return False
        else:
            return True

    @staticmethod
    def transfer_backup(sftp: SFTPClient, local_backup: list[Path], remote_path: str) -> None:
        for backup in local_backup:
            remote_file = f"{remote_path.rstrip('/')}/{backup.name}"
            sftp.put(backup, remote_file)

    def do_remote(self):
        if self.alias and self.alias.strip():
            host_config = self.load_ssh_config(self.alias)
            self.hostname = host_config.get("hostname", None)
            self.username = host_config.get("user", None)
            self.port = host_config.get("port", 22)
            self.identity_file = host_config.get("identityfile", None)
        else:
            self.identity_file = [self.identity_file] if self.identity_file and self.identity_file.strip() else None

        validate_ssh_config(
            self.hostname,
            username=self.username,
            port=self.port,
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
            attr = sftp.stat(self.remote_path)

            self.transfer_backup(
                sftp,
                local_backup=self.backup_list,
                remote_path=self.remote_path
            )

            if not self.is_success_send_backup(sftp):
                raise BackuperError("File domain to remote failed")

        except FileNotFoundError:
            raise BackuperError(f"Remote path does not exist: {self.remote_path}")
        except SSHException as e:
            raise BackuperError(
                "Unable to upload domain to remote path",
                f"'{self.remote_path}'"
            ) from e

        finally:
            sftp.close()
            ssh.close()