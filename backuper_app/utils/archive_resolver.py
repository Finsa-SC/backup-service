from pathlib import Path
from datetime import datetime
from backuper_app.exception import InvalidArgumetError
from exception import BackuperError

DATE_FORMAT = "%Y-%m-%d"

def is_valid_date(date: str):
    try:
        datetime.strptime(date, DATE_FORMAT)
        return True
    except ValueError:
        return False

def get_archive_by_date(archive_path: Path, date: str) -> list[Path]:
    if not is_valid_date(date):
        raise InvalidArgumetError(f"Invalid date value: got {date}, expected format {DATE_FORMAT}")

    date = date.replace('-', '')
    match_date = list(
        archive_path.rglob(f"*_{date}_*")
    )
    match_date.sort(key=lambda path: path.name)

    return match_date

def get_archive_by_path(archive_path: Path):
    if archive_path.is_file(follow_symlinks=True):
        return archive_path
    else:
        raise BackuperError(f"{archive_path} is doesn't exist or not a file")

#Get list of path with name match
def get_archive_glob(destination: Path, backup_name: str) -> list[Path]:
    path_list = list(
        destination.glob(f"{backup_name}*")
    )

    path_list.sort(key=lambda backup: backup.name)
    return path_list

if __name__ == "__main__":
    print(get_archive_by_date(Path("/home/silence-suzuka/backup_archive"), "2026-07-31"))