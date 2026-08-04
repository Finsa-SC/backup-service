import subprocess, datetime
from pathlib import Path
from backuper_app.utils import get_logger
from .compression import resolve_compression_from_config

logger = get_logger(__name__)

class Backuper:
    def __init__(self, target_path: Path, destination_path: Path, parent_path: Path, backup_name=None, compression_type: str = "zstd", link_mode: str = "follow"):
        self.target_path = target_path
        self.destination_path = destination_path
        self.parent_path = parent_path
        self.backup_name = backup_name
        self.compression_type = compression_type
        self.link_mode = link_mode

        if not self.target_path.is_relative_to(self.parent_path):
            raise ValueError(f"Mismatch target path and parent path: parent={self.parent_path} target={self.target_path}")

    @staticmethod
    def set_backup_name(backup_name: str) -> str:
        return f"{backup_name}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"

    def run_link_mode(self, command: list[str]) -> list[str]:
        print(self.link_mode)
        match self.link_mode:
            case "follow":
                command.append("--dereference")
                return command
            case "preserve":
                return command
            case "ignore":
                for path in self.target_path.iterdir():
                    if path.is_symlink():
                        relative_path = path.relative_to(self.parent_path)
                        command.insert(4, f"--exclude={relative_path}")
                return command
            case _:
                raise ValueError(f"Invalid link mode: {self.link_mode}, expected=follow/preserve/ignore")

    def compress(self) -> Path:
        backup_name = self.set_backup_name(self.backup_name)

        compression = resolve_compression_from_config(self.compression_type)

        backup_path = self.destination_path / f"{backup_name}.tar.{compression.suffix}"

        str_command = [
            "tar",
            compression.compress_flag,
            "-C",
            str(self.parent_path),
            "-cf",
            str(backup_path),
            f"{self.target_path.name}"
        ]

        command = self.run_link_mode(str_command)
        print(f"command: {command}")
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            backup_path.unlink(missing_ok=True)
            raise ChildProcessError(result.stderr)
        else:
            return backup_path

    def do_backup(self) -> Path:
        #Validate path
        logger.debug(f"Validate path for {self.target_path}")
        if not self.target_path.exists():
            raise FileNotFoundError(f"Target path not found for {self.target_path}")

        logger.debug(f"Validate path for {self.destination_path}")
        if not self.destination_path.exists():
            raise FileNotFoundError(f"Destination path not found for {self.destination_path}")

        backup_path = self.compress()

        logger.debug(f"Backup for {self.target_path.name} success with no error found.")

        return backup_path

if __name__ == "__main__":
    try:
        backuper = Backuper(target_path="/", destination_path="/home/silence-suzuka/backup_test", backup_name="My_Backup")
        backuper.do_backup()
    except Exception as e:
        logger.error(e)
