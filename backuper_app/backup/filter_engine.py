from pathlib import Path
from backuper_app.utils import get_logger

logger = get_logger(__name__)

class FilterEngine:
    def __init__(self, target_path: Path, include: list[str] | None, exclude: list[str] | None, link_mode: str):
        self.target_path = target_path
        self.include = include
        self.exclude = exclude
        self.link_mode = link_mode

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

    def do_filtering(self) -> list[str]:
        filtered = []

        #Get base file
        if self.include:
            filtered.extend(list(self.resolve_glob_path(self.include)))
        else:
            filtered.extend(self.target_path.rglob("*"))

        logger.debug(f"Full file: {filtered}")

        #Filter exclude
        if self.exclude:
            for file in self.resolve_glob_path(self.exclude):
                if file in filtered:
                    filtered.remove(file)
                    logger.debug(f"Removed: {file}")

        #filter link file when link mode == ignore
        if self.link_mode == "ignore":
            for file in self.get_link_file():
                if file in filtered:
                    filtered.remove(file)
                    logger.debug(f"Removed: {file}")

        return filtered

if __name__ == "__main__":
    engine = FilterEngine(Path("/devops_learn"), include=None, exclude=None, link_mode="ignore")
    for p in engine.do_filtering():
        logger.debug(p)