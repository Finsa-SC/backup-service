from pathlib import Path
from backuper_app.infrastructure import get_logger

logger = get_logger(__name__)

class FilterEngine:
    def __init__(self, target_path: Path, include: list[str] | None, exclude: list[str] | None, link_mode: str):
        self.target_path = target_path
        self.include = include
        self.exclude = exclude
        self.link_mode = link_mode
        self.file_list = []

    def resolve_glob_path(self, glob_pattern: list[str]) -> set[Path]:
        file_match = set()
        for glob in glob_pattern:
            for file in self.target_path.glob(glob):
                file_match.add(file)
        return file_match

    def get_link_file(self) -> set[Path]:
        link_file = set()
        for file in self.target_path.rglob("*"):
            if file.is_symlink():
                link_file.add(file)
        return link_file

    #Return final list of path to domain and exception count
    def do_filtering(self) -> tuple[list[Path], int]:
        #Get base file
        if self.target_path.is_file():
            self.file_list.extend([self.target_path])
        elif self.include:
            self.file_list.extend(list(self.resolve_glob_path(self.include)))
        else:
            self.file_list.extend(self.target_path.rglob("*"))

        filtered_count = len(self.file_list)
        logger.debug(f"Full file: {self.file_list}")

        #Filter exclude
        if self.exclude:
            # Get exclude file list then
            for file in self.resolve_glob_path(self.exclude):
                # Remove file from list if file in exclude glob result
                if file in self.file_list:
                    self.file_list.remove(file)
                    logger.debug(f"Removed: {file}")

        #filter link file when link mode == ignore
        if self.link_mode == "ignore":
            for file in self.get_link_file():
                if file in self.file_list:
                    self.file_list.remove(file)
                    logger.debug(f"Removed: {file}")

        print(self.file_list)
        return self.file_list, (filtered_count - len(self.file_list))

if __name__ == "__main__":
    engine = FilterEngine(Path("/devops_learn"), include=None, exclude=None, link_mode="ignore")
    for p in engine.do_filtering():
        logger.debug(p)