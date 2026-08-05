from pathlib import Path
from backuper_app.utils import get_logger

logger = get_logger(__name__)

class Analyzer:
    def __init__(
            self,
            target_path: Path,
            destination: Path,
            files: list[Path],
            compression_type: str,
            link_mode: str,
            archive_enabled: bool,
            include: list[str],
            exclude: list[str],
            retention: int | None,
    ):
        self.target = target_path
        self.destination = destination
        self.files = files
        self.compression = compression_type
        self.link_mode = link_mode
        self.archive_enabled = archive_enabled
        self.include = include
        self.exclude = exclude
        self.retention = retention

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

    def analyze_estimate_size(self) -> str:
        size: float = 0
        units = [
            "B",
            "KiB",
            "MiB",
            "GiB",
            "TiB",
        ]

        for file in self.files:
            if not file.is_dir():
                size += file.lstat().st_size

        byte = 1024
        unit_index = 0
        while size >= byte:
            size /= byte
            unit_index += 1

        return f"{size:.2f} {units[unit_index]}"

    def show_statistic(self, file_statistic: dict[str, int]) -> None:
        logger.info("Starting dry run...")

        #Backup info
        logger.info(f"""
        Backup
        Target      : {self.target}
        Destination : {self.destination}
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

        estimated_size = self.analyze_estimate_size()
        matched_file.append(f"\tEstimate size: {estimated_size}")

        logger.info("\n".join(matched_file))

        #Action
        logger.info(f"""
        Action
        Manifest    : Yes
        Checksum    : Yes
        Archive     : {self.archive_enabled}
        Keep last   : {self.retention}
        """)

        logger.info("Dry run completed successfully")
        logger.info("No filesystem changed were made")

    def analyze_statistic(self):
        mapping = self.get_file_statistic()
        self.show_statistic(mapping)