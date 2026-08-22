from pathlib import Path
from backuper_app.utils import get_logger, format_size

logger = get_logger(__name__)

class Analyzer:
    def __init__(
            self,
            files: list[Path],
            backup_total: int,
            backup_plan,
    ):
        self.files              = files
        self.backup_total       = backup_total

        self.target             = backup_plan.target_path
        self.destination        = backup_plan.destination_path
        self.compression        = backup_plan.compression_type
        self.link_mode          = backup_plan.link_mode

        self.include            = backup_plan.include
        self.exclude            = backup_plan.exclude

        self.retention          = backup_plan.retention
        self.archive_enabled    = backup_plan.archive_enabled
        self.archive_path       = backup_plan.archive_path

        self.encryption_enabled = backup_plan.encryption_enabled

        self.remote_enabled     = backup_plan.remote_enabled
        self.remote_path        = backup_plan.remote_path

    def get_file_statistic(self) -> dict[str, int]:
        mapping = dict(file=0, directory=0, symlink=0, socket=0, unknown=0)
        for file in self.files:
            if file.is_file():
                mapping['file'] += 1
            elif file.is_dir():
                mapping['directory'] += 1
            elif file.is_symlink():
                mapping['symlink'] += 1
            elif file.is_socket():
                mapping['socket'] += 1
            else:
                mapping['unknown'] += 1

        return mapping

    def show_statistic(self, file_statistic: dict[str, int]) -> None:
        from backuper_app.utils import analyze_estimate_size, format_size

        logger.info("Starting dry run...")

        #Backup info
        logger.info(f"""
        Backup
        Target      : {self.target if self.target.exists() else '-'}
        Destination : {self.destination if self.destination.exists() else '-'}
        Compression : {self.compression}
        Link mode   : {self.link_mode}
        """)

        #Filter
        logger.info(f"""
        Filter
        Include     : {self.include}
        exclude     : {self.exclude}
        """)

        #File statistic
        matched_file = ["\n\tStatistics"]
        for type_file, value in file_statistic.items():
            matched_file.append(f"\t{type_file:<12}: {value}")
        matched_file.append(f"\t{'Filtered':<12}: {self.backup_total}")

        estimated_size = analyze_estimate_size(self.files)
        matched_file.append(f"\tEstimate size: {format_size(estimated_size)}")

        logger.info("\n".join(matched_file))

        #Action
        logger.info(f"""
        Action
        Manifest     : Yes
        Checksum     : Yes
        Encryption   : {self.encryption_enabled} 
        Archive      : {self.archive_enabled}
        Archive Path : {self.archive_path if self.archive_enabled and self.archive_path.is_dir() else "-"}
        Keep last    : {self.retention if self.retention else '-'}
        Remote       : {self.remote_enabled}
        Remote Path  : {self.remote_path if self.remote_path else "-"}
        """)

        logger.info("""
        Result
        Dry run completed successfully
        No filesystem changes were made
        """)

    def analyze_statistic(self):
        mapping = self.get_file_statistic()
        self.show_statistic(mapping)