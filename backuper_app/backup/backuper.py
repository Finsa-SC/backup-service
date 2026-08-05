import subprocess, datetime
from pathlib import Path
from backuper_app.utils import get_logger
from .filter_engine import FilterEngine
from .compression import resolve_compression_from_config
from .manifest import create_manifest_data

logger = get_logger(__name__)

class Backuper:
    def __init__(
            self,
            target_path: Path,
            destination_path: Path,
            parent_path: Path,
            include: list[str] | None,
            exclude: list[str] | None,
            backup_name=None,
            compression_type: str = "zstd",
            link_mode: str = "follow"
    ):
        self.target_path = target_path
        self.destination_path = destination_path
        self.parent_path = parent_path
        self.backup_name = backup_name
        self.compression_type = compression_type
        self.link_mode = link_mode
        self.exclude = exclude
        self.include = include

        if not self.target_path.is_relative_to(self.parent_path):
            raise ValueError(f"Mismatch target path and parent path: parent={self.parent_path} target={self.target_path}")

    @staticmethod
    def set_backup_name(backup_name: str) -> str:
        return f"{backup_name}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"

    def compress(self) -> Path:
        backup_name = self.set_backup_name(self.backup_name)

        compression = resolve_compression_from_config(self.compression_type)

        backup_path = self.destination_path / f"{backup_name}.tar.{compression.suffix}"

        str_command = [
            "tar",
            compression.compress_flag,
            "-cf",
            str(backup_path),
            "-C",
            str(self.parent_path),
        ]

        filter_engine = FilterEngine(
            target_path=self.target_path,
            include=self.include,
            exclude=self.exclude,
            link_mode=self.link_mode,
        )
        str_command.extend(filter_engine.do_filtering())

        #Add manifest file
        temp_dir_path = create_manifest_data(
            backup_name=backup_name,
            target_path=self.target_path,
            include=self.include if self.include else [],
            exclude=self.exclude if self.exclude else [],
        )

        manifest_relative_path = Path(temp_dir_path / ".manifest").relative_to(temp_dir_path)
        manifest_command = [
            "-C",
            str(temp_dir_path),
            str(manifest_relative_path),
        ]
        str_command.extend(manifest_command)

        result = subprocess.run(
            str_command,
            capture_output=True,
            text=True,
        )

        #Remove temporary manifest
        import shutil
        shutil.rmtree(temp_dir_path)

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
