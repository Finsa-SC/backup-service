import subprocess, datetime
from pathlib import Path
from backuper_app.utils import get_logger, not_enough_space, analyze_estimate_size, get_space_info, format_size
from backuper_app.exception import NotEnoughDiskSpaceError, BackuperError
from backuper_app.backup.analyzer import Analyzer
from .filter_engine import FilterEngine
from .compression import resolve_compression_from_config
from .manifest import create_manifest_data

logger = get_logger(__name__)

class Backuper:
    def __init__(
            self,
            backup_plan
    ):
        self.backup_plan        = backup_plan
        self.target_path        = backup_plan.target_path
        self.destination_path   = backup_plan.destination_path
        self.parent_path        = backup_plan.parent_path
        self.backup_name        = backup_plan.backup_name
        self.compression_type   = backup_plan.compression_type

        self.exclude            = backup_plan.exclude
        self.include            = backup_plan.include

        self.dry_run            = backup_plan.dry_run
        self.link_mode          = backup_plan.link_mode

        self.retention          = backup_plan.retention
        self.archive_enabled    = backup_plan.archive_enabled
        self.archive_path       = backup_plan.archive_path

        self.encryption_enabled = backup_plan.encryption_enabled

        self.remote_enabled     = backup_plan.remote_enabled
        self.remote_path        = backup_plan.remote_path

        if not self.target_path.is_relative_to(self.parent_path):
            raise BackuperError(f"Mismatch target path and parent path: parent={self.parent_path} target={self.target_path}")

    @staticmethod
    def set_backup_name(backup_name: str) -> str:
        return f"{backup_name}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"

    def get_relative_path_list(self, path_list: list[Path]) -> list[Path]:
        return [path.relative_to(self.parent_path) for path in path_list]

    def compress(
            self,
            compression,
            backup_path: Path,
            backup_list: list[Path],
            temp_dir_path: Path,
            manifest_relative_path: Path,
    ) -> Path:
        str_command = [
            "tar",
            compression.compress_flag,
            "-cf",
            str(backup_path),
            "-C",
            str(self.parent_path),
        ]

        relative_backup = self.get_relative_path_list(backup_list)
        str_command.extend(relative_backup)

        # Insert manifest into compression command
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

        if result.returncode != 0:
            backup_path.unlink(missing_ok=True)
            raise ChildProcessError(result.stderr)
        else:
            return backup_path

    def _validate_backup_path(self):
        if not self.target_path.exists():
            raise BackuperError(f"Target path not found for {self.target_path}")

        if not self.destination_path.exists():
            raise BackuperError(f"Destination path not found for {self.destination_path}")

    def do_backup(self) -> Path:
        self._validate_backup_path()

        filter_engine = FilterEngine(
            target_path=self.target_path,
            include=self.include,
            exclude=self.exclude,
            link_mode=self.link_mode,
        )
        backup_list, backup_total = filter_engine.do_filtering()

        if self.dry_run:
            analyzer = Analyzer(
                backup_list,
                backup_total,
                self.backup_plan
            )
            analyzer.analyze_statistic()
            exit(0)

        # Do normal backup if --dry-run off
        elif backup_list:
            required_space = analyze_estimate_size(files=backup_list)
            space_available = get_space_info(self.target_path)['space_available']

            if not_enough_space(required=required_space, space_available=space_available):
                raise NotEnoughDiskSpaceError(f"""
                Not enough disk space
                
                Required : {format_size(required_space)}
                Available: {format_size(space_available)}
                Destination: {self.destination_path}
                """)

            backup_name = self.set_backup_name(self.backup_name)

            compression = resolve_compression_from_config(self.compression_type)
            backup_path = self.destination_path / f"{backup_name}.tar.{compression.suffix}"

            ### Add manifest file
            temp_dir_path = create_manifest_data(
                backup_name=backup_name,
                target_path=self.target_path,
                include=self.include if self.include else [],
                exclude=self.exclude if self.exclude else [],
                compression=self.compression_type,
                link_mode=self.link_mode,
            )

            # resolve manifest relative path to store into compression
            # because if you don't do that, manifest path will save as absolute path
            manifest_relative_path = Path(temp_dir_path / ".manifest").relative_to(temp_dir_path)

            ###Compress backup
            backup_path = self.compress(
                compression,
                backup_path=backup_path,
                backup_list=backup_list,
                temp_dir_path=temp_dir_path,
                manifest_relative_path=manifest_relative_path,
            )

            # Remove temporary manifest
            import shutil
            shutil.rmtree(temp_dir_path)
        else:
            # Raise exception if no file match from filter engine, only active when use include config
            from backuper_app.exception import FilterEmptyError
            raise FilterEmptyError(f"No files matched the configured include patterns: {self.include}")

        logger.debug(f"Backup for {self.target_path.name} success with no error found.")

        return backup_path